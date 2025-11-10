import os


class LanguageDetector:
    EXTENSIONS = {"python": [".py"], "js": [".js", ".jsx"], "java": [".java"]}

    def detect_languages_in_repo(self, repo_path: str):
        count = {}
        for root, dirs, files in os.walk(repo_path):
            for f in files:
                for l, exts in self.EXTENSIONS.items():
                    if any(f.endswith(e) for e in exts):
                        count[l] = count.get(l, 0) + 1
        return count
