"""
Result dataclasses for standardized evaluator output.
"""

# result['Name'] = result['Name'].apply(lambda x: str(x).strip().title())

# new_df = result.sort_values(by='Formula Sum', ascending= False)

# # new_df.to_csv("Assignment_1 Metrics", index = False)
# clean_df = new_df.drop_duplicates(subset=['Roll Number'])

from typing import List


class Results:
    def __init__(self, comparison= None):
        self.data = comparison if comparison else Compare().data

    def report_data(self) -> List[dict]:
        report = []
        
        return report