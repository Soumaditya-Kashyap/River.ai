import PyPDF2
import os
from typing import List, Dict
import tiktoken

class MultiPDFProcessor:
    def __init__(self, max_chunk_size: int = 1000):
        self.max_chunk_size = max_chunk_size
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.documents = {}
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a single PDF file."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading {pdf_path}: {str(e)}")
        return text
    
    def chunk_text(self, text: str, filename: str) -> List[Dict[str, str]]:
        """Split text into chunks with metadata."""
        tokens = self.encoding.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), self.max_chunk_size):
            chunk_tokens = tokens[i:i + self.max_chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append({
                'text': chunk_text,
                'source': filename,
                'chunk_id': f"{filename}_chunk_{len(chunks)}"
            })
        
        return chunks
    
    def process_multiple_pdfs(self, pdf_paths: List[str]) -> Dict[str, List[Dict[str, str]]]:
        """Process multiple PDF files and return chunked text."""
        all_chunks = {}
        
        for pdf_path in pdf_paths:
            if os.path.exists(pdf_path):
                filename = os.path.basename(pdf_path)
                print(f"Processing {filename}...")
                
                text = self.extract_text_from_pdf(pdf_path)
                if text.strip():
                    chunks = self.chunk_text(text, filename)
                    all_chunks[filename] = chunks
                    self.documents[filename] = {
                        'path': pdf_path,
                        'text': text,
                        'chunks': chunks
                    }
                else:
                    print(f"No text extracted from {filename}")
            else:
                print(f"File not found: {pdf_path}")
        
        return all_chunks
    
    def get_document_info(self) -> Dict[str, Dict]:
        """Get information about processed documents."""
        info = {}
        for filename, doc_data in self.documents.items():
            info[filename] = {
                'chunk_count': len(doc_data['chunks']),
                'total_length': len(doc_data['text'])
            }
        return info
    
    def process_pdf(self, uploaded_file) -> List[Dict[str, str]]:
        """Process a single PDF uploaded via Streamlit."""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            return []
        
        if not text.strip():
            return []
        
        # Create chunks with page information
        tokens = self.encoding.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), self.max_chunk_size):
            chunk_tokens = tokens[i:i + self.max_chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append({
                'text': chunk_text,
                'source': uploaded_file.name,
                'chunk_id': f"{uploaded_file.name}_chunk_{len(chunks)}",
                'page': f"Pages {i//self.max_chunk_size + 1}-{min((i+self.max_chunk_size)//self.max_chunk_size + 1, len(tokens)//self.max_chunk_size + 1)}"
            })
        
        return chunks
