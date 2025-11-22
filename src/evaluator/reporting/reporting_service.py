import pandas as pd
from pathlib import Path
from evaluator.reporting.report_builder import ReportBuilder


class ReportingService:
    """
    Service for building and saving reports from comparison results.
    """

    def __init__(self):
        self.debug = False

    # -------------------------------------------------------------------------
    def build(self, executed_results):
        """
        Build a combined report across multiple student submissions.

        Parameters
        ----------
        executed_results : list[dict]
            Each entry should be from ExecutionService.execute(...), containing:
            {
                "student_path": Path,
                "execution": {...},
                "results": [ {assertion, question, status, score, error}, ... ]
            }

        Returns
        -------
        ReportBuilder
            A wrapper containing the flattened DataFrame and export utilities.
        """
        all_rows = []

        for item in executed_results:
            student_path = Path(item.get("student_path", ""))
            results = item.get("results", [])
            student_name = student_path.stem

            for r in results:
                row = {
                    "student": student_name,
                    "file": str(student_path),
                    "question": r.get("question"),
                    "assertion": r.get("assertion"),
                    "status": r.get("status"),
                    "score": r.get("score"),
                    "error": r.get("error"),
                }
                all_rows.append(row)

        df = pd.DataFrame(all_rows)

        if df.empty:
            if self.debug:
                print("Warning: Empty DataFrame in ReportingService.build()")
            return ReportBuilder(pd.DataFrame())

        # Compute per-question and per-student aggregates
        df["max_score"] = 1
        df["percentage"] = (df["score"] / df["max_score"]) * 100

        # Compute summary stats per student
        student_summary = (
            df.groupby("student")[["score", "max_score"]]
            .sum()
            .reset_index()
            .assign(percentage=lambda x: (x["score"] / x["max_score"]) * 100)
        )

        # Attach as attribute for quick access
        df.attrs["summary"] = student_summary

        return ReportBuilder(df)

    # -------------------------------------------------------------------------
    def save_all(self, report: "ReportBuilder", output_dir: Path):
        """
        Save full report and summary into the given folder.

        Parameters
        ----------
        report : ReportBuilder
            The report object returned from build()
        output_dir : Path
            Target folder for saving outputs.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save detailed and summary reports
        report.to_csv(output_dir / "detailed_report.csv")
        report.to_html(output_dir / "detailed_report.html")
        report.to_log(output_dir / "detailed_report.log")

        # Save summary separately if available
        summary_df = report.df.attrs.get("summary")
        if summary_df is not None:
            summary_path = output_dir / "summary_by_student.csv"
            summary_df.to_csv(summary_path, index=False)

        if self.debug:
            print(f"Reports saved to {output_dir}")
