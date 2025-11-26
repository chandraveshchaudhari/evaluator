import pandas as pd
from pathlib import Path
from io import StringIO
import html as html_lib


class ReportingService:
    """
    Service for building, summarizing, and exporting grouped student evaluation reports.
    """

    def __init__(self, executed_results: list[dict] | None = None, debug: bool = False):
        self.debug = debug
        self.df: pd.DataFrame | None = self.dataframe(executed_results)

    # -------------------------------------------------------------------------
    def dataframe(self, executed_results: list[dict] = None) -> pd.DataFrame:
        """
        Flatten all evaluation results into a DataFrame.
        """
        all_rows = []
        for item in executed_results or []:
            student_path = Path(item.get("student_path", ""))
            results = item.get("results", [])
            ns = item.get("execution", {}).get("namespace", {})
            student_name = ns.get("name") or student_path.stem
            roll_no = ns.get("roll_number") or "N/A"

            for r in results:
                row = {
                    "file": str(student_path),
                    "student": student_name,
                    "roll_number": roll_no,
                    "question": r.get("question"),
                    "assertion": r.get("assertion"),
                    "status": r.get("status"),
                    "score": r.get("score"),
                    "error": r.get("error"),
                }
                # Optional: if instructor provided descriptions (safe fallback)
                if "description" in r:
                    row["description"] = r["description"]
                all_rows.append(row)

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
        - Grouped by file/student/roll_number
        - Nested grouping by question
        - Includes question descriptions (if available)
        - Two dropdowns: filter by student and question
        - Displays total marks summary per student
        """
        if self.df is None:
            raise RuntimeError("Report not built yet. Call build() first.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        grouped = self.df.groupby(["file", "student", "roll_number"])
        html_out = StringIO()

        html_out.write("""
        <html><head><meta charset="UTF-8"><title>Evaluator Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            select { padding: 6px; font-size: 15px; margin-right: 10px; }
            table { border-collapse: collapse; width: 100%; margin-top: 10px; }
            th, td { border: 1px solid #ccc; padding: 6px; text-align: left; }
            th { background: #f2f2f2; }
            tr:nth-child(even) { background: #fafafa; }
            .student-block { margin-top: 40px; border: 1px solid #ddd; padding: 15px; border-radius: 6px; }
            .question-header { font-weight: bold; margin-top: 15px; font-size: 1.05em; color: #333; }
            .description { color: #555; margin-bottom: 10px; font-style: italic; }
            .passed { background-color: #e6ffe6; }
            .failed { background-color: #ffe6e6; }
            .summary { margin-top: 5px; font-weight: bold; color: #333; }
            .hidden { display: none; }
        </style>
        <script>
            function filterReports() {
                const studentVal = document.getElementById("studentSelect").value;
                const questionVal = document.getElementById("questionSelect").value;

                document.querySelectorAll(".student-block").forEach(div => {
                    const showStudent = (studentVal === "" || div.id === studentVal);
                    div.style.display = showStudent ? "block" : "none";

                    if (showStudent) {
                        div.querySelectorAll(".question-block").forEach(qb => {
                            qb.style.display = (questionVal === "" || qb.dataset.qname === questionVal) ? "block" : "none";
                        });
                    }
                });
            }
        </script>
        </head><body>
        <h2>Evaluator Report</h2>
        <label for="studentSelect">Student:</label>
        <select id="studentSelect" onchange="filterReports()">
            <option value="">-- All Students --</option>
        """)

        # Student dropdown
        student_ids = []
        for (file, student, roll) in grouped.groups.keys():
            sid = f"{student}_{roll}".replace(" ", "_")
            student_ids.append(sid)
            html_out.write(f"<option value='{sid}'>{html_lib.escape(student)} ({html_lib.escape(str(roll))})</option>")
        html_out.write("</select>")

        # Question dropdown
        html_out.write('<label for="questionSelect">Question:</label><select id="questionSelect" onchange="filterReports()">')
        html_out.write("<option value=''>-- All Questions --</option>")
        all_questions = list(dict.fromkeys(self.df["question"]))
        for q in all_questions:
            html_out.write(f"<option value='{html_lib.escape(str(q))}'>{html_lib.escape(str(q))}</option>")
        html_out.write("</select><hr>")

        # Student-wise rendering
        for (file, student, roll_number), g in grouped:
            sid = f"{student}_{roll_number}".replace(" ", "_")
            html_out.write(f'<div class="student-block" id="{sid}">')
            html_out.write(f"<h3>{html_lib.escape(student)} — {html_lib.escape(str(roll_number))}</h3>")
            html_out.write(f"<p><strong>File:</strong> {html_lib.escape(str(file))}</p>")

            total_score = g["score"].sum()
            total_possible = g["max_score"].sum()
            percentage = round((total_score / total_possible) * 100, 2) if total_possible > 0 else 0.0
            html_out.write(f"<p class='summary'>Total: {total_score}/{total_possible} ({percentage}%)</p>")

            # Preserve order from notebook
            unique_questions = list(dict.fromkeys(g["question"]))

            for q in unique_questions:
                subdf = g[g["question"] == q]
                html_out.write(f'<div class="question-block" data-qname="{html_lib.escape(str(q))}">')
                html_out.write(f'<div class="question-header">Question: {html_lib.escape(str(q))}</div>')

                # Optional description support
                desc = subdf["description"].iloc[0] if "description" in subdf.columns and pd.notna(subdf["description"].iloc[0]) else ""
                if desc:
                    html_out.write(f'<div class="description">{html_lib.escape(desc)}</div>')

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
                html_out.write("</tbody></table></div>")  # close question-block

            html_out.write("</div>")  # close student-block

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
