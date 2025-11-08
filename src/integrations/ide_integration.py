import requests
import json
from typing import Dict, List

class IDEIntegration:
    """Integration with VS Code, JetBrains IDEs"""
    
    def __init__(self, api_endpoint='http://localhost:8080'):
        self.api_endpoint = api_endpoint
    
    # VS Code Extension API
    def vscode_review_file(self, file_path: str, content: str) -> Dict:
        """Real-time review for VS Code"""
        payload = {
            'file_path': file_path,
            'content': content,
            'action': 'review'
        }
        response = requests.post(f'{self.api_endpoint}/vscode/review', json=payload)
        return response.json()
    
    def vscode_inline_suggestions(self, file_path: str, line: int, code: str) -> List[Dict]:
        """Get inline suggestions for current line"""
        payload = {'file_path': file_path, 'line': line, 'code': code}
        response = requests.post(f'{self.api_endpoint}/vscode/suggestions', json=payload)
        return response.json().get('suggestions', [])
    
    # CLI Tool
    def cli_review(self, repo_path: str, files: List[str] = None) -> Dict:
        """Command-line interface review"""
        from security.security_scanner import SecurityScanner
        from languages.language_detector import LanguageDetector
        
        scanner = SecurityScanner()
        detector = LanguageDetector()
        
        languages = detector.detect_languages_in_repo(repo_path)
        security_report = scanner.generate_security_report(repo_path)
        
        return {
            'languages': languages,
            'security': security_report,
            'status': 'complete'
        }
    
    # Pre-commit Hook
    def generate_pre_commit_hook(self) -> str:
        """Generate pre-commit hook script"""
        hook_script = """#!/bin/bash
# AI Code Review Pre-commit Hook

echo "Running AI code review..."

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

# Run review
python -m src.integrations.ide_integration cli-review . "$STAGED_FILES"

if [ $? -ne 0 ]; then
    echo "Code review found issues. Fix them before committing."
    exit 1
fi

echo "Code review passed!"
exit 0
"""
        return hook_script
    
    def install_pre_commit_hook(self, repo_path: str):
        """Install pre-commit hook in repository"""
        import os
        hook_path = os.path.join(repo_path, '.git', 'hooks', 'pre-commit')
        with open(hook_path, 'w') as f:
            f.write(self.generate_pre_commit_hook())
        os.chmod(hook_path, 0o755)  # Make executable
