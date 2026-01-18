#!/usr/bin/env python
"""Analyze aggregated results and generate summary reports."""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path


def clean_results(results: list[dict]) -> list[dict]:
    """Clean edge cases in results data.
    
    Rules:
    1. If error_rate > 75% (only 25% valid trials), report accuracy=0.0 (doesn't work)
    2. If accuracy=1.0 and variance=0.0 (too few valid trials all succeeded), treat as 0.0
    """
    cleaned = []
    for row in results:
        row = row.copy()  # Don't modify original
        
        try:
            total = int(row.get("total", 0))
            errors = int(row.get("errors", 0))
            accuracy = row.get("accuracy", "")
            variance = row.get("variance", "")
            
            if total > 0:
                error_rate = errors / total
                
                # Rule 1: If error rate is very high (>75%), mark as not applicable
                if error_rate > 0.75:
                    row["accuracy"] = "0.0"
                    row["variance"] = "0.0"
                else:
                    # Rule 2: If accuracy=1.0 and variance=0.0, treat as 0.0
                    try:
                        acc_float = float(accuracy) if accuracy else None
                        var_float = float(variance) if variance else None
                        if acc_float == 1.0 and var_float == 0.0:
                            row["accuracy"] = "0.0"
                            row["variance"] = "0.0"
                    except (ValueError, TypeError):
                        pass
        except (ValueError, TypeError):
            pass  # Leave as is if can't convert
        
        cleaned.append(row)
    
    return cleaned


def load_aggregated_results(csv_path: Path) -> list[dict]:
    """Load aggregated results CSV and clean edge cases."""
    if not csv_path.exists():
        return []
    
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        results = list(reader)
    
    # Clean edge cases (accuracy=1.0, variance=0.0 -> treat as 0.0)
    results = clean_results(results)
    return results


def analyze_by_approach(results: list[dict]) -> dict:
    """Compute statistics grouped by approach."""
    stats = defaultdict(lambda: {"accuracies": [], "variances": [], "variances_exclusive": [], "errors": [], "aborted": 0})
    
    for row in results:
        approach = row["approach"]
        # Skip rows with empty/None accuracy (all trials errored)
        accuracy = row.get("accuracy", "")
        variance = row.get("variance", "")
        if accuracy != "" and accuracy is not None:
            acc_val = float(accuracy)
            stats[approach]["accuracies"].append(acc_val)
            
            if variance != "" and variance is not None:
                var_val = float(variance)
                stats[approach]["variances"].append(var_val)
                # Exclusive variance: Only include if accuracy > 0 (excludes failed approaches)
                if acc_val > 0:
                    stats[approach]["variances_exclusive"].append(var_val)
                    
        stats[approach]["errors"].append(int(row.get("errors", 0)))
        if row.get("aborted", "no") == "yes":
            stats[approach]["aborted"] += 1
    
    # Compute means
    summary = {}
    for approach, data in stats.items():
        n_acc = len(data["accuracies"])
        n_var = len(data["variances"])
        n_var_ex = len(data["variances_exclusive"])
        summary[approach] = {
            "count": len(data["errors"]),  # Total evaluations
            "valid_count": n_acc,  # Evaluations with valid accuracy
            "mean_accuracy": sum(data["accuracies"]) / n_acc if n_acc > 0 else None,
            "mean_variance": sum(data["variances"]) / n_var if n_var > 0 else None,
            "mean_variance_exclusive": sum(data["variances_exclusive"]) / n_var_ex if n_var_ex > 0 else None,
            "total_errors": sum(data["errors"]),
            "aborted_count": data["aborted"],
        }
    
    return summary


def analyze_by_model(results: list[dict]) -> dict:
    """Compute statistics grouped by model."""
    stats = defaultdict(lambda: defaultdict(lambda: {"accuracies": [], "variances": [], "variances_exclusive": [], "errors": [], "aborted": 0}))
    
    for row in results:
        model = row["model_id"]
        approach = row["approach"]
        # Skip rows with empty/None accuracy (all trials errored)
        accuracy = row.get("accuracy", "")
        variance = row.get("variance", "")
        if accuracy != "" and accuracy is not None:
            acc_val = float(accuracy)
            stats[model][approach]["accuracies"].append(acc_val)
            
            if variance != "" and variance is not None:
                var_val = float(variance)
                stats[model][approach]["variances"].append(var_val)
                # Exclusive variance: Only include if accuracy > 0
                if acc_val > 0:
                    stats[model][approach]["variances_exclusive"].append(var_val)
                    
        stats[model][approach]["errors"].append(int(row.get("errors", 0)))
        if row.get("aborted", "no") == "yes":
            stats[model][approach]["aborted"] += 1
    
    # Compute means
    summary = {}
    for model, approaches in stats.items():
        summary[model] = {}
        for approach, data in approaches.items():
            n_acc = len(data["accuracies"])
            n_var = len(data["variances"])
            n_var_ex = len(data["variances_exclusive"])
            summary[model][approach] = {
                "count": len(data["errors"]),
                "valid_count": n_acc,
                "mean_accuracy": sum(data["accuracies"]) / n_acc if n_acc > 0 else None,
                "mean_variance": sum(data["variances"]) / n_var if n_var > 0 else None,
                "mean_variance_exclusive": sum(data["variances_exclusive"]) / n_var_ex if n_var_ex > 0 else None,
                "total_errors": sum(data["errors"]),
                "aborted_count": data["aborted"],
            }
    
    return summary


def analyze_by_scenario(results: list[dict]) -> dict:
    """Compute statistics grouped by scenario."""
    stats = defaultdict(lambda: defaultdict(lambda: {"accuracies": [], "variances": [], "variances_exclusive": [], "errors": [], "aborted": 0}))
    
    for row in results:
        scenario = row["scenario"]
        approach = row["approach"]
        # Skip rows with empty/None accuracy (all trials errored)
        accuracy = row.get("accuracy", "")
        variance = row.get("variance", "")
        if accuracy != "" and accuracy is not None:
            acc_val = float(accuracy)
            stats[scenario][approach]["accuracies"].append(acc_val)
            
            if variance != "" and variance is not None:
                var_val = float(variance)
                stats[scenario][approach]["variances"].append(var_val)
                # Exclusive variance: Only include if accuracy > 0
                if acc_val > 0:
                    stats[scenario][approach]["variances_exclusive"].append(var_val)
                    
        stats[scenario][approach]["errors"].append(int(row.get("errors", 0)))
        if row.get("aborted", "no") == "yes":
            stats[scenario][approach]["aborted"] += 1
    
    # Compute means
    summary = {}
    for scenario, approaches in stats.items():
        summary[scenario] = {}
        for approach, data in approaches.items():
            n_acc = len(data["accuracies"])
            n_var = len(data["variances"])
            n_var_ex = len(data["variances_exclusive"])
            summary[scenario][approach] = {
                "count": len(data["errors"]),
                "valid_count": n_acc,
                "mean_accuracy": sum(data["accuracies"]) / n_acc if n_acc > 0 else None,
                "mean_variance": sum(data["variances"]) / n_var if n_var > 0 else None,
                "mean_variance_exclusive": sum(data["variances_exclusive"]) / n_var_ex if n_var_ex > 0 else None,
                "total_errors": sum(data["errors"]),
                "aborted_count": data["aborted"],
            }
    
    return summary


def analyze_nlt_gains(results: list[dict]) -> dict:
    """Compute NLT gains (NLT accuracy - Structured accuracy) per model/scenario."""
    # Group by (model, scenario, perturbed)
    paired_data = defaultdict(lambda: {"nlt": None, "structured": None})
    
    for row in results:
        key = (row["model_id"], row["scenario"], row["perturbed"])
        approach = row["approach"]
        accuracy = row.get("accuracy", "")
        
        # Skip if accuracy is empty/None (all trials errored)
        if accuracy == "" or accuracy is None:
            continue
            
        paired_data[key][approach] = float(accuracy)
    
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
        print(f"  Evaluations: {data['count']} ({data['valid_count']} with valid results)")
        if data['mean_accuracy'] is not None:
            print(f"  Mean Accuracy: {data['mean_accuracy']:.1%}")
        else:
            print(f"  Mean Accuracy: N/A (all trials errored)")
        if data['mean_variance'] is not None:
            var_ex_str = f" (excl. failed: {data['mean_variance_exclusive']:.4f})" if data['mean_variance_exclusive'] is not None else ""
            print(f"  Mean Variance: {data['mean_variance']:.4f}{var_ex_str}")
        else:
            print(f"  Mean Variance: N/A")
        print(f"  Total Errors: {data['total_errors']}")
        if data['aborted_count'] > 0:
            print(f"  Aborted Runs: {data['aborted_count']}")


def print_model_summary(stats: dict):
    """Print model-level summary."""
    print("\n" + "="*80)
    print("SUMMARY BY MODEL")
    print("="*80)
    
    for model, approaches in sorted(stats.items()):
        print(f"\n{model}:")
        for approach, data in sorted(approaches.items()):
            acc_str = f"{data['mean_accuracy']:6.1%}" if data['mean_accuracy'] is not None else "  N/A "
            var_val = data['mean_variance']
            var_ex = data['mean_variance_exclusive']
            
            if var_val is not None:
                if var_ex is not None and abs(var_val - var_ex) > 0.0001:
                    var_str = f"{var_val:.4f} ({var_ex:.4f})"
                else:
                    var_str = f"{var_val:.4f}       "
            else:
                var_str = "N/A          "
                
            aborted_str = f" [ABORTED:{data['aborted_count']}]" if data['aborted_count'] > 0 else ""
            print(f"  {approach:12} - Accuracy: {acc_str} | "
                  f"Variance: {var_str} | Errors: {data['total_errors']}{aborted_str}")


def print_scenario_summary(stats: dict):
    """Print scenario-level summary."""
    print("\n" + "="*80)
    print("SUMMARY BY SCENARIO")
    print("="*80)
    
    for scenario, approaches in sorted(stats.items()):
        print(f"\n{scenario.upper()}:")
        for approach, data in sorted(approaches.items()):
            acc_str = f"{data['mean_accuracy']:6.1%}" if data['mean_accuracy'] is not None else "  N/A "
            var_val = data['mean_variance']
            var_ex = data['mean_variance_exclusive']
            
            if var_val is not None:
                if var_ex is not None and abs(var_val - var_ex) > 0.0001:
                    var_str = f"{var_val:.4f} ({var_ex:.4f})"
                else:
                    var_str = f"{var_val:.4f}       "
            else:
                var_str = "N/A          "
            
            aborted_str = f" [ABORTED:{data['aborted_count']}]" if data['aborted_count'] > 0 else ""
            print(f"  {approach:12} - Accuracy: {acc_str} | "
                  f"Variance: {var_str} | Errors: {data['total_errors']}{aborted_str}")


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
