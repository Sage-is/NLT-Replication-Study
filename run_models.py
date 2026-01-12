#!/usr/bin/env python
"""Run evaluations for models from CSV, tracking which have been completed."""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


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
                    if not success:
                        failed_runs += 1

                # Perturbed
                if not args.skip_perturbed:
                    key_perturbed = (model_id, scenario, f"{approach}_perturbed")
                    if key_perturbed in completed and not args.force:
                        print(f"SKIP: {model_id} | {scenario} | {approach} | perturbed (already completed)")
                        skipped_runs += 1
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
                        if not success:
                            failed_runs += 1

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total runs: {total_runs}")
    print(f"Skipped: {skipped_runs}")
    print(f"Failed: {failed_runs}")
    print(f"Successful: {total_runs - failed_runs}")


if __name__ == "__main__":
    main()
