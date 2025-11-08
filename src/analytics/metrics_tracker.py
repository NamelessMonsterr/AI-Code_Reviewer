import json, os
from datetime import datetime

class MetricsTracker:
    def __init__(self, data_file='review_metrics.json'):
        self.data_file = data_file
    def record_review(self, pr:int, issues:int, langs:list, review_time:float):
        metrics = {"pr": pr, "issues": issues, "langs": langs, "time": review_time, "ts": datetime.now().isoformat()}
        arr = []
        if os.path.exists(self.data_file):
            arr = json.load(open(self.data_file))
        arr.append(metrics)
        with open(self.data_file,'w') as f: json.dump(arr, f)
