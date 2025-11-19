class Compare:
    def __init__(self):
        self.instructor_solution = dict()  # Initialize an empty dictionary to hold instructor solutions
        self.student_solution = dict()  # Initialize an empty dictionary to hold student solutions

    def compare(self):
        for question, instructor_sol in self.instructor_solution.items():
            if question in self.student_solution:
                student_sol = self.student_solution[question]
                if instructor_sol == student_sol:
                    print(f"Question {question}: Correct")
                else:
                    print(f"Question {question}: Incorrect")            
            else:
                print(f"Question {question}: No answer provided by student")

from .notebook_compare import compare_notebook
from .excel_compare import compare_excel

class ComparisonService:
    def compare(self, executed_submission):
        if executed_submission.type == "notebook":
            return compare_notebook(executed_submission)
        if executed_submission.type == "excel":
            return compare_excel(executed_submission)
