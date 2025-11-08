from training.model_finetuner import ModelFineTuner
from intelligence.bug_pattern_learner import BugPatternLearner
from intelligence.pattern_recognizer import CodingPatternRecognizer
from intelligence.severity_scorer import SeverityScorer
from intelligence.knowledge_base import KnowledgeBase

class EnhancedReviewPhase5:
    """Phase 5 AI Training & Intelligence"""
    
    def __init__(self):
        self.finetuner = ModelFineTuner()
        self.bug_learner = BugPatternLearner()
        self.pattern_recognizer = CodingPatternRecognizer()
        self.severity_scorer = SeverityScorer()
        self.knowledge_base = KnowledgeBase()
        
        # Load historical data
        self.bug_learner.load_patterns()
        self.knowledge_base.load_knowledge()
    
    def intelligent_review(self, code: str, file_path: str, language: str) -> Dict:
        """Run intelligent review with learning"""
        
        # Predict potential bugs
        bug_predictions = self.bug_learner.predict_bug_probability(code, file_path)
        
        # Check coding pattern consistency
        pattern_violations = self.pattern_recognizer.check_consistency(code)
        
        # Get knowledge base recommendations
        kb_recommendations = self.knowledge_base.get_recommendations_for_code(code, language)
        
        # Calculate severity for all issues
        all_issues = pattern_violations + kb_recommendations
        for issue in all_issues:
            severity = self.severity_scorer.calculate_severity(issue)
            issue['severity'] = severity
        
        return {
            'bug_predictions': bug_predictions,
            'pattern_violations': pattern_violations,
            'kb_recommendations': kb_recommendations,
            'issues_with_severity': all_issues,
            'risk_score': bug_predictions['risk_score']
        }
    
    def train_on_feedback(self, review_id: str, code: str, 
                         review: str, user_feedback: Dict):
        """Train model on user feedback"""
        
        # Collect for fine-tuning
        self.finetuner.collect_training_data({
            'code': code,
            'review_comments': review
        })
        
        # Learn severity preferences
        if 'severity_correction' in user_feedback:
            for issue in user_feedback['issues']:
                self.severity_scorer.learn_from_feedback(
                    issue,
                    user_feedback['severity_correction']
                )
    
    def start_model_training(self) -> str:
        """Start fine-tuning process"""
        # Prepare and upload training data
        training_file = self.finetuner.prepare_training_file()
        file_id = self.finetuner.upload_training_file(training_file)
        
        # Start fine-tuning
        job_id = self.finetuner.start_fine_tuning(file_id)
        
        return f"Fine-tuning job started: {job_id}"

if __name__ == "__main__":
    reviewer = EnhancedReviewPhase5()
    print("Phase 5 AI Training & Intelligence Ready")
