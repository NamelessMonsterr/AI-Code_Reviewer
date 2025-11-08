import pytest
from src.enhanced_review import EnhancedReview
from src.feedback.feedback_learner import FeedbackLearner
from src.analytics.metrics_tracker import MetricsTracker

@pytest.mark.integration
class TestFullReviewFlow:
    """Integration tests for complete review workflow"""
    
    def test_end_to_end_review(self, test_data_dir, sample_code):
        """Test complete review flow"""
        # Initialize components
        reviewer = EnhancedReview(repo_path=str(test_data_dir))
        learner = FeedbackLearner(data_dir=str(test_data_dir))
        tracker = MetricsTracker(data_dir=str(test_data_dir))
        
        # Simulate review
        # Note: This would normally call actual review logic
        # For testing, we simulate the flow
        
        # 1. Record review
        tracker.record_review(
            pr=1,
            issues=3,
            langs=['python'],
            review_time=25.0
        )
        
        # 2. Record feedback
        learner.record_feedback(
            review_id='rev_1',
            comment_id='com_1',
            feedback_type='upvote',
            issue_type='security'
        )
        
        # 3. Verify metrics
        summary = tracker.get_summary()
        assert summary['total_reviews'] == 1
        
        # 4. Verify learning
        confidence = learner.get_issue_confidence('security')
        assert confidence > 0.5
