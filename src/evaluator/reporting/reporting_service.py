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
        - Preserves question order from notebook
        - Shows total marks summary per student
        - Searchable dropdown
        """
        import html as html_lib  # avoid naming conflict
        from io import StringIO

        if self.df is None:
            raise RuntimeError("Report not built yet. Call build() first.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        grouped = self.df.groupby(["file", "student", "roll_number"])
        html_out = StringIO()

        # Header
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
            .passed { background-color: #e6ffe6; }
            .failed { background-color: #ffe6e6; }
            .summary { margin-top: 5px; font-weight: bold; color: #333; }
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

        # Dropdown menu
        for (file, student, roll) in grouped.groups.keys():
            opt_id = f"{student}_{roll}".replace(" ", "_")
            html_out.write(
                f'<option value="{opt_id}">{html_lib.escape(student)} ({html_lib.escape(str(roll))})</option>'
            )

        html_out.write("</select><hr>")

        # Student-wise blocks
        for (file, student, roll_number), g in grouped:
            block_id = f"{student}_{roll_number}".replace(" ", "_")
            html_out.write(f'<div class="student-block" id="{block_id}">')
            html_out.write(f"<h3>{html_lib.escape(student)} — {html_lib.escape(str(roll_number))}</h3>")
            html_out.write(f"<p><strong>File:</strong> {html_lib.escape(str(file))}</p>")

            # --- Summary section (total marks) ---
            total_score = g["score"].sum()
            total_possible = g["max_score"].sum()
            percentage = round((total_score / total_possible) * 100, 2) if total_possible > 0 else 0.0
            html_out.write(f"<p class='summary'>Score: {total_score} / {total_possible} ({percentage}%)</p>")

            # Preserve original question order
            unique_questions = list(dict.fromkeys(g["question"]))

            for q in unique_questions:
                subdf = g[g["question"] == q]
                html_out.write(f'<div class="question-header">Question: {html_lib.escape(str(q))}</div>')
                html_out.write(
                    "<table><thead><tr><th>Assertion</th><th>Status</th><th>Score</th><th>Error</th></tr></thead><tbody>"
                )
                for _, row in subdf.iterrows():
                    row_class = "passed" if row["status"] == "passed" else "failed"
                    html_out.write(
                        f"<tr class='{row_class}'><td>{html_lib.escape(str(row['assertion']))}</td>"
                        f"<td>{html_lib.escape(str(row['status']))}</td>"
                        f"<td>{row['score']}</td>"
                        f"<td>{html_lib.escape(str(row['error'])) if row['error'] else ''}</td></tr>"
                    )
                html_out.write("</tbody></table>")

            html_out.write("</div>")  # end student block

        html_out.write("</body></html>")

        html_str = html_out.getvalue()
        path.write_text(html_str, encoding="utf8")
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
