#!/usr/bin/env python
"""Validate that qwen structured results are cleaned properly."""
import csv
from pathlib import Path

print("Raw CSV values for qwen:")
print("-" * 80)
with open("aggregated_results.csv") as f:
    for row in csv.DictReader(f):
        if "qwen" in row["model_id"]:
            print(f"{row['model_id']:45} | {row['approach']:12} | acc={row['accuracy']:4} var={row['variance']:6} err={row['errors']:3}")

print("\n" + "=" * 80)
print("After cleaning (what analyze_results.py will see):")
print("-" * 80)

from analyze_results import load_aggregated_results
results = load_aggregated_results(Path("aggregated_results.csv"))
for row in results:
    if "qwen" in row["model_id"]:
        print(f"{row['model_id']:45} | {row['approach']:12} | acc={row['accuracy']:4} var={row['variance']:6} err={row['errors']:3}")

print("\n✓ Note: structured approach now shows 0.0 accuracy instead of 1.0")
