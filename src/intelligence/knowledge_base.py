import json
from typing import List, Dict
from datetime import datetime

class KnowledgeBase:
    """Build and maintain team-specific knowledge base"""
    
    def __init__(self):
        self.kb_file = 'team_knowledge.json'
        self.knowledge = {
            'best_practices': [],
            'common_mistakes': [],
            'approved_patterns': [],
            'deprecated_patterns': [],
            'team_guidelines': []
        }
        self.load_knowledge()
    
    def add_best_practice(self, practice: Dict):
        """Add a best practice to knowledge base"""
        entry = {
            'title': practice['title'],
            'description': practice['description'],
            'code_example': practice.get('example', ''),
            'category': practice.get('category', 'general'),
            'added_date': datetime.now().isoformat(),
            'approval_count': 0
        }
        self.knowledge['best_practices'].append(entry)
        self.save_knowledge()
    
    def add_common_mistake(self, mistake: Dict):
        """Record common mistake for future prevention"""
        entry = {
            'description': mistake['description'],
            'occurrences': mistake.get('occurrences', 1),
            'fix': mistake.get('fix', ''),
            'severity': mistake.get('severity', 'medium'),
            'last_seen': datetime.now().isoformat()
        }
        self.knowledge['common_mistakes'].append(entry)
        self.save_knowledge()
    
    def approve_pattern(self, pattern: Dict):
        """Approve a coding pattern for team use"""
        entry = {
            'pattern_name': pattern['name'],
            'description': pattern['description'],
            'code_template': pattern.get('template', ''),
            'use_cases': pattern.get('use_cases', []),
            'approved_by': pattern.get('approver', 'team'),
            'approved_date': datetime.now().isoformat()
        }
        self.knowledge['approved_patterns'].append(entry)
        self.save_knowledge()
    
    def deprecate_pattern(self, pattern_name: str, reason: str):
        """Deprecate an old coding pattern"""
        entry = {
            'pattern_name': pattern_name,
            'reason': reason,
            'deprecated_date': datetime.now().isoformat(),
            'replacement': None
        }
        self.knowledge['deprecated_patterns'].append(entry)
        self.save_knowledge()
    
    def query_knowledge(self, query: str, category: str = None) -> List[Dict]:
        """Query knowledge base"""
        results = []
        
        for cat, items in self.knowledge.items():
            if category and cat != category:
                continue
            
            for item in items:
                # Simple text matching - in production use semantic search
                item_text = json.dumps(item).lower()
                if query.lower() in item_text:
                    results.append({
                        'category': cat,
                        'item': item,
                        'relevance': self._calculate_relevance(query, item)
                    })
        
        return sorted(results, key=lambda x: x['relevance'], reverse=True)
    
    def _calculate_relevance(self, query: str, item: Dict) -> float:
        """Calculate relevance score"""
        # Simple keyword matching
        query_words = set(query.lower().split())
        item_text = json.dumps(item).lower()
        
        matches = sum(1 for word in query_words if word in item_text)
        return matches / len(query_words) if query_words else 0.0
    
    def get_recommendations_for_code(self, code: str, language: str) -> List[Dict]:
        """Get relevant recommendations for code"""
        recommendations = []
        
        # Check against common mistakes
        for mistake in self.knowledge['common_mistakes']:
            if self._check_mistake_pattern(code, mistake):
                recommendations.append({
                    'type': 'mistake_prevention',
                    'message': mistake['description'],
                    'fix': mistake['fix'],
                    'severity': mistake['severity']
                })
        
        # Check deprecated patterns
        for pattern in self.knowledge['deprecated_patterns']:
            if pattern['pattern_name'].lower() in code.lower():
                recommendations.append({
                    'type': 'deprecated_pattern',
                    'message': f"Pattern '{pattern['pattern_name']}' is deprecated",
                    'reason': pattern['reason']
                })
        
        return recommendations
    
    def _check_mistake_pattern(self, code: str, mistake: Dict) -> bool:
        """Check if code contains common mistake pattern"""
        # Simplified check
        keywords = mistake['description'].lower().split()[:3]
        return any(kw in code.lower() for kw in keywords)
    
    def save_knowledge(self):
        """Save knowledge base to file"""
        with open(self.kb_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def load_knowledge(self):
        """Load knowledge base from file"""
        try:
            with open(self.kb_file, 'r') as f:
                self.knowledge = json.load(f)
        except FileNotFoundError:
            pass
