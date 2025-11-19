from pathlib import Path

class IngestionService:
    def load_submissions(self, submission_folder):
        folder = Path(submission_folder)
        return [f for f in folder.iterdir() if f.is_file()]
