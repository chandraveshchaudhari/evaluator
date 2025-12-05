import pandas as pd
from pathlib import Path
from io import StringIO
import html as html_lib


class ReportingService:
    """
    Service for building, summarizing, and exporting grouped student evaluation reports.
    Uses total_assertions (from instructor notebook) for total marks.
    """

    def __init__(
        self,
        executed_results: list[dict] | None = None,
        solution: dict | None = None,
        debug: bool = False,
        logger=None,
        total_assertions: int = 0,
    ):
        self.debug = debug
        self.solution = solution or {}
        self.executed_results = executed_results or []
        self.logger = logger
        self.total_assertions = total_assertions or 1  # avoid division by zero
        self.df: pd.DataFrame | None = self.dataframe(self.executed_results)

        if self.logger:
            self.logger.info(f"[Reporting] Processed {len(self.df)} result rows.")

    # -------------------------------------------------------------------------
    def dataframe(self, executed_results: list[dict] = None) -> pd.DataFrame:
        """Flatten all evaluation results into a DataFrame."""
        all_rows = []
        for item in executed_results or []:
            student_path = Path(item.get("student_path", ""))
            results = item.get("results", [])
            ns = item.get("execution", {}).get("namespace", {})
            meta = item.get("execution", {}).get("student_meta", {})

            student_name = (
                meta.get("name")
                or ns.get("name")
                or student_path.stem
            )
            roll_no = (
                meta.get("roll_number")
                or ns.get("roll_number")
                or "N/A"
            )

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
                    "description": r.get("description", ""),
                }
                all_rows.append(row)

        df = pd.DataFrame(all_rows)
        if df.empty:
            if self.debug:
                print("Warning: Empty DataFrame in ReportingService.build()")
            self.df = pd.DataFrame()
            return self.df

        # Each assertion counts as 1 mark
        df["max_score"] = 1
        df["total_possible"] = self.total_assertions
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
        """Generate an interactive HTML report with filters."""
        if self.df is None:
            raise RuntimeError("Report not built yet.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        df = self.df.copy()
        # Include all rows for DataFrame completeness
        df_filtered = df.copy()

        # Filter out missing-identity rows for name/roll dropdowns and summary only
        df_summary = df[df["assertion"] != "[missing student identity]"].copy()

        grouped = df_filtered.groupby(["file", "student", "roll_number"])
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

            #summaryModal {
                display: none;
                position: fixed;
                top: 10%;
                left: 50%;
                transform: translateX(-50%);
                width: 70%;
                max-height: 70vh;
                overflow-y: auto;
                background: white;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                z-index: 1000;
            }
            #overlay {
                display: none;
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 999;
            }
            .close-btn { float: right; cursor: pointer; color: red; font-weight: bold; }
        </style>
        <script>
            function filterReports() {
                const studentVal = document.getElementById("studentSelect").value;
                const rollVal = document.getElementById("rollSelect").value;
                const fileVal = document.getElementById("fileSelect").value;
                document.querySelectorAll(".student-block").forEach(div => {
                    const name = div.dataset.name;
                    const roll = div.dataset.roll;
                    const file = div.dataset.file;
                    const show = (
                        (studentVal === "" || name === studentVal) &&
                        (rollVal === "" || roll === rollVal) &&
                        (fileVal === "" || file === fileVal)
                    );
                    div.style.display = show ? "block" : "none";
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
                    const fileA = a.dataset.file.toLowerCase();
                    const fileB = b.dataset.file.toLowerCase();
                    switch(sortType) {
                        case "marks": return scoreB - scoreA;
                        case "name": return nameA.localeCompare(nameB);
                        case "roll": return rollA.localeCompare(rollB);
                        case "file": return fileA.localeCompare(fileB);
                        default: return 0;
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
            <option value="file">File Name (A–Z)</option>
        </select>

        <button onclick="showSummary()">Show Summary</button>

        <label for="studentSelect">Student:</label>
        <select id="studentSelect" onchange="filterReports()">
            <option value="">-- All Students --</option>
        """)

        for student in sorted(df_summary["student"].unique()):
            html_out.write(f"<option value='{html_lib.escape(student)}'>{html_lib.escape(student)}</option>")
        html_out.write("</select>")

        html_out.write("""
        <label for="rollSelect">Roll:</label>
        <select id="rollSelect" onchange="filterReports()">
            <option value="">-- All Rolls --</option>
        """)
        for roll in sorted(df_summary["roll_number"].unique()):
            html_out.write(f"<option value='{html_lib.escape(str(roll))}'>{html_lib.escape(str(roll))}</option>")
        html_out.write("</select>")

        html_out.write("""
        <label for="fileSelect">File:</label>
        <select id="fileSelect" onchange="filterReports()">
            <option value="">-- All Files --</option>
        """)
        for file in sorted(Path(f).name for f in df["file"].unique()):  # includes missing identity
            html_out.write(f"<option value='{html_lib.escape(file)}'>{html_lib.escape(file)}</option>")
        html_out.write("</select><hr><div id='reportContainer'>")

        # --- Student sections ---
        for (file, student, roll_number), g in grouped:
            total_score = g["score"].sum()
            total_possible = self.total_assertions
            percentage = round((total_score / total_possible) * 100, 2)

            html_out.write(
                f'<div class="student-block" data-name="{html_lib.escape(student)}" '
                f'data-roll="{html_lib.escape(str(roll_number))}" '
                f'data-file="{html_lib.escape(Path(file).name)}" '
                f'data-total="{total_score}">'
            )
            html_out.write(f"<h3>{html_lib.escape(student)} — {html_lib.escape(str(roll_number))}</h3>")
            html_out.write(f"<p><strong>File:</strong> {html_lib.escape(str(Path(file).name))}</p>")
            html_out.write(f"<p class='summary'>Total: {total_score}/{total_possible} ({percentage}%)</p>")

            for q, subdf in g.groupby("question"):
                html_out.write(f'<div class="question-block" data-qname="{html_lib.escape(str(q))}">')
                html_out.write(f'<div class="question-header">Question: {html_lib.escape(str(q))}</div>')
                desc = subdf["description"].iloc[0] if "description" in subdf.columns else ""
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

        # --- Summary modal (exclude missing identity) ---
        html_out.write("""
        </div><div id="overlay" onclick="closeSummary()"></div>
        <div id="summaryModal">
            <span class="close-btn" onclick="closeSummary()">✖</span>
            <h3>Student Summary</h3>
            <table>
                <thead><tr>
                  <th>Student</th><th>Roll Number</th><th>File</th>
                  <th>Total Marks</th><th>Out Of</th><th>Percentage</th>
                </tr></thead><tbody>
        """)
        summary = (
            df_summary.groupby(["file", "student", "roll_number"])
            .agg(total_score=("score", "sum"))
            .reset_index()
        )
        summary["max_score"] = self.total_assertions
        summary["percentage"] = (summary["total_score"] / summary["max_score"] * 100).fillna(0)
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
