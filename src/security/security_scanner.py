import subprocess, json, os, re
from typing import Dict, List

class SecurityScanner:
    def scan_with_bandit(self, file_path: str) -> List[Dict]:
        try:
            result = subprocess.run(
                ['bandit', '-r', file_path, '-f', 'json'],
                capture_output=True, text=True
            )
            if result.returncode == 0 or result.stdout:
                data = json.loads(result.stdout)
                return [{"severity": d.get('severity'), "message": d.get('issue_text'), "line": d.get('line_number')}
                        for d in data.get("results",[])]
        except Exception as e:
            return [{'error': f'Bandit scan failed: {str(e)}'}]
        return []

    def detect_secrets(self, file_path: str) -> List[Dict]:
        patterns = {'api_key': r'api[_-]?key\s*[=:]\s*[\'\"]([a-zA-Z0-9\-_]{20,})[\'\"]'}
        secrets = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    for k, pat in patterns.items():
                        if re.search(pat, line):
                            secrets.append({"type": "secret", "line": line_num, "detail": k})
        except Exception as e:
            return [{'error': f'Secret scan failed: {str(e)}'}]
        return secrets

    def scan_dependencies(self, repo_path: str) -> List[Dict]:
        vulns = []
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            try:
                result = subprocess.run(['npm', 'audit', '--json'], cwd=repo_path, capture_output=True, text=True)
                data = json.loads(result.stdout)
                for k,v in data.get("vulnerabilities",{}).items():
                    vulns.append({"package": k, "severity": v.get("severity")})
            except: pass
        return vulns

    def generate_security_report(self, repo_path: str) -> Dict:
        return {
            'bandit': self.scan_with_bandit(repo_path),
            'secrets': self.detect_secrets(repo_path),
            'dependencies': self.scan_dependencies(repo_path)
        }
