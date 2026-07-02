#!/usr/bin/env python
"""Clean up bad evaluation results (aborted runs, incomplete test runs).

Scans all result JSON files, identifies:
  1. Aborted runs (all trials errored, summary.aborted=True)
  2. Incomplete/test runs (total trials < expected, e.g. sample_limit=2)

Removes those files, cleans corresponding rows from aggregated_results.csv,
and prunes empty directories.

Usage:
    python src/scripts/clean_aborted.py              # dry-run (default)
    python src/scripts/clean_aborted.py --apply      # actually delete
    python src/scripts/clean_aborted.py --apply -v   # delete with verbose output
"""

import argparse
import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
AGGREGATED_CSV = PROJECT_ROOT / "aggregated_results.csv"

# Full evaluation: 16 inputs × 5 replicates = 80 trials
EXPECTED_TOTAL = 80


def scan_aborted_files(results_dir: Path, verbose: bool = False) -> list[Path]:
    """Find all result JSON files where summary.aborted is True."""
    aborted = []
    for json_file in sorted(results_dir.rglob("*.json")):
        try:
            with open(json_file) as f:
                data = json.load(f)
            summary = data.get("summary", {})
            if summary.get("aborted", False):
                aborted.append(json_file)
                if verbose:
                    total = summary.get("total", "?")
                    errors = summary.get("errors", "?")
                    model = summary.get("model", "?")
                    print(
                        f"  ABORTED: {json_file.relative_to(results_dir)} "
                        f"(model={model}, total={total}, errors={errors})"
                    )
        except (json.JSONDecodeError, OSError) as e:
            print(f"  WARNING: Could not read {json_file}: {e}", file=sys.stderr)
    return aborted


def scan_incomplete_files(results_dir: Path, expected_total: int, verbose: bool = False) -> list[Path]:
    """Find result JSON files with fewer trials than expected (test/smoke runs)."""
    incomplete = []
    for json_file in sorted(results_dir.rglob("*.json")):
        try:
            with open(json_file) as f:
                data = json.load(f)
            summary = data.get("summary", {})
            total = summary.get("total", 0)
            # Skip aborted files (handled separately)
            if summary.get("aborted", False):
                continue
            if total < expected_total:
                incomplete.append(json_file)
                if verbose:
                    model = summary.get("model", "?")
                    repl = summary.get("replicates", "?")
                    sample = summary.get("sample_limit", "?")
                    print(
                        f"  INCOMPLETE: {json_file.relative_to(results_dir)} "
                        f"(model={model}, total={total}/{expected_total}, "
                        f"replicates={repl}, sample_limit={sample})"
                    )
        except (json.JSONDecodeError, OSError) as e:
            print(f"  WARNING: Could not read {json_file}: {e}", file=sys.stderr)
    return incomplete


def clean_aggregated_csv(
    csv_path: Path,
    deleted_files: set[Path],
    expected_total: int,
    dry_run: bool,
    verbose: bool,
) -> dict[str, int]:
    """Clean aggregated_results.csv: remove aborted, incomplete, and orphan rows.

    Returns dict with counts: aborted, incomplete, orphan.
    """
    counts = {"aborted": 0, "incomplete": 0, "orphan": 0}
    if not csv_path.exists():
        return counts

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    kept = []
    for row in rows:
        reason = None

        # Check aborted
        if row.get("aborted", "").lower() == "yes":
            reason = "aborted"

        # Check if result_file was deleted or is missing
        if not reason:
            result_file = row.get("result_file", "")
            if result_file:
                full_path = PROJECT_ROOT / result_file
                if full_path in deleted_files:
                    reason = "incomplete"
                elif not full_path.exists():
                    reason = "orphan"

        # Check total < expected (catches rows pointing to incomplete files
        # that weren't in our deleted set, e.g. already-deleted files)
        if not reason:
            try:
                total = int(row.get("total", 0) or 0)
                if total < expected_total:
                    reason = "incomplete"
            except (ValueError, TypeError):
                pass

        if reason:
            counts[reason] = counts.get(reason, 0) + 1
            if verbose or dry_run:
                tag = "WOULD REMOVE" if dry_run else "REMOVING"
                print(
                    f"  {tag} [{reason}] CSV row: {row['model_id']} | "
                    f"{row['scenario']} | {row['approach']} | "
                    f"perturbed={row['perturbed']} | total={row.get('total', '?')}"
                )
        else:
            kept.append(row)

    if not dry_run and sum(counts.values()) > 0:
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(kept)

    return counts


def prune_empty_dirs(results_dir: Path, dry_run: bool, verbose: bool) -> int:
    """Remove empty directories under results/. Returns count removed."""
    count = 0
    # Walk bottom-up so children are removed before parents
    for dirpath in sorted(results_dir.rglob("*"), reverse=True):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            count += 1
            if verbose or dry_run:
                tag = "WOULD PRUNE" if dry_run else "PRUNING"
                print(f"  {tag} empty dir: {dirpath.relative_to(results_dir)}")
            if not dry_run:
                dirpath.rmdir()
    return count


def main():
    parser = argparse.ArgumentParser(
        description="Clean up bad evaluation results (aborted + incomplete)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete files (default is dry-run)",
    )
    parser.add_argument(
        "--expected-total",
        type=int,
        default=EXPECTED_TOTAL,
        help=f"Expected trial count per run (default: {EXPECTED_TOTAL})",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS_DIR,
        help=f"Results directory (default: {RESULTS_DIR.relative_to(PROJECT_ROOT)})",
    )
    parser.add_argument(
        "--aggregated-csv",
        type=Path,
        default=AGGREGATED_CSV,
        help=f"Aggregated CSV path (default: {AGGREGATED_CSV.name})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )
    args = parser.parse_args()

    dry_run = not args.apply
    mode_str = "DRY RUN" if dry_run else "APPLYING"

    print(f"{'='*60}")
    print(f"Clean Bad Results — {mode_str}")
    print(f"{'='*60}")

    # Step 1: Find aborted JSON files
    print(f"\n[1/5] Scanning for aborted result files...")
    aborted_files = scan_aborted_files(args.results_dir, verbose=args.verbose)
    print(f"      Found {len(aborted_files)} aborted file(s)")

    # Step 2: Find incomplete/test JSON files
    print(f"\n[2/5] Scanning for incomplete result files (total < {args.expected_total})...")
    incomplete_files = scan_incomplete_files(args.results_dir, args.expected_total, verbose=args.verbose)
    print(f"      Found {len(incomplete_files)} incomplete file(s)")

    # Step 3: Delete bad files
    all_bad_files = aborted_files + incomplete_files
    if all_bad_files:
        print(f"\n[3/5] {'Would delete' if dry_run else 'Deleting'} " f"{len(all_bad_files)} bad file(s)...")
        for f in all_bad_files:
            if args.verbose or dry_run:
                tag = "WOULD DELETE" if dry_run else "DELETING"
                print(f"  {tag}: {f.relative_to(PROJECT_ROOT)}")
            if not dry_run:
                f.unlink()
    else:
        print(f"\n[3/5] No bad files to delete")

    # Step 4: Clean aggregated CSV
    deleted_set = set(all_bad_files)
    print(f"\n[4/5] Cleaning aggregated CSV...")
    csv_counts = clean_aggregated_csv(args.aggregated_csv, deleted_set, args.expected_total, dry_run, args.verbose)
    total_csv = sum(csv_counts.values())
    print(
        f"      {'Would remove' if dry_run else 'Removed'} {total_csv} row(s): "
        f"{csv_counts['aborted']} aborted, "
        f"{csv_counts['incomplete']} incomplete, "
        f"{csv_counts['orphan']} orphan"
    )

    # Step 5: Prune empty directories
    print(f"\n[5/5] Pruning empty directories...")
    pruned_dirs = prune_empty_dirs(args.results_dir, dry_run, args.verbose)
    print(f"      {'Would prune' if dry_run else 'Pruned'} {pruned_dirs} empty dir(s)")

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY ({mode_str})")
    print(f"{'='*60}")
    print(f"  Aborted files:    {len(aborted_files)}")
    print(f"  Incomplete files: {len(incomplete_files)}")
    print(
        f"  CSV rows removed: {total_csv} "
        f"({csv_counts['aborted']}A/{csv_counts['incomplete']}I/{csv_counts['orphan']}O)"
    )
    print(f"  Empty dirs:       {pruned_dirs}")

    grand_total = len(all_bad_files) + total_csv + pruned_dirs
    if grand_total == 0:
        print(f"\n  ✓ Everything is clean — nothing to do!")
    elif dry_run:
        print(f"\n  → Re-run with --apply to execute cleanup")

    return 0


if __name__ == "__main__":
    sys.exit(main())
