import json
from typing import List, Dict
from collections import defaultdict
import numpy as np

class BugPatternLearner:
    """Learn from historical bugs to predict future issues"""
    
    def __init__(self):
        self.bug_patterns = defaultdict(lambda: {
            'count': 0,
            'severity_scores': [],
            'fix_patterns': [],
            'time_to_fix': []
        })
        self.bug_history_file = 'bug_history.json'
    
    def record_bug(self, bug: Dict):
        """Record a bug for pattern learning"""
        pattern_key = self._extract_pattern_key(bug)
        
        self.bug_patterns[pattern_key]['count'] += 1
        self.bug_patterns[pattern_key]['severity_scores'].append(bug['severity'])
        self.bug_patterns[pattern_key]['fix_patterns'].append(bug['fix_pattern'])
        self.bug_patterns[pattern_key]['time_to_fix'].append(bug.get('time_to_fix', 0))
        
        self._save_patterns()
    
    def _extract_pattern_key(self, bug: Dict) -> str:
        """Extract pattern signature from bug"""
        # Combine bug type, file type, and location
        return f"{bug['type']}:{bug.get('file_extension', 'unknown')}:{bug.get('function_type', 'unknown')}"
    
    def predict_bug_probability(self, code: str, file_path: str) -> Dict:
        """Predict probability of bugs in code"""
        predictions = []
        
        for pattern_key, data in self.bug_patterns.items():
            if data['count'] < 3:  # Need minimum occurrences
                continue
            
            # Calculate probability based on historical data
            probability = self._calculate_probability(code, pattern_key, data)
            
            if probability > 0.3:  # Threshold for reporting
                predictions.append({
                    'pattern': pattern_key,
                    'probability': probability,
                    'historical_count': data['count'],
                    'avg_severity': np.mean(data['severity_scores']),
                    'avg_fix_time': np.mean(data['time_to_fix']),
                    'recommendation': self._get_recommendation(pattern_key, data)
                })
        
        return {
            'predictions': sorted(predictions, key=lambda x: x['probability'], reverse=True),
            'risk_score': self._calculate_risk_score(predictions)
        }
    
    def _calculate_probability(self, code: str, pattern_key: str, data: Dict) -> float:
        """Calculate probability of bug occurrence"""
        # Simple heuristic - in production, use ML model
        base_probability = min(data['count'] / 100.0, 0.8)
        
        # Check for pattern indicators in code
        pattern_parts = pattern_key.split(':')
        indicators_found = sum(1 for part in pattern_parts if part in code.lower())
        
        return base_probability * (indicators_found / len(pattern_parts))
    
    def _calculate_risk_score(self, predictions: List[Dict]) -> float:
        """Calculate overall risk score for code"""
        if not predictions:
            return 0.0
        
        weighted_risk = sum(
            p['probability'] * p['avg_severity'] 
            for p in predictions
        )
        return min(weighted_risk / len(predictions), 1.0)
    
    def _get_recommendation(self, pattern_key: str, data: Dict) -> str:
        """Get recommendation based on historical fixes"""
        if not data['fix_patterns']:
            return "Review carefully for potential issues"
        
        # Most common fix pattern
        fix_counts = defaultdict(int)
        for fix in data['fix_patterns']:
            fix_counts[fix] += 1
        
        most_common_fix = max(fix_counts.items(), key=lambda x: x[1])[0]
        return f"Consider: {most_common_fix}"
    
    def _save_patterns(self):
        """Save learned patterns to file"""
        # Convert defaultdict to regular dict for JSON serialization
        patterns_dict = {k: dict(v) for k, v in self.bug_patterns.items()}
        
        with open(self.bug_history_file, 'w') as f:
            json.dump(patterns_dict, f, indent=2)
    
    def load_patterns(self):
        """Load previously learned patterns"""
        try:
            with open(self.bug_history_file, 'r') as f:
                patterns = json.load(f)
                self.bug_patterns = defaultdict(lambda: {
                    'count': 0,
                    'severity_scores': [],
                    'fix_patterns': [],
                    'time_to_fix': []
                })
                self.bug_patterns.update(patterns)
        except FileNotFoundError:
            pass
