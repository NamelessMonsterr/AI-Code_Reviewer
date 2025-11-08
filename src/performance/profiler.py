from openai import OpenAI
import os
from typing import Dict, List

class PerformanceProfiler:
    """Analyze and suggest performance optimizations"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=self.api_key)
    
    def analyze_performance(self, code: str, language: str) -> Dict:
        """Analyze code for performance issues"""
        prompt = f"""Analyze this {language} code for performance issues:

{code}

Identify:
1. Time complexity (Big O)
2. Space complexity
3. Potential bottlenecks
4. Inefficient algorithms
5. Memory leaks
6. N+1 query problems (if database code)"""
        
        response = self.client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.2
        )
        
        analysis = response.choices[0].message.content
        
        return {
            'analysis': analysis,
            'recommendations': self._extract_recommendations(analysis)
        }
    
    def suggest_optimizations(self, code: str, language: str) -> List[Dict]:
        """Suggest specific performance optimizations"""
        prompt = f"""Suggest performance optimizations for this {language} code:

{code}

For each optimization provide:
1. Original code snippet
2. Optimized version
3. Performance improvement (estimated %)
4. Trade-offs"""
        
        response = self.client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.2,
            max_tokens=1000
        )
        
        return self._parse_optimizations(response.choices[0].message.content)
    
    def detect_antipatterns(self, code: str, language: str) -> List[str]:
        """Detect performance anti-patterns"""
        antipatterns = {
            'python': [
                'Using + for string concatenation in loops',
                'Not using list comprehensions',
                'Using global variables excessively',
                'Not using generators for large datasets'
            ],
            'javascript': [
                'DOM manipulation in loops',
                'Not debouncing event handlers',
                'Memory leaks with event listeners',
                'Blocking the event loop'
            ],
            'java': [
                'Creating unnecessary objects',
                'String concatenation with +',
                'Not using connection pooling',
                'Synchronization overhead'
            ]
        }
        
        detected = []
        patterns = antipatterns.get(language.lower(), [])
        
        for pattern in patterns:
            if self._check_pattern(code, pattern):
                detected.append(pattern)
        
        return detected
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract recommendations from analysis"""
        lines = analysis.split('\n')
        return [line for line in lines if 'recommend' in line.lower() or 'should' in line.lower()]
    
    def _parse_optimizations(self, text: str) -> List[Dict]:
        """Parse optimization suggestions"""
        return [{'optimization': text}]
    
    def _check_pattern(self, code: str, pattern: str) -> bool:
        """Check if anti-pattern exists in code"""
        keywords = pattern.lower().split()
        return any(kw in code.lower() for kw in keywords[:2])
