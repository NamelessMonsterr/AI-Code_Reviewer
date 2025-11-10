import os
import time
from security.security_scanner import SecurityScanner
from languages.language_detector import LanguageDetector
from autofix.code_fixer import CodeFixer
from analytics.metrics_tracker import MetricsTracker


class EnhancedReview:
    def run(self, repo):
        ld = LanguageDetector()
        sc = SecurityScanner()
        cf = CodeFixer()
        mt = MetricsTracker()
        langs = list(ld.detect_languages_in_repo(repo).keys())
        report = sc.generate_security_report(repo)
        # Basic example fix -- integrate as needed
        # fix = cf.generate_fix(some_code, some_issue, langs[0])
        mt.record_review(1, len(report.get("bandit", [])), langs, 0.1)
        print(report)


if __name__ == "__main__":
    EnhancedReview().run(".")
