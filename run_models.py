#!/usr/bin/env python
"""Run evaluations for models from CSV, tracking which have been completed."""

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def update_models_csv(csv_path: Path, model_id: str, scenario: str, approach: str):
    """Update models.csv to mark a scenario/approach as done."""
    rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row["model_id"] == model_id:
                col_name = f"{scenario}_{approach}_done"
                if col_name in row:
                    row[col_name] = "yes"
            rows.append(row)

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def update_aggregated_results(
    csv_path: Path, model_id: str, scenario: str, approach: str, perturbed: bool, result_file: Path
):
    """Add or update entry in aggregated_results.csv."""
    # Read result JSON
    with open(result_file) as f:
        data = json.load(f)

    summary = data.get("summary", {})

    # Prepare new row
    new_row = {
        "model_id": model_id,
        "scenario": scenario,
        "approach": approach,
        "perturbed": "yes" if perturbed else "no",
        "accuracy": summary.get("accuracy", 0.0),
        "variance": summary.get("variance", 0.0),
        "total": summary.get("total", 0),
        "errors": summary.get("errors", 0),
        "timestamp": data.get("timestamp", datetime.now().strftime("%Y%m%d_%H%M%S")),
        "result_file": str(result_file),
    }

    # Read existing rows
    rows = []
    fieldnames = [
        "model_id",
        "scenario",
        "approach",
        "perturbed",
        "accuracy",
        "variance",
        "total",
        "errors",
        "timestamp",
        "result_file",
    ]

    if csv_path.exists():
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    # Update or append
    found = False
    for i, row in enumerate(rows):
        if (
            row["model_id"] == model_id
            and row["scenario"] == scenario
            and row["approach"] == approach
            and row["perturbed"] == new_row["perturbed"]
        ):
            rows[i] = new_row
            found = True
            break

    if not found:
        rows.append(new_row)

    # Write back
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_latest_result_file(results_dir: Path, model_id: str, scenario: str, approach: str, perturbed: bool) -> Path | None:
    """Find the latest result JSON file for a given configuration."""
    perturb_str = "perturbed" if perturbed else "non_perturbed"
    safe_model = model_id.replace("/", "_").replace(":", "_")
    
    result_path = results_dir / scenario / approach / perturb_str / safe_model
    if not result_path.exists():
        return None
    
    json_files = sorted(result_path.glob("*.json"), reverse=True)
    return json_files[0] if json_files else None


def get_completed_models(results_dir: Path) -> dict[tuple[str, str, str], bool]:
    """Get set of (model, scenario, approach) that have results."""
    completed = {}
    if not results_dir.exists():
        return completed

    for scenario_dir in results_dir.iterdir():
        if not scenario_dir.is_dir():
            continue
        scenario = scenario_dir.name

        for approach_dir in scenario_dir.iterdir():
            if not approach_dir.is_dir():
                continue
            approach = approach_dir.name

            for perturbed_dir in approach_dir.iterdir():
                if not perturbed_dir.is_dir():
                    continue

                for model_dir in perturbed_dir.iterdir():
                    if not model_dir.is_dir():
                        continue
                    model = model_dir.name.replace("_", "/").replace(":", ":")

                    # Check if has any JSON results
                    if list(model_dir.glob("*.json")):
                        completed[(model, scenario, approach)] = True

    return completed


def run_evaluation(
    model_id: str,
    scenario: str,
    approach: str,
    replicates: int = 5,
    perturbed: bool = False,
    sample_limit: int | None = None,
) -> bool:
    """Run evaluation for a model/scenario/approach combination."""
    cmd = [
        ".venv/bin/python",
        "-m",
        "nlt.cli",
        "--scenario",
        scenario,
        "--approach",
        approach,
        "--model",
        model_id,
        "--replicates",
        str(replicates),
    ]

    if perturbed:
        cmd.append("--perturbed")
    if sample_limit:
        cmd.extend(["--sample-limit", str(sample_limit)])

    print(f"\n{'='*60}")
    print(f"Running: {model_id} | {scenario} | {approach} | {'perturbed' if perturbed else 'non-perturbed'}")
    print(f"{'='*60}\n")

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Evaluation failed with exit code {e.returncode}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Run evaluations from models CSV")
    parser.add_argument("--csv", default="models.csv", help="Path to models CSV file")
    parser.add_argument("--results-dir", default="results", help="Results directory to check for existing runs")
    parser.add_argument("--aggregated-csv", default="aggregated_results.csv", help="Path to aggregated results CSV")
    parser.add_argument(
        "--force", action="store_true", help="Rerun all models even if they have results"
    )
    parser.add_argument("--scenarios", nargs="+", default=["alex", "sage"], help="Scenarios to run")
    parser.add_argument(
        "--approaches", nargs="+", default=["nlt", "structured"], help="Approaches to run"
    )
    parser.add_argument("--replicates", type=int, default=5, help="Number of replicates per input")
    parser.add_argument("--sample-limit", type=int, help="Limit number of inputs (for testing)")
    parser.add_argument("--skip-perturbed", action="store_true", help="Only run non-perturbed prompts")

    args = parser.parse_args()

    # Read models CSV
    models = []
    with open(args.csv) as f:
        reader = csv.DictReader(f)
        models = list(reader)

    print(f"Loaded {len(models)} models from {args.csv}")

    # Get completed evaluations
    completed = get_completed_models(Path(args.results_dir))
    print(f"Found {len(completed)} completed evaluations")

    # Run evaluations
    total_runs = 0
    skipped_runs = 0
    failed_runs = 0

    for model in models:
        model_id = model["model_id"]

        for scenario in args.scenarios:
            for approach in args.approaches:
                # Non-perturbed
                key = (model_id, scenario, approach)
                if key in completed and not args.force:
                    print(f"SKIP: {model_id} | {scenario} | {approach} | non-perturbed (already completed)")
                    skipped_runs += 1
                    
                    # Still update aggregated results if file exists
                    result_file = get_latest_result_file(
                        Path(args.results_dir), model_id, scenario, approach, perturbed=False
                    )
                    if result_file:
                        update_aggregated_results(
                            Path(args.aggregated_csv), model_id, scenario, approach, False, result_file
                        )
                else:
                    success = run_evaluation(
                        model_id=model_id,
                        scenario=scenario,
                        approach=approach,
                        replicates=args.replicates,
                        perturbed=False,
                        sample_limit=args.sample_limit,
                    )
                    total_runs += 1
                    if success:
                        # Update models.csv
                        update_models_csv(Path(args.csv), model_id, scenario, approach)
                        
                        # Update aggregated results
                        result_file = get_latest_result_file(
                            Path(args.results_dir), model_id, scenario, approach, perturbed=False
                        )
                        if result_file:
                            update_aggregated_results(
                                Path(args.aggregated_csv), model_id, scenario, approach, False, result_file
                            )
                    else:
                        failed_runs += 1

                # Perturbed
                if not args.skip_perturbed:
                    key_perturbed = (model_id, scenario, f"{approach}_perturbed")
                    if key_perturbed in completed and not args.force:
                        print(f"SKIP: {model_id} | {scenario} | {approach} | perturbed (already completed)")
                        skipped_runs += 1
                        
                        # Still update aggregated results if file exists
                        result_file = get_latest_result_file(
                            Path(args.results_dir), model_id, scenario, approach, perturbed=True
                        )
                        if result_file:
                            update_aggregated_results(
                                Path(args.aggregated_csv), model_id, scenario, approach, True, result_file
                            )
                    else:
                        success = run_evaluation(
                            model_id=model_id,
                            scenario=scenario,
                            approach=approach,
                            replicates=args.replicates,
                            perturbed=True,
                            sample_limit=args.sample_limit,
                        )
                        total_runs += 1
                        if success:
                            # Update models.csv (same column, just marks scenario/approach done)
                            update_models_csv(Path(args.csv), model_id, scenario, approach)
                            
                            # Update aggregated results
                            result_file = get_latest_result_file(
                                Path(args.results_dir), model_id, scenario, approach, perturbed=True
                            )
                            if result_file:
                                update_aggregated_results(
                                    Path(args.aggregated_csv), model_id, scenario, approach, True, result_file
                                )
                        else:
                            failed_runs += 1

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total runs: {total_runs}")
    print(f"Skipped: {skipped_runs}")
    print(f"Failed: {failed_runs}")
    print(f"Successful: {total_runs - failed_runs}")
    print(f"\nResults aggregated in: {args.aggregated_csv}")


if __name__ == "__main__":
    main()
