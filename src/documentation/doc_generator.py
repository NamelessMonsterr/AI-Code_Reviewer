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

Include:
1. Brief description
2. Parameters with types
3. Return value with type
4. Raises/Exceptions
5. Example usage"""
        
        response = self.client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.2
        )
        
        return response.choices[0].message.content
    
    def generate_readme(self, repo_structure: Dict, main_files: List[str]) -> str:
        """Generate comprehensive README.md"""
        prompt = f"""Generate a professional README.md for a project with this structure:

Repository Structure:
{repo_structure}

Main Files:
{main_files}

Include:
1. Project title and description
2. Features
3. Installation instructions
4. Usage examples
5. API documentation
6. Contributing guidelines
7. License"""
        
        response = self.client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def generate_api_docs(self, endpoint_code: str) -> str:
        """Generate OpenAPI/Swagger documentation"""
        prompt = f"""Generate OpenAPI 3.0 documentation for this API endpoint:

{endpoint_code}

Include complete schema with:
1. Path and method
2. Request parameters
3. Request body schema
4. Response schemas (success and errors)
5. Authentication requirements
6. Examples"""
        
        response = self.client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.2
        )
        
        return response.choices[0].message.content
    
    def _get_doc_style(self, language: str) -> str:
        """Get documentation style for language"""
        styles = {
            'python': 'Google-style Python docstring',
            'javascript': 'JSDoc',
            'java': 'Javadoc',
            'go': 'GoDoc',
            'ruby': 'YARD'
        }
        return styles.get(language.lower(), 'standard documentation')
