import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MetricsTracker:
    """Track and analyze code review metrics"""

    def __init__(self, data_file: str = "review_metrics.json", data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path("data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / data_file
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure metrics file exists"""
        if not self.data_file.exists():
            self.data_file.write_text("[]")

    def record_review(
        self,
        pr: int,
        issues: int,
        langs: List[str],
        review_time: float,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Record a code review with metrics"""
        try:
            metrics = {
                "pr": pr,
                "issues": issues,
                "languages": langs,
                "review_time": review_time,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
            }

            # Load existing data
            data = self._load_data()
            data.append(metrics)

            # Save updated data
            self._save_data(data)
            logger.info(f"Recorded review for PR #{pr}")

        except Exception as e:
            logger.error(f"Failed to record review: {str(e)}")
            raise

    def _load_data(self) -> List[Dict]:
        """Load metrics data from file"""
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in metrics file, resetting")
            return []
        except Exception as e:
            logger.error(f"Error loading metrics: {str(e)}")
            return []

    def _save_data(self, data: List[Dict]) -> None:
        """Save metrics data to file"""
        try:
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")
            raise

    def get_summary(self) -> Dict:
        """Get summary statistics"""
        try:
            data = self._load_data()

            if not data:
                return self._empty_summary()

            total_reviews = len(data)
            total_issues = sum(r["issues"] for r in data)
            total_time = sum(r["review_time"] for r in data)
            avg_time = total_time / total_reviews if total_reviews > 0 else 0

            # Get most common languages
            lang_counts = {}
            for review in data:
                for lang in review["languages"]:
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1

            top_languages = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                "total_reviews": total_reviews,
                "total_issues": total_issues,
                "avg_review_time": round(avg_time, 2),
                "total_time_saved": round(total_time, 2),
                "top_languages": [lang for lang, _ in top_languages],
            }
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return self._empty_summary()

    def _empty_summary(self) -> Dict:
        """Return empty summary structure"""
        return {
            "total_reviews": 0,
            "total_issues": 0,
            "avg_review_time": 0,
            "total_time_saved": 0,
            "top_languages": [],
        }
