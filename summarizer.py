from typing import List, Dict
from model import GeminiModel

class PDFSummarizer:
    def __init__(self, model: GeminiModel):
        self.model = model
    
    def summarize_text(self, text: str, filename: str = "document") -> str:
        """Summarize text using Gemini."""
        text_sample = text[:8000] if len(text) > 8000 else text
        
        prompt = f"""Please provide a comprehensive summary of the following document ({filename}):
        
{text_sample}

Summary should include:
- Main topics and themes
- Key points and findings
- Important conclusions
- Document structure and organization

Please format the summary in a clear, structured way with bullet points where appropriate."""
        
        try:
            return self.model.generate_content(prompt)
        except Exception as e:
            return f"Error summarizing {filename}: {str(e)}"
    
    def summarize_single_document(self, text: str, filename: str) -> str:
        """Summarize a single document using Gemini."""
        return self.summarize_text(text, filename)
    
    def summarize_multiple_documents(self, documents_data: Dict[str, str]) -> Dict[str, str]:
        """Summarize multiple documents."""
        summaries = {}
        
        for filename, text in documents_data.items():
            summary = self.summarize_single_document(text, filename)
            summaries[filename] = summary
            print(f"Summarized: {filename}")
        
        return summaries
    
    def create_combined_summary(self, summaries: Dict[str, str]) -> str:
        """Create a combined summary of all documents."""
        combined_text = "\n\n".join([f"Document: {filename}\n{summary}" 
                                   for filename, summary in summaries.items()])
        
        prompt = f"""Based on the following individual document summaries, create a comprehensive overview:
        
{combined_text}
        
Please provide:
1. Common themes across documents
2. Key differences between documents
3. Overall insights and conclusions"""
        
        try:
            return self.model.generate_content(prompt)
        except Exception as e:
            return f"Error creating combined summary: {str(e)}"
