from typing import Dict, List
import numpy as np

class SeverityScorer:
    """Automatically score issue severity using ML"""
    
    def __init__(self):
        self.weights = {
            'security': 10.0,
            'performance': 7.0,
            'correctness': 8.0,
            'maintainability': 5.0,
            'style': 2.0
        }
        self.historical_scores = []
    
    def calculate_severity(self, issue: Dict) -> Dict:
        """Calculate severity score for an issue"""
        # Base score from issue category
        category = issue.get('category', 'style')
        base_score = self.weights.get(category, 5.0)
        
        # Adjust for context
        context_multiplier = self._get_context_multiplier(issue)
        impact_score = self._calculate_impact(issue)
        frequency_score = self._get_frequency_score(issue)
        
        # Calculate final score
        final_score = base_score * context_multiplier * impact_score * frequency_score
        
        # Normalize to 0-10 scale
        normalized_score = min(max(final_score / 10, 0), 10)
        
        # Determine severity level
        severity_level = self._get_severity_level(normalized_score)
        
        return {
            'severity_score': round(normalized_score, 2),
            'severity_level': severity_level,
            'category': category,
            'factors': {
                'base_score': base_score,
                'context_multiplier': context_multiplier,
                'impact_score': impact_score,
                'frequency_score': frequency_score
            }
        }
    
    def _get_context_multiplier(self, issue: Dict) -> float:
        """Get context-based multiplier"""
        multiplier = 1.0
        
        # Critical files (auth, payment, etc.)
        critical_keywords = ['auth', 'payment', 'security', 'admin']
        file_path = issue.get('file_path', '').lower()
        if any(kw in file_path for kw in critical_keywords):
            multiplier *= 1.5
        
        # Production code vs test code
        if 'test' in file_path or 'spec' in file_path:
            multiplier *= 0.7
        
        return multiplier
    
    def _calculate_impact(self, issue: Dict) -> float:
        """Calculate potential impact of issue"""
        impact_indicators = {
            'data_loss': 2.0,
            'security_breach': 2.0,
            'crash': 1.8,
            'memory_leak': 1.5,
            'performance_degradation': 1.3,
            'incorrect_output': 1.2,
            'poor_ux': 1.0
        }
        
        description = issue.get('description', '').lower()
        
        for indicator, score in impact_indicators.items():
            if indicator in description:
                return score
        
        return 1.0
    
    def _get_frequency_score(self, issue: Dict) -> float:
        """Score based on how frequently this issue occurs"""
        issue_type = issue.get('type', 'unknown')
        
        # Check historical frequency
        frequency = sum(1 for h in self.historical_scores if h.get('type') == issue_type)
        
        if frequency > 10:
            return 1.3  # Common issue, should be addressed
        elif frequency > 5:
            return 1.1
        else:
            return 1.0
    
    def _get_severity_level(self, score: float) -> str:
        """Convert numeric score to severity level"""
        if score >= 8.0:
            return 'CRITICAL'
        elif score >= 6.0:
            return 'HIGH'
        elif score >= 4.0:
            return 'MEDIUM'
        elif score >= 2.0:
            return 'LOW'
        else:
            return 'INFO'
    
    def learn_from_feedback(self, issue: Dict, user_severity: str):
        """Learn from user corrections to severity"""
        calculated = self.calculate_severity(issue)
        
        self.historical_scores.append({
            'type': issue.get('type'),
            'calculated_severity': calculated['severity_level'],
            'user_severity': user_severity,
            'issue': issue
        })
        
        # Adjust weights if consistent mismatch
        self._adjust_weights()
    
    def _adjust_weights(self):
        """Adjust weights based on user feedback"""
        if len(self.historical_scores) < 10:
            return
        
        # Analyze recent feedback
        recent = self.historical_scores[-20:]
        mismatches = [h for h in recent if h['calculated_severity'] != h['user_severity']]
        
        if len(mismatches) > 10:
            # Adjust weights (simplified - in production use ML)
            for category in self.weights:
                self.weights[category] *= 0.95  # Slight adjustment
