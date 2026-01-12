#!/usr/bin/env python
"""Analyze aggregated results and generate summary reports."""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path


def load_aggregated_results(csv_path: Path) -> list[dict]:
    """Load aggregated results CSV."""
    if not csv_path.exists():
        return []
    
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        return list(reader)


def analyze_by_approach(results: list[dict]) -> dict:
    """Compute statistics grouped by approach."""
    stats = defaultdict(lambda: {"accuracies": [], "variances": [], "errors": []})
    
    for row in results:
        approach = row["approach"]
        stats[approach]["accuracies"].append(float(row.get("accuracy", 0.0)))
        stats[approach]["variances"].append(float(row.get("variance", 0.0)))
        stats[approach]["errors"].append(int(row.get("errors", 0)))
    
    # Compute means
    summary = {}
    for approach, data in stats.items():
        n = len(data["accuracies"])
        summary[approach] = {
            "count": n,
            "mean_accuracy": sum(data["accuracies"]) / n if n > 0 else 0.0,
            "mean_variance": sum(data["variances"]) / n if n > 0 else 0.0,
            "total_errors": sum(data["errors"]),
        }
    
    return summary


def analyze_by_model(results: list[dict]) -> dict:
    """Compute statistics grouped by model."""
    stats = defaultdict(lambda: defaultdict(lambda: {"accuracies": [], "variances": [], "errors": []}))
    
    for row in results:
        model = row["model_id"]
        approach = row["approach"]
        stats[model][approach]["accuracies"].append(float(row.get("accuracy", 0.0)))
        stats[model][approach]["variances"].append(float(row.get("variance", 0.0)))
        stats[model][approach]["errors"].append(int(row.get("errors", 0)))
    
    # Compute means
    summary = {}
    for model, approaches in stats.items():
        summary[model] = {}
        for approach, data in approaches.items():
            n = len(data["accuracies"])
            summary[model][approach] = {
                "count": n,
                "mean_accuracy": sum(data["accuracies"]) / n if n > 0 else 0.0,
                "mean_variance": sum(data["variances"]) / n if n > 0 else 0.0,
                "total_errors": sum(data["errors"]),
            }
    
    return summary


def analyze_by_scenario(results: list[dict]) -> dict:
    """Compute statistics grouped by scenario."""
    stats = defaultdict(lambda: defaultdict(lambda: {"accuracies": [], "variances": [], "errors": []}))
    
    for row in results:
        scenario = row["scenario"]
        approach = row["approach"]
        stats[scenario][approach]["accuracies"].append(float(row.get("accuracy", 0.0)))
        stats[scenario][approach]["variances"].append(float(row.get("variance", 0.0)))
        stats[scenario][approach]["errors"].append(int(row.get("errors", 0)))
    
    # Compute means
    summary = {}
    for scenario, approaches in stats.items():
        summary[scenario] = {}
        for approach, data in approaches.items():
            n = len(data["accuracies"])
            summary[scenario][approach] = {
                "count": n,
                "mean_accuracy": sum(data["accuracies"]) / n if n > 0 else 0.0,
                "mean_variance": sum(data["variances"]) / n if n > 0 else 0.0,
                "total_errors": sum(data["errors"]),
            }
    
    return summary


def analyze_nlt_gains(results: list[dict]) -> dict:
    """Compute NLT gains (NLT accuracy - Structured accuracy) per model/scenario."""
    # Group by (model, scenario, perturbed)
    paired_data = defaultdict(lambda: {"nlt": None, "structured": None})
    
    for row in results:
        key = (row["model_id"], row["scenario"], row["perturbed"])
        approach = row["approach"]
        accuracy = float(row.get("accuracy", 0.0))
        
        paired_data[key][approach] = accuracy
    
    # Compute gains
    gains = []
    for key, data in paired_data.items():
        if data["nlt"] is not None and data["structured"] is not None:
            model, scenario, perturbed = key
            gain = data["nlt"] - data["structured"]
            gains.append({
                "model": model,
                "scenario": scenario,
                "perturbed": perturbed,
                "nlt_accuracy": data["nlt"],
                "structured_accuracy": data["structured"],
                "gain": gain,
            })
    
    return gains


def print_approach_summary(stats: dict):
    """Print approach-level summary."""
    print("\n" + "="*80)
    print("SUMMARY BY APPROACH")
    print("="*80)
    
    for approach, data in sorted(stats.items()):
        print(f"\n{approach.upper()}:")
        print(f"  Evaluations: {data['count']}")
        print(f"  Mean Accuracy: {data['mean_accuracy']:.1%}")
        print(f"  Mean Variance: {data['mean_variance']:.4f}")
        print(f"  Total Errors: {data['total_errors']}")


def print_model_summary(stats: dict):
    """Print model-level summary."""
    print("\n" + "="*80)
    print("SUMMARY BY MODEL")
    print("="*80)
    
    for model, approaches in sorted(stats.items()):
        print(f"\n{model}:")
        for approach, data in sorted(approaches.items()):
            print(f"  {approach:12} - Accuracy: {data['mean_accuracy']:6.1%} | "
                  f"Variance: {data['mean_variance']:.4f} | Errors: {data['total_errors']}")


def print_scenario_summary(stats: dict):
    """Print scenario-level summary."""
    print("\n" + "="*80)
    print("SUMMARY BY SCENARIO")
    print("="*80)
    
    for scenario, approaches in sorted(stats.items()):
        print(f"\n{scenario.upper()}:")
        for approach, data in sorted(approaches.items()):
            print(f"  {approach:12} - Accuracy: {data['mean_accuracy']:6.1%} | "
                  f"Variance: {data['mean_variance']:.4f} | Errors: {data['total_errors']}")


def print_nlt_gains(gains: list[dict]):
    """Print NLT accuracy gains."""
    print("\n" + "="*80)
    print("NLT GAINS (NLT - Structured)")
    print("="*80)
    
    if not gains:
        print("\nNo paired data available for gain calculation.")
        return
    
    # Overall mean gain
    mean_gain = sum(g["gain"] for g in gains) / len(gains)
    print(f"\nOverall Mean Gain: {mean_gain:+.1%}")
    
    # Per model
    print("\nBy Model:")
    by_model = defaultdict(list)
    for g in gains:
        by_model[g["model"]].append(g["gain"])
    
    for model, model_gains in sorted(by_model.items()):
        mean = sum(model_gains) / len(model_gains)
        print(f"  {model:40} {mean:+6.1%} (n={len(model_gains)})")
    
    # Per scenario
    print("\nBy Scenario:")
    by_scenario = defaultdict(list)
    for g in gains:
        by_scenario[g["scenario"]].append(g["gain"])
    
    for scenario, scenario_gains in sorted(by_scenario.items()):
        mean = sum(scenario_gains) / len(scenario_gains)
        print(f"  {scenario:12} {mean:+6.1%} (n={len(scenario_gains)})")


def export_summary_csv(output_path: Path, approach_stats: dict, model_stats: dict, scenario_stats: dict):
    """Export summary statistics to CSV."""
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        
        # Approach summary
        writer.writerow(["# APPROACH SUMMARY"])
        writer.writerow(["approach", "count", "mean_accuracy", "mean_variance", "total_errors"])
        for approach, data in sorted(approach_stats.items()):
            writer.writerow([
                approach,
                data["count"],
                f"{data['mean_accuracy']:.4f}",
                f"{data['mean_variance']:.4f}",
                data["total_errors"],
            ])
        
        writer.writerow([])
        
        # Model summary
        writer.writerow(["# MODEL SUMMARY"])
        writer.writerow(["model", "approach", "count", "mean_accuracy", "mean_variance", "total_errors"])
        for model, approaches in sorted(model_stats.items()):
            for approach, data in sorted(approaches.items()):
                writer.writerow([
                    model,
                    approach,
                    data["count"],
                    f"{data['mean_accuracy']:.4f}",
                    f"{data['mean_variance']:.4f}",
                    data["total_errors"],
                ])
        
        writer.writerow([])
        
        # Scenario summary
        writer.writerow(["# SCENARIO SUMMARY"])
        writer.writerow(["scenario", "approach", "count", "mean_accuracy", "mean_variance", "total_errors"])
        for scenario, approaches in sorted(scenario_stats.items()):
            for approach, data in sorted(approaches.items()):
                writer.writerow([
                    scenario,
                    approach,
                    data["count"],
                    f"{data['mean_accuracy']:.4f}",
                    f"{data['mean_variance']:.4f}",
                    data["total_errors"],
                ])
    
    print(f"\nSummary exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze aggregated NLT evaluation results")
    parser.add_argument(
        "--csv",
        default="aggregated_results.csv",
        help="Path to aggregated results CSV"
    )
    parser.add_argument(
        "--export",
        help="Export summary to CSV file"
    )
    parser.add_argument(
        "--show-gains",
        action="store_true",
        help="Show NLT accuracy gains over structured approach"
    )
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv)
    
    if not csv_path.exists():
        print(f"ERROR: Aggregated results file not found: {csv_path}", file=sys.stderr)
        print("Run evaluations first with: make run-models", file=sys.stderr)
        sys.exit(1)
    
    # Load data
    results = load_aggregated_results(csv_path)
    
    if not results:
        print("No results found in aggregated CSV.")
        sys.exit(0)
    
    print(f"Loaded {len(results)} result entries from {csv_path}")
    
    # Analyze
    approach_stats = analyze_by_approach(results)
    model_stats = analyze_by_model(results)
    scenario_stats = analyze_by_scenario(results)
    
    # Print summaries
    print_approach_summary(approach_stats)
    print_model_summary(model_stats)
    print_scenario_summary(scenario_stats)
    
    if args.show_gains:
        gains = analyze_nlt_gains(results)
        print_nlt_gains(gains)
    
    # Export if requested
    if args.export:
        export_summary_csv(Path(args.export), approach_stats, model_stats, scenario_stats)
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
