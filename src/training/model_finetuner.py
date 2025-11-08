from openai import OpenAI
import json
import os
from typing import List, Dict
from datetime import datetime

class ModelFineTuner:
    """Fine-tune AI models on team-specific code patterns"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=self.api_key)
        self.training_data = []
    
    def collect_training_data(self, code_review: Dict):
        """Collect training examples from historical reviews"""
        example = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert code reviewer for this specific codebase."
                },
                {
                    "role": "user",
                    "content": f"Review this code:\n{code_review['code']}"
                },
                {
                    "role": "assistant",
                    "content": code_review['review_comments']
                }
            ]
        }
        self.training_data.append(example)
    
    def prepare_training_file(self, output_file='training_data.jsonl'):
        """Prepare training data in JSONL format"""
        with open(output_file, 'w') as f:
            for example in self.training_data:
                f.write(json.dumps(example) + '\n')
        return output_file
    
    def upload_training_file(self, file_path: str) -> str:
        """Upload training file to OpenAI"""
        with open(file_path, 'rb') as f:
            response = self.client.files.create(
                file=f,
                purpose='fine-tune'
            )
        return response.id
    
    def start_fine_tuning(self, file_id: str, model='gpt-3.5-turbo') -> str:
        """Start fine-tuning job"""
        response = self.client.fine_tuning.jobs.create(
            training_file=file_id,
            model=model,
            hyperparameters={
                "n_epochs": 3,
                "batch_size": 4,
                "learning_rate_multiplier": 0.1
            }
        )
        return response.id
    
    def check_fine_tuning_status(self, job_id: str) -> Dict:
        """Check status of fine-tuning job"""
        response = self.client.fine_tuning.jobs.retrieve(job_id)
        return {
            'status': response.status,
            'trained_tokens': getattr(response, 'trained_tokens', 0),
            'fine_tuned_model': getattr(response, 'fine_tuned_model', None)
        }
    
    def use_fine_tuned_model(self, model_id: str, code: str) -> str:
        """Use fine-tuned model for code review"""
        response = self.client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "user", "content": f"Review this code:\n{code}"}
            ]
        )
        return response.choices[0].message.content
    
    def evaluate_model_performance(self, model_id: str, test_cases: List[Dict]) -> Dict:
        """Evaluate fine-tuned model against test cases"""
        results = {
            'total': len(test_cases),
            'correct': 0,
            'accuracy': 0.0,
            'details': []
        }
        
        for test in test_cases:
            prediction = self.use_fine_tuned_model(model_id, test['code'])
            is_correct = self._compare_reviews(prediction, test['expected_review'])
            
            if is_correct:
                results['correct'] += 1
            
            results['details'].append({
                'code': test['code'],
                'expected': test['expected_review'],
                'predicted': prediction,
                'correct': is_correct
            })
        
        results['accuracy'] = results['correct'] / results['total']
        return results
    
    def _compare_reviews(self, review1: str, review2: str) -> bool:
        """Compare two reviews for similarity"""
        keywords = ['issue', 'error', 'warning', 'fix', 'improve']
        review1_lower = review1.lower()
        review2_lower = review2.lower()
        
        matches = sum(1 for kw in keywords if kw in review1_lower and kw in review2_lower)
        return matches >= 3
