import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for handling Google Gemini AI operations"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def is_configured(self):
        """Check if Gemini is properly configured"""
        return self.model is not None and self.api_key
    
    def generate_response(self, message, context="You are a helpful AI tutor assistant. Give answers in a friendly and educational manner. 100 words only"):
        """Generate response using Gemini AI"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Gemini AI is not properly configured. Please check your API key.'
            }
        
        try:
            # Prepare the prompt with context
            prompt = f"{context}\n\nUser: {message}\nAI:"
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return {
                    'success': True,
                    'response': response.text.strip()
                }     
            else:
                return {
                    'success': False,
                    'error': 'No response generated'
                }
                
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_educational_content(self, topic, grade_level="general"):
        """Generate educational content for a specific topic"""
        context = f"""You are an expert educational AI tutor. Create engaging and educational content about the given topic. 
        Tailor the content for {grade_level} level understanding. 
        Make it informative, clear, and engaging."""
        
        prompt = f"Create educational content about: {topic}"
        return self.generate_response(prompt, context)
    
    def explain_concept(self, concept, difficulty="intermediate"):
        """Explain a concept in simple terms"""
        context = f"""You are a patient AI tutor. Explain concepts clearly and simply at a {difficulty} level. 
        Use examples and analogies when helpful. Break down complex ideas into understandable parts."""
        
        prompt = f"Please explain this concept: {concept}"
        return self.generate_response(prompt, context)