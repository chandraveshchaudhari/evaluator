"""
Builds student reports from evaluation results.
"""
from evaluator.reporting.report_builder import ReportBuilder

class ReportingService:
    def build(self, comparison_results):
        return ReportBuilder(comparison_results)




import json
import csv
from pathlib import Path
import pandas as pd
from pathlib import Path
from evaluator.reporting.results import Results

class ReportBuilder:
    def __init__(self, comparison_dict=None):
        """
        comparison_dict is a list of dictionaries or a dict-of-dicts returned by comparison module.
        """
        self.data = comparison_dict if comparison_dict else Results().report_data()

    # --- VIEWING ---
    def show(self):
        return pd.DataFrame(self.data)

    # --- EXPORTS ---
    def to_csv(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(path, index=False)
        return path

    def to_html(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        html = self.df.to_html(index=False)
        path.write_text(html, encoding="utf8")
        return path

    def to_log(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf8") as f:
            f.write(self.df.to_string(index=False))
        return path



# def build_json_report(result: Dict[str, Any], out_path: str) -> str:
#     """Write result dict as JSON to out_path and return the path."""
#     os.makedirs(os.path.dirname(out_path), exist_ok=True)
#     with open(out_path, "w", encoding="utf8") as f:
#         json.dump(result, f, indent=2, ensure_ascii=False)
#     return out_path


# def build_csv_summary(rows: list[Dict[str, Any]], out_path: str) -> str:
#     """Write a list of per-student summary rows (dicts) to a CSV file."""
#     if not rows:
#         raise ValueError("rows must not be empty")
#     os.makedirs(os.path.dirname(out_path), exist_ok=True)
#     fieldnames = list(rows[0].keys())
#     with open(out_path, "w", newline="", encoding="utf8") as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         for r in rows:
#             writer.writerow(r)
#     return out_path

# clean_df.to_csv(f"{assignment_number} Metrics.csv", index = False)
