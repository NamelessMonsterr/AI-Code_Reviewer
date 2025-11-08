import pytest
from src.feedback.feedback_learner import FeedbackLearner

class TestFeedbackLearner:
    
    @pytest.fixture
    def learner(self, test_data_dir):
        """Create FeedbackLearner instance"""
        return FeedbackLearner(
            feedback_file='test_feedback.json',
            data_dir=str(test_data_dir)
        )
    
    def test_record_feedback(self, learner):
        """Test recording feedback"""
        learner.record_feedback(
            review_id='rev_123',
            comment_id='com_456',
            feedback_type='upvote',
            issue_type='security'
        )
        
        assert len(learner.feedback_data['reviews']) == 1
        assert learner.feedback_data['reviews'][0]['feedback_type'] == 'upvote'
    
    def test_invalid_feedback_type(self, learner):
        """Test invalid feedback type raises error"""
        with pytest.raises(ValueError):
            learner.record_feedback(
                review_id='rev_123',
                comment_id='com_456',
                feedback_type='invalid',
                issue_type='security'
            )
    
    def test_confidence_calculation(self, learner):
        """Test confidence score calculation"""
        # Record positive feedback
        for _ in range(8):
            learner.record_feedback('rev_1', 'com_1', 'upvote', 'security')
        
        # Record negative feedback
        for _ in range(2):
            learner.record_feedback('rev_2', 'com_2', 'downvote', 'security')
        
        confidence = learner.get_issue_confidence('security')
        assert confidence > 0.5  # More positive than negative
    
    def test_should_report_issue(self, learner):
        """Test issue reporting decision"""
        # High confidence issue
        for _ in range(10):
            learner.record_feedback('rev_1', 'com_1', 'upvote', 'critical')
        
        assert learner.should_report_issue('critical', threshold=0.3)
        
        # Low confidence issue
        for _ in range(10):
            learner.record_feedback('rev_2', 'com_2', 'downvote', 'style')
        
        assert not learner.should_report_issue('style', threshold=0.7)
    
    def test_feedback_summary(self, learner):
        """Test feedback summary generation"""
        learner.record_feedback('rev_1', 'com_1', 'upvote', 'security')
        learner.record_feedback('rev_2', 'com_2', 'accept', 'security')
        learner.record_feedback('rev_3', 'com_3', 'downvote', 'security')
        
        summary = learner.get_feedback_summary()
        
        assert 'security' in summary
        assert summary['security']['total_feedback'] == 3
        assert 0 <= summary['security']['confidence'] <= 1
        assert 0 <= summary['security']['approval_rate'] <= 1
