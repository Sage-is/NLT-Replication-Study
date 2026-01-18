#!/usr/bin/env python
"""
Safe backfill script to act as a pure data aggregation tool.
It scans the results/ directory for JSON files and updates aggregated_results.csv
with token usage stats, WITHOUT triggering any model runs.
"""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

# Get project root (two levels up from this script)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def update_aggregated_results(csv_path: Path):
    """Scan results directory and rebuild/update the aggregated CSV."""
    results_dir = PROJECT_ROOT / "results"
    if not results_dir.exists():
        print("No results directory found.")
        return

    # Dictionary to hold latest result for each (model, scenario, approach, perturbed) key
    # Key: (model_id, scenario, approach, perturbed)
    # Value: dict of row data
    latest_results = {}

    print("Scanning results directory...")
    
    # Traverse directory structure: results/scenario/approach/perturbed/model_id/*.json
    for scenario_dir in results_dir.iterdir():
        if not scenario_dir.is_dir(): continue
        scenario = scenario_dir.name
        
        for approach_dir in scenario_dir.iterdir():
            if not approach_dir.is_dir(): continue
            approach = approach_dir.name
            
            for perturbed_dir in approach_dir.iterdir():
                if not perturbed_dir.is_dir(): continue
                perturbed_str = perturbed_dir.name
                perturbed = (perturbed_str == "perturbed")
                
                for model_dir in perturbed_dir.iterdir():
                    if not model_dir.is_dir(): continue
                    # Decode safe model name back to ID if needed, 
                    # but usually we can read it from the JSON content to be sure.
                    
                    # Find latest JSON file
                    json_files = sorted(model_dir.glob("*.json"), reverse=True)
                    if not json_files:
                        continue
                        
                    latest_file = json_files[0]
                    
                    try:
                        with open(latest_file) as f:
                            data = json.load(f)
                            
                        summary = data.get("summary", {})
                        model_id = summary.get("model", "unknown")
                        
                        # Extract metrics
                        accuracy = summary.get("accuracy")
                        variance = summary.get("variance")
                        
                        # Handle None values
                        accuracy_str = "" if accuracy is None else str(accuracy)
                        variance_str = "" if variance is None else str(variance)
                        
                        # Extract token usage
                        total_tokens = 0
                        prompt_tokens = 0
                        completion_tokens = 0
                        
                        results_list = data.get("results", [])
                        if results_list:
                            for res in results_list:
                                usage = res.get("usage", {})
                                if usage:
                                    total_tokens += int(usage.get("total_tokens") or 0)
                                    prompt_tokens += int(usage.get("prompt_tokens") or 0)
                                    completion_tokens += int(usage.get("completion_tokens") or 0)
                        
                        row = {
                            "model_id": model_id,
                            "scenario": scenario,
                            "approach": approach,
                            "perturbed": "yes" if perturbed else "no",
                            "accuracy": accuracy_str,
                            "variance": variance_str,
                            "total": summary.get("total", 0),
                            "errors": summary.get("errors", 0),
                            "valid_trials": summary.get("valid_trials", 0),
                            "aborted": "yes" if summary.get("aborted", False) else "no",
                            "timestamp": data.get("timestamp", datetime.now().strftime("%Y%m%d_%H%M%S")),
                            "result_file": str(latest_file),
                            "total_tokens": total_tokens,
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens
                        }
                        
                        key = (model_id, scenario, approach, "yes" if perturbed else "no")
                        latest_results[key] = row
                        
                    except Exception as e:
                        print(f"Error processing {latest_file}: {e}")

    print(f"Found {len(latest_results)} unique result sets.")
    
    # Define fields
    fieldnames = [
        "model_id",
        "scenario",
        "approach",
        "perturbed",
        "accuracy",
        "variance",
        "total",
        "errors",
        "valid_trials",
        "aborted",
        "timestamp",
        "result_file",
        "total_tokens",
        "prompt_tokens",
        "completion_tokens",
    ]

    # Write to CSV
    print(f"Writing to {csv_path}...")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for key in sorted(latest_results.keys()):
            writer.writerow(latest_results[key])
            
    print("Done.")

if __name__ == "__main__":
    update_aggregated_results(PROJECT_ROOT / "aggregated_results.csv")
