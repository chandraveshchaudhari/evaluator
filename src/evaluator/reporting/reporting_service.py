import pandas as pd
from pathlib import Path

import pandas as pd
from pathlib import Path
from io import StringIO


class ReportingService:
    """
    Service for building, summarizing, and exporting grouped student evaluation reports.
    """

    def __init__(self, executed_results: list[dict] | None = None, debug: bool = False):
        self.data = executed_results if executed_results else []
        self.debug = debug
        self.df: pd.DataFrame | None = self.dataframe(executed_results)

    # -------------------------------------------------------------------------
    def dataframe(self, executed_results: list[dict] = None) -> pd.DataFrame:
        """
        Flatten all evaluation results into a DataFrame.
        """
        executed_results = executed_results or self.data
        all_rows = []

        for item in executed_results:
            student_path = Path(item.get("student_path", ""))
            results = item.get("results", [])
            ns = item.get("execution", {}).get("namespace", {})
            student_name = ns.get("name") or student_path.stem
            roll_no = ns.get("roll_number") or "N/A"

            for r in results:
                all_rows.append({
                    "file": str(student_path),
                    "student": student_name,
                    "roll_number": roll_no,
                    "question": r.get("question"),
                    "assertion": r.get("assertion"),
                    "status": r.get("status"),
                    "score": r.get("score"),
                    "error": r.get("error"),
                })

        df = pd.DataFrame(all_rows)

        if df.empty:
            if self.debug:
                print("Warning: Empty DataFrame in ReportingService.build()")
            self.df = pd.DataFrame()
            return self.df

        df["max_score"] = 1
        df["percentage"] = (df["score"] / df["max_score"]) * 100
        self.df = df
        return df

    # -------------------------------------------------------------------------
    def to_csv(self, path):
        if self.df is None:
            raise RuntimeError("Report not built yet. Call build() first.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(path, index=False)
        return path

    # -------------------------------------------------------------------------
    def to_html(self, path):
        """
        Produce a grouped interactive HTML report:
          - Top-level grouping by file/student/roll_number
          - Nested tables by question
          - Searchable student dropdown
        """
        if self.df is None:
            raise RuntimeError("Report not built yet. Call build() first.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        grouped = self.df.groupby(["file", "student", "roll_number"])
        html_out = StringIO()

        # HTML Header
        html_out.write("""
        <html><head><meta charset="UTF-8"><title>Evaluator Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            select { padding: 6px; font-size: 15px; }
            table { border-collapse: collapse; width: 100%; margin-top: 10px; }
            th, td { border: 1px solid #ccc; padding: 6px; text-align: left; }
            th { background: #f2f2f2; }
            tr:nth-child(even) { background: #fafafa; }
            .student-block { margin-top: 40px; border: 1px solid #ddd; padding: 15px; border-radius: 6px; }
            .question-header { font-weight: bold; margin-top: 15px; }
        </style>
        <script>
            function showStudent() {
                const selected = document.getElementById("studentSelect").value;
                document.querySelectorAll(".student-block").forEach(div => {
                    div.style.display = div.id === selected || selected === "" ? "block" : "none";
                });
            }
        </script>
        </head><body>
        <h2>Evaluator Student Report</h2>
        <label for="studentSelect">Filter by student:</label>
        <select id="studentSelect" onchange="showStudent()">
            <option value="">-- Show All Students --</option>
        """)

        # Dropdown
        for (file, student, roll) in grouped.groups.keys():
            opt_id = f"{student}_{roll}".replace(" ", "_")
            html_out.write(f'<option value="{opt_id}">{html.escape(student)} ({html.escape(str(roll))})</option>')

        html_out.write("</select><hr>")

        # Grouped content
        for (file, student, roll_number), g in grouped:
            block_id = f"{student}_{roll_number}".replace(" ", "_")
            html_out.write(f'<div class="student-block" id="{block_id}">')
            html_out.write(f"<h3>{html.escape(student)} — {html.escape(str(roll_number))}</h3>")
            html_out.write(f"<p><strong>File:</strong> {html.escape(str(file))}</p>")

            for q, subdf in g.groupby("question"):
                html_out.write(f'<div class="question-header">Question: {html.escape(str(q))}</div>')
                html_out.write("<table><thead><tr><th>Assertion</th><th>Status</th><th>Score</th><th>Error</th></tr></thead><tbody>")
                for _, row in subdf.iterrows():
                    html_out.write(f"<tr><td>{html.escape(str(row['assertion']))}</td>"
                                   f"<td>{html.escape(str(row['status']))}</td>"
                                   f"<td>{row['score']}</td>"
                                   f"<td>{html.escape(str(row['error'])) if row['error'] else ''}</td></tr>")
                html_out.write("</tbody></table>")

            html_out.write("</div>")  # end student block

        html_out.write("</body></html>")

        html = html_out.getvalue()
        path.write_text(html, encoding="utf8")
        return path

    # -------------------------------------------------------------------------
    def to_log(self, path):
        if self.df is None:
            raise RuntimeError("Report not built yet. Call build() first.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.df.to_string(index=False), encoding="utf8")
        return path

    # -------------------------------------------------------------------------
    def summary(self):
        if self.df is None:
            raise RuntimeError("Report not built yet. Call build() first.")
        return {
            "total_tests": len(self.df),
            "passed": int(self.df["score"].sum()),
            "failed": int((1 - self.df["score"]).sum()),
            "percentage": float(self.df["percentage"].mean()),
        }
