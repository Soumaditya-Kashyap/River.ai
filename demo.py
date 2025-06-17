import os
from dotenv import load_dotenv
from model import GeminiModel
from pdf_processor import MultiPDFProcessor
from summarizer import PDFSummarizer
from chat_interface import MultiPDFChatbot

def main():
    """Demo the multi-PDF chatbot functionality"""
    print("Multi-PDF Chatbot Demo")
    print("=" * 50)
    
    
    
    
    
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: Please set GEMINI_API_KEY in your .env file")
        return
    
    try:
        
        print("Initializing Gemini model...")
        model = GeminiModel(api_key)
        
        print("Initializing PDF processor...")
        processor = MultiPDFProcessor()
        
        print("Initializing summarizer...")
        summarizer = PDFSummarizer(model)
        
        print("Initializing chatbot...")
        chatbot = MultiPDFChatbot(model)
        
        print("\n✅ All components initialized successfully!")
        print("\nTo use the full application, run:")
        print("python run_app.py")
        print("or")
        print("streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Error initializing components: {e}")

if __name__ == "__main__":
    main()