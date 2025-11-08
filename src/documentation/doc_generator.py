from openai import OpenAI
import os
from typing import Dict, List

class DocumentationGenerator:
    """Auto-generate code documentation"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_docstring(self, function_code: str, language: str) -> str:
        """Generate docstring/documentation for function"""
        style = self._get_doc_style(language)
        
        prompt = f"""Generate {style} documentation for this {language} function:

{function_code}
