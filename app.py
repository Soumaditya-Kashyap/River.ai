import streamlit as st
import os
from dotenv import load_dotenv
from pdf_processor import MultiPDFProcessor
from summarizer import PDFSummarizer
from chat_interface import MultiPDFChatbot
from model import GeminiModel


load_dotenv()

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Multi-PDF Chatbot",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Multi-PDF Chatbot with Gemini")
    st.markdown("Upload multiple PDFs, get summaries, and ask questions about their content!")
    
    # Initialize components
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("Please set your GEMINI_API_KEY in the .env file")
            st.stop()
            
        model = GeminiModel(api_key)
        processor = MultiPDFProcessor()
        summarizer = PDFSummarizer(model)
        chatbot = MultiPDFChatbot(model)
        
    except Exception as e:
        st.error(f"Error initializing components: {str(e)}")
        st.stop()
    
    # Sidebar for file upload
    with st.sidebar:
        st.header(" Upload PDFs")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="You can upload multiple PDF files"
        )
        
        if uploaded_files:
            st.success(f"Uploaded {len(uploaded_files)} file(s)")
            
            
            if st.button("Process PDFs", type="primary"):
                with st.spinner("Processing PDFs..."):
                    
                    pdf_data = {}
                    for file in uploaded_files:
                        chunks = processor.process_pdf(file)
                        pdf_data[file.name] = chunks
                    
                    
                    st.session_state.pdf_data = pdf_data
                    st.session_state.processed_files = [f.name for f in uploaded_files]
                    
                   
                    chatbot.load_documents(pdf_data)
                    st.session_state.chatbot = chatbot
                    
                    st.success("PDFs processed successfully!")
    
    if 'pdf_data' in st.session_state:
    
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "selected_section" not in st.session_state:
            st.session_state.selected_section = "combined" if len(st.session_state.processed_files) > 1 else st.session_state.processed_files[0]
        
        # Generate all summaries first
        for filename in st.session_state.processed_files:
            summary_key = f"summary_{filename}"
            if summary_key not in st.session_state:
                with st.spinner(f"Generating summary for {filename}..."):
                    chunks = st.session_state.pdf_data[filename]
                    full_text = "\n\n".join([chunk['text'] for chunk in chunks])
                    st.session_state[summary_key] = summarizer.summarize_text(full_text[:8000], filename)
        
        # Single PDF - Simple layout
        if len(st.session_state.processed_files) == 1:
            filename = st.session_state.processed_files[0]
            
            # Display summary
            st.markdown(f"###  {filename}")
            st.write(st.session_state[f"summary_{filename}"])
            
            # Generate and show suggested questions
            if f"questions_{filename}" not in st.session_state:
                with st.spinner("Generating questions..."):
                    st.session_state[f"questions_{filename}"] = st.session_state.chatbot.generate_suggested_questions(st.session_state[f"summary_{filename}"])
            
            st.markdown("---")
            st.markdown("** Quick Questions:**")
            
       
            cols = st.columns(2)
            questions = st.session_state[f"questions_{filename}"]
            for i, question in enumerate(questions[:6]):
                if question.strip():
                    with cols[i % 2]:
                        if st.button(f"❓ {question}", key=f"single_q_{i}", use_container_width=True):
                            st.session_state.messages.append({"role": "user", "content": question})
                            with st.spinner("Getting answer..."):
                                response = st.session_state.chatbot.chat(question)
                                st.session_state.messages.append({"role": "assistant", "content": response})
                            st.rerun()
        
        # Multiple PDFs - Card-based horizontal layout
        else:
            combined_summary_key = "combined_summary" 
            if combined_summary_key not in st.session_state:
                with st.spinner("Creating combined overview..."):
                    individual_summaries = {f: st.session_state[f"summary_{f}"] for f in st.session_state.processed_files}
                    st.session_state[combined_summary_key] = summarizer.create_combined_summary(individual_summaries)
            
        
            st.markdown("### 📚 Select a Document Section")
            
            # Create card options
            cards = [{"key": "combined", "title": "🔗 Combined Overview", "desc": "All documents together"}]
            for filename in st.session_state.processed_files:
                short_name = filename[:15] + "..." if len(filename) > 15 else filename
                cards.append({"key": filename, "title": f"📄 {short_name}", "desc": "Individual summary"})
            
         
            cols = st.columns(len(cards))
            for i, card in enumerate(cards):
                with cols[i]:
                    is_selected = st.session_state.selected_section == card["key"]
                    if st.button(
                        f"{card['title']}\n{card['desc']}", 
                        key=f"card_{card['key']}", 
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.selected_section = card["key"]
                        st.rerun()
            
            st.markdown("---")
            
       
            selected = st.session_state.selected_section
            
            if selected == "combined":
                st.markdown("### 🔗 Combined Overview")
                st.write(st.session_state[combined_summary_key])
                
                if f"questions_combined" not in st.session_state:
                    with st.spinner("Generating questions..."):
                        combined_text = "\n\n".join([st.session_state[f"summary_{f}"] for f in st.session_state.processed_files])
                        st.session_state[f"questions_combined"] = st.session_state.chatbot.generate_suggested_questions(combined_text)
                
                questions_key = "questions_combined"
            else:
                st.markdown(f"### 📄 {selected}")
                st.write(st.session_state[f"summary_{selected}"])
                
                if f"questions_{selected}" not in st.session_state:
                    with st.spinner("Generating questions..."):
                        st.session_state[f"questions_{selected}"] = st.session_state.chatbot.generate_suggested_questions(st.session_state[f"summary_{selected}"])
                
                questions_key = f"questions_{selected}"
            
            st.markdown("---")
            st.markdown("**💡 Quick Questions:**")
            
            questions = st.session_state[questions_key]
            cols = st.columns(2)
            for i, question in enumerate(questions[:6]):
                if question.strip():
                    with cols[i % 2]:
                        if st.button(f"❓ {question}", key=f"q_{selected}_{i}", use_container_width=True):
                            context = f"[About {selected}] " if selected != "combined" else ""
                            st.session_state.messages.append({"role": "user", "content": f"{context}{question}"})
                            with st.spinner("Getting answer..."):
                                response = st.session_state.chatbot.chat(f"{context}{question}")
                                st.session_state.messages.append({"role": "assistant", "content": response})
                            st.rerun()
        
        st.markdown("---")
        st.markdown("### 💬 Chat")
        
     
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask a question about your documents"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot.chat(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
        
     
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    else:
        
        st.info("👈 Please upload PDF files using the sidebar to get started!")
        
        # Instructions
        st.markdown("""
        ### How to use this Multi-PDF Chatbot:
        
        1. **Upload PDFs**: Use the sidebar to upload one or more PDF files
        2. **Process**: Click the "Process PDFs" button to analyze your documents
        3. **Select Section**: Choose from horizontal cards (Combined or Individual documents)
        4. **Try Suggested Questions**: Click on suggested questions to get quick insights
        5. **Chat**: Ask your own questions about the documents
        
        - 📚 **Multi-PDF Support**: Upload and analyze multiple documents simultaneously
        - 🤖 **Gemini AI**: Powered by Google's advanced Gemini language model
        - 🎯 **Card-based UI**: Easy navigation between different document sections
        - 📝 **Smart Summaries**: Get concise summaries of each document + combined overview
        - 💡 **Suggested Questions**: Get relevant questions to explore your documents
        - 💬 **Intelligent Chat**: Ask questions and get contextual answers
        - 🔍 **Semantic Search**: Find relevant information across all your documents
        """)

if __name__ == "__main__":
    main()
