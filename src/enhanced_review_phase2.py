import os
from feedback.feedback_learner import FeedbackLearner
from integrations.ide_integration import IDEIntegration
from integrations.platform_support import PlatformSupport
from rules.custom_rules_engine import CustomRulesEngine
from models.model_selector import ModelSelector, ModelProvider


class EnhancedReviewPhase2:
    """Phase 2 enhanced review with learning and integrations"""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.feedback_learner = FeedbackLearner()
        self.rules_engine = CustomRulesEngine()
        self.model_selector = ModelSelector()

    def run_intelligent_review(self, file_content: str, language: str) -> str:
        """Run review with learned patterns and custom rules"""

        # Apply custom rules
        rule_violations = self.rules_engine.apply_all_rules(file_content, language)

        # Select appropriate model
        model_config = self.model_selector.select_model("code_review", len(file_content))

        # Filter issues based on learned feedback
        filtered_issues = []
        for violation in rule_violations.get("naming_violations", []):
            if self.feedback_learner.should_report_issue("naming_violation"):
                filtered_issues.append(violation)

        # Generate review comment
        comment = "## 🤖 AI Code Review (Phase 2)\\n\\n"
        comment += f"**Model Used**: {model_config['model']}\\n\\n"

        if filtered_issues:
            comment += "### Custom Rule Violations\\n"
            for issue in filtered_issues:
                confidence = self.feedback_learner.get_issue_confidence(issue["type"])
                comment += f"- {issue['message']} (Confidence: {confidence:.2f})\\n"

        return comment


if __name__ == "__main__":
    reviewer = EnhancedReviewPhase2(".")
    print("Phase 2 Review Complete")
