"""IO helpers."""
from __future__ import annotations
from typing import Optional


def read_text_file(path: str, encoding: str = "utf8") -> str:
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def write_to_file(string_data, file_path=f"logfile_{assignment_number}.txt"):
  file_path = os.path.join(os.getcwd(), file_path)
  # print('write to file is executed', file_path)
  with open(file_path, 'a+') as file:
    file.writelines(string_data)


