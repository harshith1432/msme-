# Script to assemble the entire MSME knowledge base dataset from the verified document into structured JSON files.
import json
import os
import csv
import io

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Parse Central Compliance from raw_central_compliance.csv
cc_path = os.path.join(DATA_DIR, 'raw_central_compliance.csv')
central_compliance = []
if os.path.exists(cc_path):
    with open(cc_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('ID'):
                central_compliance.append(row)

with open(os.path.join(DATA_DIR, 'central_compliance.json'), 'w', encoding='utf-8') as f:
    json.dump(central_compliance, f, indent=2, ensure_ascii=False)

print(f"Processed Central Compliance: {len(central_compliance)} records.")
