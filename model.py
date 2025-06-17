"""
Gemini AI Model Integration
Handles Google Gemini API interactions for the Multi-PDF Chatbot
"""

import google.generativeai as genai
from typing import Optional, Dict, Any
import logging

class GeminiModel:
    """
    Wrapper class for Google Gemini AI model
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the Gemini model
        
        Args:
            api_key (str): Google Gemini API key
            model_name (str): Model name to use (default: gemini-1.5-flash)
        """
        self.api_key = api_key
        self.model_name = model_name
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Generation configuration
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 4096,
        }
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        
        logging.info(f"Initialized Gemini model: {self.model_name}")
    
    def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Generate content using Gemini model
        
        Args:
            prompt (str): Input prompt for generation
            **kwargs: Additional generation parameters
            
        Returns:
            str: Generated content
            
        Raises:
            Exception: If generation fails
        """
        try:
       
            generation_config = {**self.generation_config, **kwargs}
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response.text:
                return response.text
            else:
                raise Exception("Empty response from Gemini model")
                
        except Exception as e:
            logging.error(f"Error generating content: {str(e)}")
            raise Exception(f"Failed to generate content: {str(e)}")
    
    def generate_summary(self, text: str, max_length: int = 500) -> str:
        """
        Generate a summary of the provided text
        
        Args:
            text (str): Text to summarize
            max_length (int): Maximum length of summary
            
        Returns:
            str: Generated summary
        """
        prompt = f"""Please provide a comprehensive summary of the following text. 
        Keep the summary concise but informative, focusing on the main points and key insights.
        Maximum length: {max_length} words.

        Text to summarize:
        {text}

        Summary:"""
        
        return self.generate_content(prompt, max_output_tokens=max_length * 2)
    
    def answer_question(self, context: str, question: str) -> str:
        """
        Answer a question based on provided context
        
        Args:
            context (str): Context information
            question (str): Question to answer
            
        Returns:
            str: Generated answer
        """
        prompt = f"""Based on the following context, please answer the question accurately and comprehensively.
        If the context doesn't contain enough information to answer the question, please state that clearly.

        Context:
        {context}

        Question: {question}

        Answer:"""
    
        return self.generate_content(prompt)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            dict: Model information
        """
        return {
            "model_name": self.model_name,
            "generation_config": self.generation_config,
            "safety_settings": self.safety_settings
        }