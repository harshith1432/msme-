"""
Parser script to process the MSME Compliance & Incentives Navigator dataset.
"""
import os
import json
import csv
import io

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# We can store the parsed records in their respective JSON files
print("Parser setup complete.")
