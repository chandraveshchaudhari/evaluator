import json
from pathlib import Path
import pandas as pd
import nbformat
from openpyxl import load_workbook


def load_notebook(path):
    return nbformat.read(path, as_version=4)

def load_excel(path):
    return load_workbook(path, data_only=False)

def load_json(path):
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)

def load_csv(path):
    return pd.read_csv(path)

def load_raw_code(path):
    return Path(path).read_text(encoding="utf8")
