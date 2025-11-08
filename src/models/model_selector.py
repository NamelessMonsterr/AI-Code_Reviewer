import os
from typing import Dict, List
from enum import Enum

class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    DEEPSEEK = "deepseek"
    LOCAL = "local"

class ModelSelector:
    """Intelligent model selection for cost optimization"""
    
    def __init__(self):
        self.models = {
            ModelProvider.OPENAI: {
                'gpt-4': {'cost_per_1k': 0.03, 'quality': 0.95},
                'gpt-3.5-turbo': {'cost_per_1k': 0.002, 'quality': 0.75}
            },
            ModelProvider.ANTHROPIC: {
                'claude-3-opus': {'cost_per_1k': 0.015, 'quality': 0.93},
                'claude-3-sonnet': {'cost_per_1k': 0.003, 'quality': 0.85}
            },
            ModelProvider.GOOGLE: {
                'gemini-pro': {'cost_per_1k': 0.00025, 'quality': 0.80}
            }
        }
        self.usage_tracker = {}
    
    def select_model(self, task_type: str, code_length: int) -> Dict:
        """Select optimal model based on task and budget"""
        if task_type == 'style_check':
            # Use cheaper model for style checks
            return {
                'provider': ModelProvider.OPENAI,
                'model': 'gpt-3.5-turbo'
            }
        elif task_type == 'security_review':
            # Use premium model for security
            return {
                'provider': ModelProvider.ANTHROPIC,
                'model': 'claude-3-opus'
            }
        elif task_type == 'code_fix':
            # Balanced model for fixes
            return {
                'provider': ModelProvider.ANTHROPIC,
                'model': 'claude-3-sonnet'
            }
        else:
            # Default to balanced model
            return {
                'provider': ModelProvider.OPENAI,
                'model': 'gpt-4'
            }
    
    def track_usage(self, provider: ModelProvider, model: str, tokens: int):
        """Track model usage for cost analysis"""
        key = f"{provider.value}:{model}"
        if key not in self.usage_tracker:
            self.usage_tracker[key] = {'tokens': 0, 'calls': 0, 'cost': 0.0}
        
        self.usage_tracker[key]['tokens'] += tokens
        self.usage_tracker[key]['calls'] += 1
        
        cost_per_1k = self.models[provider][model]['cost_per_1k']
        self.usage_tracker[key]['cost'] += (tokens / 1000) * cost_per_1k
    
    def get_cost_report(self) -> Dict:
        """Generate cost usage report"""
        total_cost = sum(data['cost'] for data in self.usage_tracker.values())
        return {
            'total_cost': round(total_cost, 4),
            'by_model': self.usage_tracker
        }
