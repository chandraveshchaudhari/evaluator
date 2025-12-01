import pandas as pd
from pathlib import Path
from io import StringIO
import html as html_lib


class ReportingService:
    """
    Service for building, summarizing, and exporting grouped student evaluation reports.
    Uses instructor solution data for total marks (assert count per question).
    """

    def __init__(self, executed_results: list[dict] | None = None, solution: dict | None = None, debug: bool = False):
        self.debug = debug
        self.solution = solution or {}
        self.df: pd.DataFrame | None = self.dataframe(executed_results)

    # -------------------------------------------------------------------------
    def _get_max_scores_from_solution(self):
        """
        Returns a mapping of {question_name: number_of_assertions} from the instructor solution.
        """
        if not self.solution or "questions" not in self.solution:
            return {}

        max_scores = {}
        for qname, qdata in self.solution["questions"].items():
            tests = qdata.get("tests", [])
            max_scores[qname] = len(tests)
        return max_scores

    # -------------------------------------------------------------------------
    def dataframe(self, executed_results: list[dict] = None) -> pd.DataFrame:
        """
        Flatten all evaluation results into a DataFrame and align with instructor totals.
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
                if "description" in r:
                    row["description"] = r["description"]
                all_rows.append(row)

        df = pd.DataFrame(all_rows)
        if df.empty:
            if self.debug:
                print("Warning: Empty DataFrame in ReportingService.build()")
            self.df = pd.DataFrame()
            return self.df

        # Add max score per question using instructor data
        max_scores = self._get_max_scores_from_solution()
        df["max_score"] = df["question"].map(max_scores).fillna(1).astype(int)
        df["percentage"] = (df["score"] / df["max_score"]) * 100
        self.df = df
        return df

    # -------------------------------------------------------------------------
    def to_csv(self, path):
        if self.df is None:
            raise RuntimeError("Report not built yet.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(path, index=False)
        return path

    # -------------------------------------------------------------------------
    def to_html(self, path):
        """
        Generate an interactive HTML report:
        - Sortable by marks, name, roll
        - Scrollable summary modal
        - Totals derived from instructor notebook
        """
        if self.df is None:
            raise RuntimeError("Report not built yet.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        grouped = self.df.groupby(["file", "student", "roll_number"])
        html_out = StringIO()

        html_out.write("""
        <html><head><meta charset="UTF-8"><title>Evaluator Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            select, button { padding: 6px; font-size: 15px; margin-right: 10px; }
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

            #summaryModal {
                display: none;
                position: fixed;
                top: 10%;
                left: 50%;
                transform: translateX(-50%);
                width: 70%;
                max-height: 70vh;  /* fixed height */
                overflow-y: auto;  /* enable scrolling */
                background: white;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                z-index: 1000;
            }
            #summaryModal::-webkit-scrollbar {
                width: 10px;
            }
            #summaryModal::-webkit-scrollbar-thumb {
                background-color: #ccc;
                border-radius: 10px;
            }
            #summaryModal::-webkit-scrollbar-thumb:hover {
                background-color: #999;
            }
            #overlay {
                display: none;
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 999;
            }
            .close-btn {
                float: right;
                cursor: pointer;
                color: red;
                font-weight: bold;
            }
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
            function sortStudents() {
                const sortType = document.getElementById("sortSelect").value;
                const container = document.getElementById("reportContainer");
                const blocks = Array.from(container.getElementsByClassName("student-block"));
                blocks.sort((a, b) => {
                    const scoreA = parseFloat(a.dataset.total);
                    const scoreB = parseFloat(b.dataset.total);
                    const nameA = a.dataset.name.toLowerCase();
                    const nameB = b.dataset.name.toLowerCase();
                    const rollA = a.dataset.roll.toLowerCase();
                    const rollB = b.dataset.roll.toLowerCase();
                    switch(sortType) {
                        case "marks": return scoreB - scoreA;
                        case "name": return nameA.localeCompare(nameB);
                        case "roll": return rollA.localeCompare(rollB);
                        case "default": return nameA === "student name" ? 1 : -1;
                    }
                });
                blocks.forEach(b => container.appendChild(b));
            }
            function showSummary() {
                document.getElementById("overlay").style.display = "block";
                document.getElementById("summaryModal").style.display = "block";
            }
            function closeSummary() {
                document.getElementById("overlay").style.display = "none";
                document.getElementById("summaryModal").style.display = "none";
            }
        </script>
        </head><body>
        <h2>Evaluator Report</h2>

        <label for="sortSelect">Sort By:</label>
        <select id="sortSelect" onchange="sortStudents()">
            <option value="marks">Total Marks (High → Low)</option>
            <option value="name">Student Name (A–Z)</option>
            <option value="roll">Roll Number (A–Z)</option>
            <option value="default">Default (Student Name Last)</option>
        </select>

        <button onclick="showSummary()">Show Summary</button>

        <label for="studentSelect">Student:</label>
        <select id="studentSelect" onchange="filterReports()">
            <option value="">-- All Students --</option>
        """)

        # --- Student summaries per file ---
        summary = (
            self.df.groupby(["file", "student", "roll_number"])
            .agg(total_score=("score", "sum"), max_score=("max_score", "sum"))
            .reset_index()
        )
        summary["percentage"] = (summary["total_score"] / summary["max_score"] * 100).fillna(0)
        summary = summary.sort_values(by=["total_score", "percentage"], ascending=False).reset_index(drop=True)

        for _, row in summary.iterrows():
            student = row["student"]
            roll = row["roll_number"]
            sid = f"{student}_{roll}".replace(" ", "_")
            html_out.write(f"<option value='{sid}'>{html_lib.escape(student)} ({html_lib.escape(str(roll))})</option>")

        html_out.write("</select><hr><div id='reportContainer'>")

        # --- Individual student sections ---
        for (file, student, roll_number), g in grouped:
            sid = f"{student}_{roll_number}".replace(" ", "_")
            total_score = g["score"].sum()
            total_possible = g["max_score"].sum()
            percentage = round((total_score / total_possible) * 100, 2) if total_possible > 0 else 0.0

            html_out.write(
                f'<div class="student-block" id="{sid}" data-name="{student}" data-roll="{roll_number}" data-total="{total_score}">'
            )
            html_out.write(f"<h3>{html_lib.escape(student)} — {html_lib.escape(str(roll_number))}</h3>")
            html_out.write(f"<p><strong>File:</strong> {html_lib.escape(str(file))}</p>")
            html_out.write(f"<p class='summary'>Total: {total_score}/{total_possible} ({percentage}%)</p>")

            for q, subdf in g.groupby("question"):
                html_out.write(f'<div class="question-block" data-qname="{html_lib.escape(str(q))}">')
                html_out.write(f'<div class="question-header">Question: {html_lib.escape(str(q))}</div>')
                desc = subdf["description"].iloc[0] if "description" in subdf.columns and pd.notna(subdf["description"].iloc[0]) else ""
                if desc:
                    html_out.write(f'<div class="description">{html_lib.escape(desc)}</div>')
                html_out.write("<table><thead><tr><th>Assertion</th><th>Status</th><th>Score</th><th>Error</th></tr></thead><tbody>")
                for _, row in subdf.iterrows():
                    row_class = "passed" if row["status"] == "passed" else "failed"
                    html_out.write(
                        f"<tr class='{row_class}'><td>{html_lib.escape(str(row['assertion']))}</td>"
                        f"<td>{html_lib.escape(str(row['status']))}</td>"
                        f"<td>{row['score']}</td>"
                        f"<td>{html_lib.escape(str(row['error'])) if row['error'] else ''}</td></tr>"
                    )
                html_out.write("</tbody></table></div>")
            html_out.write("</div>")

        html_out.write("</div>")  # reportContainer end

        # --- Summary Modal ---
        html_out.write("""
        <div id="overlay" onclick="closeSummary()"></div>
        <div id="summaryModal">
            <span class="close-btn" onclick="closeSummary()">✖</span>
            <h3>Student Summary</h3>
            <table>
                <thead><tr>
                  <th>Student</th>
                  <th>Roll Number</th>
                  <th>File</th>
                  <th>Total Marks</th>
                  <th>Out of</th>
                  <th>Percentage</th>
                </tr></thead>
                <tbody>
        """)
        for _, row in summary.iterrows():
            html_out.write(
                f"<tr><td>{html_lib.escape(row['student'])}</td>"
                f"<td>{html_lib.escape(str(row['roll_number']))}</td>"
                f"<td>{html_lib.escape(Path(row['file']).name)}</td>"
                f"<td>{row['total_score']}</td>"
                f"<td>{row['max_score']}</td>"
                f"<td>{round(row['percentage'], 2)}%</td></tr>"
            )

        html_out.write("</tbody></table></div></body></html>")
        path.write_text(html_out.getvalue(), encoding="utf8")
        return path
