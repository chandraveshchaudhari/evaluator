"""
Result dataclasses for standardized evaluator output.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AssertionResult:
    assertion: str
    passed: bool
    error: Optional[str] = None
    traceback: Optional[str] = None

@dataclass
class QuestionResult:
    question_name: str
    results: List[AssertionResult]


result['Name'] = result['Name'].apply(lambda x: str(x).strip().title())

new_df = result.sort_values(by='Formula Sum', ascending= False)

# new_df.to_csv("Assignment_1 Metrics", index = False)
clean_df = new_df.drop_duplicates(subset=['Roll Number'])

