# Ingestion & Validation Script for India MSME Compliance & Incentives Navigator
import json
import csv
import io
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def parse_csv_section(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    return [row for row in reader]

print(f"Data directory ready at: {DATA_DIR}")
