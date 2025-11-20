"""
Result dataclasses for standardized evaluator output.
"""
import pandas as pd
from pathlib import Path

class ReportBuilder:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def show(self):
        """Return the DataFrame for immediate viewing."""
        return self.df

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
        path.write_text(self.df.to_string(index=False), encoding="utf8")
        return path

    def summary(self):
        """Return a high-level summary as dictionary."""
        return {
            "total_tests": len(self.df),
            "passed": int(self.df["score"].sum()),
            "failed": int((1 - self.df["score"]).sum()),
            "percentage": float(self.df["percentage"].mean()),
        }
