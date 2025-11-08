import pytest
from src.analytics.metrics_tracker import MetricsTracker

class TestMetricsTracker:
    
    @pytest.fixture
    def tracker(self, test_data_dir):
        """Create MetricsTracker instance"""
        return MetricsTracker(
            data_file='test_metrics.json',
            data_dir=str(test_data_dir)
        )
    
    def test_record_review(self, tracker):
        """Test recording a review"""
        tracker.record_review(
            pr=123,
            issues=5,
            langs=['python', 'javascript'],
            review_time=45.5
        )
        
        summary = tracker.get_summary()
        assert summary['total_reviews'] == 1
        assert summary['total_issues'] == 5
    
    def test_summary_calculation(self, tracker):
        """Test summary statistics"""
        tracker.record_review(pr=1, issues=5, langs=['python'], review_time=30.0)
        tracker.record_review(pr=2, issues=3, langs=['python'], review_time=20.0)
        tracker.record_review(pr=3, issues=7, langs=['javascript'], review_time=40.0)
        
        summary = tracker.get_summary()
        
        assert summary['total_reviews'] == 3
        assert summary['total_issues'] == 15
        assert summary['avg_review_time'] == 30.0
        assert 'python' in summary['top_languages']
    
    def test_empty_summary(self, tracker):
        """Test summary with no data"""
        summary = tracker.get_summary()
        
        assert summary['total_reviews'] == 0
        assert summary['total_issues'] == 0
        assert summary['avg_review_time'] == 0
