import os
import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class CodeFixer:
    """Generate AI-powered code fixes for identified issues"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_fix(self, code: str, issue: str, lang: str) -> Optional[str]:
        """
        Generate a fix for code issue using GPT-4
        
        Args:
            code: The problematic code snippet
            issue: Description of the issue
            lang: Programming language
            
        Returns:
            Fixed code or None if generation fails
        """
        messages = [
            {
                "role": "system",
                "content": f"You are an expert {lang} developer. Provide only the fixed code without explanations."
            },
            {
                "role": "user",
                "content": f"Fix this {lang} code issue:\n\nIssue: {issue}\n\nCode:\n```{lang}\n{code}\n```\n\nProvide only the corrected code."
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.2,
                max_tokens=500
            )
            
            fixed_code = response.choices[0].message.content
            logger.info(f"Successfully generated fix for {lang} code issue")
            return self._extract_code_from_response(fixed_code, lang)
            
        except Exception as e:
            logger.error(f"Failed to generate fix: {str(e)}")
            raise
    
    def _extract_code_from_response(self, response: str, lang: str) -> str:
        """Extract code from markdown code blocks if present"""
        # Remove markdown code fences if present
        if f"```{lang}" in response:
            lines = response.split('\n')
            code_lines = []
            in_code_block = False
            
            for line in lines:
                if line.startswith(f"```{lang}") or line.startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    code_lines.append(line)
            
            return '\n'.join(code_lines).strip()
        
        return response.strip()
    
    def suggest_alternative_fixes(self, code: str, issue: str, lang: str, 
                                  num_alternatives: int = 3) -> list[str]:
        """
        Generate multiple alternative fixes
        
        Args:
            code: The problematic code
            issue: Description of the issue
            lang: Programming language
            num_alternatives: Number of alternatives to generate
            
        Returns:
            List of alternative fixes
        """
        alternatives = []
        
        for i in range(num_alternatives):
            try:
                messages = [
                    {
                        "role": "system",
                        "content": f"You are an expert {lang} developer. Provide alternative solution #{i+1}."
                    },
                    {
                        "role": "user",
                        "content": f"Provide an alternative fix for this {lang} code:\n\nIssue: {issue}\n\nCode:\n```{lang}\n{code}\n```"
                    }
                ]
                
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.4 + (i * 0.2),  # Increase temperature for variety
                    max_tokens=500
                )
                
                fix = response.choices[0].message.content
                alternatives.append(self._extract_code_from_response(fix, lang))
                
            except Exception as e:
                logger.error(f"Failed to generate alternative {i+1}: {str(e)}")
                continue
        
        return alternatives
