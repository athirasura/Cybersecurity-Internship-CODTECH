"""
reporter.py
Output logging for toolkit runs. Saves results to JSON and/or CSV so each
assessment produces a tangible, timestamped artefact.
"""

import json
import csv
import os
from datetime import datetime


class Reporter:
    def __init__(self, target, outdir="reports"):
        self.target = target
        self.outdir = outdir
        self.timestamp = datetime.now()
        os.makedirs(outdir, exist_ok=True)

    def _basename(self, module):
        stamp = self.timestamp.strftime("%Y%m%d_%H%M%S")
        safe_target = self.target.replace(".", "-").replace(":", "-")
        return os.path.join(self.outdir, f"{module}_{safe_target}_{stamp}")

    def save_json(self, module, data):
        path = f"{self._basename(module)}.json"
        report = {
            "module": module,
            "target": self.target,
            "timestamp": self.timestamp.isoformat(),
            "results": data,
        }
        with open(path, "w") as fh:
            json.dump(report, fh, indent=2)
        print(f"[*] JSON report saved: {path}")
        return path

    def save_csv(self, module, rows, header):
        path = f"{self._basename(module)}.csv"
        with open(path, "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            writer.writerows(rows)
        print(f"[*] CSV report saved:  {path}")
        return path
