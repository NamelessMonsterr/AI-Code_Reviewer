import openai
import os
from typing import List, Dict

class InteractiveChatbot:
    """Interactive Q&A for code review clarifications"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
        self.conversation_history = []
    
    def start_conversation(self, code_context: str, issue: str):
        """Initialize conversation with code context"""
        self.conversation_history = [
            {
                'role': 'system',
                'content': 'You are an expert code reviewer. Answer questions about code issues clearly and concisely.'
            },
            {
                'role': 'user',
                'content': f"Code context:\n{code_context}\n\nIssue found: {issue}"
            }
        ]
    
    def ask_question(self, question: str) -> str:
        """Ask follow-up question about code issue"""
        self.conversation_history.append({
            'role': 'user',
            'content': question
        })
        
        response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=self.conversation_history,
            temperature=0.3,
            max_tokens=300
        )
        
        answer = response.choices[0].message.content
        self.conversation_history.append({
            'role': 'assistant',
            'content': answer
        })
        
        return answer
    
    def explain_issue(self, issue: str, code: str) -> str:
        """Detailed explanation of code issue"""
        prompt = f"""Explain this code issue in detail:

Issue: {issue}

Code:
{code}

Provide:
1. What the issue is
2. Why it's a problem
3. How to fix it
4. Best practices to avoid it"""
        
        response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.2
        )
        
        return response.choices[0].message.content
    
    def suggest_alternatives(self, code: str, language: str) -> List[str]:
        """Suggest alternative implementations"""
        prompt = f"""Provide 3 alternative implementations for this {language} code:

{code}

For each alternative, explain:
- The approach
- Pros and cons
- Performance implications"""
        
        response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.4
        )
        
        return response.choices[0].message.content.split('\n\n')
