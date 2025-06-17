from typing import List, Dict, Tuple
from model import GeminiModel
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MultiPDFChatbot:
    def __init__(self, model: GeminiModel):
        self.model = model
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.document_vectors = None
        self.all_chunks = []
        
    def load_documents(self, pdf_data: Dict[str, List[Dict]]):
        """Load and process multiple PDF documents."""
        # Flatten all chunks for similarity search
        self.all_chunks = []
        chunk_texts = []
        
        for filename, chunks in pdf_data.items():
            for chunk in chunks:
                chunk_data = {
                    'text': chunk['text'],
                    'source': filename,
                    'page': chunk.get('page', 'Unknown'),
                    'chunk_id': chunk.get('chunk_id', f"{filename}_{len(self.all_chunks)}")
                }
                self.all_chunks.append(chunk_data)
                chunk_texts.append(chunk['text'])
        
        # Create TF-IDF vectors for similarity search
        if chunk_texts:
            try:
                self.document_vectors = self.vectorizer.fit_transform(chunk_texts)
                print(f"Loaded {len(self.all_chunks)} chunks from {len(pdf_data)} documents")
                print(f"Vector shape: {self.document_vectors.shape}")
            except Exception as e:
                print(f"Error creating vectors: {e}")
                self.document_vectors = None
    
    def find_relevant_chunks(self, query: str, top_k: int = 3) -> List[Dict]:
        """Find most relevant chunks for a query."""
        if self.document_vectors is None or len(self.all_chunks) == 0:
            return []
        
        try:
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
            
            # Get top k most similar chunks, ensuring we don't exceed available chunks
            actual_k = min(top_k, len(similarities))
            top_indices = np.argsort(similarities)[-actual_k:][::-1]
            
            # Filter out chunks with very low similarity (threshold: 0.05)
            relevant_chunks = []
            for idx in top_indices:
                if similarities[idx] > 0.05:  # Lower minimum similarity threshold
                    chunk = self.all_chunks[idx].copy()
                    chunk['similarity'] = similarities[idx]
                    relevant_chunks.append(chunk)
            
            # If no chunks meet similarity threshold, return top 2 anyway
            if not relevant_chunks and len(top_indices) > 0:
                for idx in top_indices[:2]:
                    chunk = self.all_chunks[idx].copy()
                    chunk['similarity'] = similarities[idx]
                    relevant_chunks.append(chunk)
            
            return relevant_chunks
        except Exception as e:
            print(f"Error finding relevant chunks: {e}")
            return []
    
    def chat(self, user_query: str) -> str:
        """Process user query and return AI response."""
        relevant_chunks = self.find_relevant_chunks(user_query, top_k=5)
        
        if not relevant_chunks:
            return "I don't have any relevant information to answer your question. Could you try rephrasing your question or asking about specific topics from your documents?"
        
        # Build context from relevant chunks
        context_parts = []
        for chunk in relevant_chunks:
            context_parts.append(f"From {chunk['source']}:\n{chunk['text'][:1000]}")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""Based on the following information from the loaded documents, please answer the user's question accurately and comprehensively:
        
Context from documents:
{context}

User Question: {user_query}

Please provide a detailed answer based on the provided context. If you need more specific information, suggest what the user should ask about."""
        
        try:
            response = self.model.generate_content(prompt)
            return response
        except Exception as e:
            return f"Error processing your question: {str(e)}. Please try again."
    
    def get_document_list(self) -> List[str]:
        """Get list of loaded documents."""
        return list(set([chunk['source'] for chunk in self.all_chunks]))

    def generate_suggested_questions(self, document_content: str = None) -> List[str]:
        """Generate suggested questions based on document content."""
        if document_content:
            # Generate questions based on specific document
            prompt = f"""Based on the following document content, generate 7 short, relevant questions (max 8-10 words each) that someone might ask:

{document_content[:2000]}

Generate exactly 7 short questions in this format:
1. What is the main topic?
2. What are key findings?
3. What methodology was used?
4. What are the conclusions?
5. What are the implications?
6. What recommendations are made?
7. What future research is needed?

Make each question concise and specific to the content."""
        else:
            # Generate general questions based on all loaded documents
            if not self.all_chunks:
                return [
                    "What is the main topic?",
                    "What are key findings?", 
                    "What methodology was used?",
                    "What are the conclusions?",
                    "What are the implications?"
                ]
            
            sample_content = "\n".join([chunk['text'][:200] for chunk in self.all_chunks[:5]])
            prompt = f"""Based on the following sample content, generate 7 short questions (max 8-10 words each):

{sample_content}

Generate exactly 7 short, relevant questions that would help understand these documents."""
        
        try:
            response = self.model.generate_content(prompt)
            # Extract questions from response
            lines = response.split('\n')
            questions = []
            for line in lines:
                line = line.strip()
                if line and ('?' in line):
                    # Remove numbering and clean up
                    clean_question = line
                    if '. ' in line:
                        clean_question = line.split('. ', 1)[1] if len(line.split('. ', 1)) > 1 else line
                    # Keep questions short
                    if len(clean_question) > 80:
                        clean_question = clean_question[:77] + "..."
                    questions.append(clean_question)
                    if len(questions) >= 7:
                        break
            
            return questions if questions else [
                "What is the main topic?",
                "What are key findings?",
                "What methodology was used?",
                "What are the conclusions?",
                "What are the implications?",
                "What recommendations exist?",
                "What future work is suggested?"
            ]
        except Exception as e:
            print(f"Error generating questions: {e}")
            return [
                "What is the main topic?",
                "What are key findings?",
                "What methodology was used?",
                "What are the conclusions?",
                "What are the implications?",
                "What recommendations exist?",
                "What future work is suggested?"
            ]
