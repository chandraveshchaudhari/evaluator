
import pandas as pd
from evaluator.reporting.report_builder import ReportBuilder


class ReportingService:
    """
    Service for building reports from comparison results.
    """
    def build(self, comparison_results):
        """
        Build a ReportBuilder object from comparison results.

        comparison_results : list[dict]
            Output from ComparisonService.run_assertions()

        Returns
        -------
        ReportBuilder: 
            Contains DataFrame + export methods
        """

        # Convert list of dicts to a pandas DataFrame
        df = pd.DataFrame(comparison_results)

        # Add useful summary columns
        if "score" in df.columns:
            df["max_score"] = 1
            df["percentage"] = (df["score"] / df["max_score"]) * 100

        # Create ReportBuilder with this DataFrame
        return ReportBuilder(df)

    def build(self, comparison_results):
        """Build a report from comparison results."""
        pass

    def build_dataframe(self, results):
        """Build a DataFrame from results."""
        pass

    def build_html(self, df, template):
        """Build HTML report from DataFrame and template."""
        pass

    def build_csv(self, df):
        """Build CSV report from DataFrame."""
        pass

    def build_log(self, df):
        """Build log report from DataFrame."""
        pass

    def generate_output_folder(self, base_path):
        """Generate output folder for reports."""
        pass
