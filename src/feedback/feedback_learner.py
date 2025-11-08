import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FeedbackLearner:
    """Learn from user feedback to improve review quality"""
    
    def __init__(self, feedback_file: str = 'feedback_data.json', data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path('data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.data_dir / feedback_file
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self) -> Dict:
        """Load existing feedback data"""
        try:
            if self.feedback_file.exists():
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in feedback file, resetting")
        except Exception as e:
            logger.error(f"Error loading feedback: {str(e)}")
        
        return {'reviews': [], 'patterns': {}}
    
    def _save_feedback(self) -> None:
        """Save feedback data"""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            raise
    
    def record_feedback(self, review_id: str, comment_id: str, 
                       feedback_type: str, issue_type: str,
                       metadata: Optional[Dict] = None) -> None:
        """
        Record user feedback on review comments
        
        Args:
            review_id: Unique review identifier
            comment_id: Unique comment identifier
            feedback_type: Type of feedback ('upvote', 'downvote', 'dismiss', 'accept')
            issue_type: Type of issue being reviewed
            metadata: Additional feedback metadata
        """
        if feedback_type not in ['upvote', 'downvote', 'dismiss', 'accept']:
            raise ValueError(f"Invalid feedback type: {feedback_type}")
        
        try:
            feedback = {
                'review_id': review_id,
                'comment_id': comment_id,
                'feedback_type': feedback_type,
                'issue_type': issue_type,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            self.feedback_data['reviews'].append(feedback)
            self._update_patterns(issue_type, feedback_type)
            self._save_feedback()
            
            logger.info(f"Recorded {feedback_type} feedback for {issue_type}")
            
        except Exception as e:
            logger.error(f"Failed to record feedback: {str(e)}")
            raise
    
    def _update_patterns(self, issue_type: str, feedback_type: str) -> None:
        """Update learned patterns based on feedback"""
        if issue_type not in self.feedback_data['patterns']:
            self.feedback_data['patterns'][issue_type] = {
                'upvotes': 0,
                'downvotes': 0,
                'dismissals': 0,
                'accepts': 0,
                'total': 0
            }
        
        pattern = self.feedback_data['patterns'][issue_type]
        
        if feedback_type == 'upvote':
            pattern['upvotes'] += 1
        elif feedback_type == 'downvote':
            pattern['downvotes'] += 1
        elif feedback_type == 'dismiss':
            pattern['dismissals'] += 1
        elif feedback_type == 'accept':
            pattern['accepts'] += 1
        
        pattern['total'] += 1
    
    def get_issue_confidence(self, issue_type: str) -> float:
        """
        Calculate confidence score for an issue type based on historical feedback
        
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        if issue_type not in self.feedback_data['patterns']:
            return 0.5  # Default neutral confidence
        
        pattern = self.feedback_data['patterns'][issue_type]
        total = pattern.get('total', 0)
        
        if total == 0:
            return 0.5
        
        positive = pattern['upvotes'] + pattern['accepts']
        negative = pattern['downvotes'] + pattern['dismissals']
        
        # Calculate confidence with normalization
        confidence = (positive - negative) / total
        
        # Normalize to 0-1 scale
        normalized = (confidence + 1) / 2
        
        return max(0.0, min(1.0, normalized))
    
    def should_report_issue(self, issue_type: str, threshold: float = 0.3) -> bool:
        """
        Decide if issue should be reported based on learned feedback
        
        Args:
            issue_type: Type of issue to check
            threshold: Minimum confidence threshold (default 0.3)
            
        Returns:
            bool: True if issue should be reported
        """
        confidence = self.get_issue_confidence(issue_type)
        return confidence > threshold
    
    def get_feedback_summary(self) -> Dict:
        """Get summary of feedback patterns"""
        summary = {}
        
        for issue_type, stats in self.feedback_data['patterns'].items():
            total = stats.get('total', 0)
            summary[issue_type] = {
                'total_feedback': total,
                'confidence': self.get_issue_confidence(issue_type),
                'stats': {
                    'upvotes': stats['upvotes'],
                    'downvotes': stats['downvotes'],
                    'dismissals': stats['dismissals'],
                    'accepts': stats['accepts']
                },
                'approval_rate': (stats['upvotes'] + stats['accepts']) / total if total > 0 else 0
            }
        
        return summary
    
    def get_trending_issues(self, limit: int = 10) -> List[Dict]:
        """Get most commonly reported issues"""
        patterns = self.feedback_data['patterns']
        
        # Sort by total feedback count
        sorted_issues = sorted(
            patterns.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:limit]
        
        return [
            {
                'issue_type': issue_type,
                'count': stats['total'],
                'confidence': self.get_issue_confidence(issue_type)
            }
            for issue_type, stats in sorted_issues
        ]
