# src/evaluator/evaluator.py

from evaluator.reporting.report_builder import ReportBuilder


class Evaluator:
    def __init__(self, solution_file, submission_folder):
        self.solution_file = solution_file
        self.submission_folder = submission_folder

    def report(self):
        # orchestrate your ingestion, comparison, execution, reporting modules
        report = ReportBuilder(self.solution_file, self.submission_folder)
        return report


from evaluator.ingestion.ingestion_service import IngestionService
from evaluator.execution.execution_service import ExecutionService
from evaluator.comparison.comparison_service import ComparisonService
from evaluator.reporting.reporting_service import ReportingService

class Evaluator:
    def __init__(self, solution_file, submission_folder):
        self.solution_file = solution_file
        self.submission_folder = submission_folder

        # DI (Dependency inversion)
        self.ingestion = IngestionService()
        self.execution = ExecutionService()
        self.comparison = ComparisonService()
        self.reporting = ReportingService()

    def run(self):
        # 1. Load submissions
        submissions = self.ingestion.load_submissions(self.submission_folder)

        all_results = []

        for submission in submissions:
            # 2. Execute
            executed = self.execution.execute(self.solution_file, submission)

            # 3. Compare
            result_dict = self.comparison.compare(executed)

            all_results.append(result_dict)

        # 4. Reporting
        report = self.reporting.build(all_results)
        return report
