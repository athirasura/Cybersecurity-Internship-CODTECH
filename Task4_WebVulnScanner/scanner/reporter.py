"""
reporter.py
Saves scan findings to JSON and CSV, and prints a readable summary.
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

    def _basename(self):
        stamp = self.timestamp.strftime("%Y%m%d_%H%M%S")
        safe = self.target.replace("http://", "").replace("https://", "")
        safe = safe.replace("/", "_").replace(":", "-").replace(".", "-")
        return os.path.join(self.outdir, f"scan_{safe}_{stamp}")

    def summary(self, findings):
        print("\n" + "=" * 60)
        print(f"  SCAN SUMMARY — {self.target}")
        print("=" * 60)
        if not findings:
            print("  No issues detected.")
            return
        by_sev = {"High": [], "Medium": [], "Low": []}
        for f in findings:
            by_sev.setdefault(f["severity"], []).append(f)
        for sev in ("High", "Medium", "Low"):
            items = by_sev.get(sev, [])
            if items:
                print(f"\n  [{sev}] {len(items)} finding(s):")
                for f in items:
                    print(f"    - {f['type']} @ {f['location']} ({f['method']})")
        print("=" * 60 + "\n")

    def save(self, findings):
        base = self._basename()
        report = {
            "target": self.target,
            "timestamp": self.timestamp.isoformat(),
            "total_findings": len(findings),
            "findings": findings,
        }
        with open(f"{base}.json", "w") as fh:
            json.dump(report, fh, indent=2)
        print(f"[*] JSON report saved: {base}.json")

        if findings:
            keys = ["type", "severity", "location", "method", "payload", "evidence"]
            with open(f"{base}.csv", "w", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=keys)
                writer.writeheader()
                for f in findings:
                    writer.writerow({k: f.get(k, "") for k in keys})
            print(f"[*] CSV report saved:  {base}.csv")
