from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from nlt.api.client import DEFAULT_API_URL, DEFAULT_MODEL, SageClient
from nlt.core import evaluator
from nlt.data.scenarios import SCENARIOS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run NLT evaluation harness against Sage API")
    parser.add_argument("--auth-token", required=False, help="Sage API bearer token")
    parser.add_argument("--model", default=None, help="Target model name (single model)")
    parser.add_argument("--models", nargs="+", default=None, help="List of models to evaluate")
    parser.add_argument("--scenario", choices=SCENARIOS.keys(), required=True, help="Scenario to evaluate")
    parser.add_argument("--approach", choices=["nlt", "structured"], required=True, help="Prompting approach")
    parser.add_argument("--perturbed", action="store_true", help="Use perturbed prompts")
    parser.add_argument("--replicates", type=int, default=1, help="Number of runs per input")
    parser.add_argument("--sample-limit", type=int, default=None, help="Optional cap on number of inputs")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="Override API base URL")
    parser.add_argument("--delay-seconds", type=float, default=0.0, help="Sleep between requests to avoid rate limits")
    parser.add_argument("--output-dir", default="results", help="Directory to save results")
    parser.add_argument("--no-save", action="store_true", help="Skip saving results to disk")
    parser.add_argument("--timeout", type=int, default=300, help="API timeout in seconds (default: 300)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging (includes API requests/responses)")
    return parser.parse_args()


def save_results(
    results: list[Any],
    summary: dict[str, Any],
    output_dir: str,
    scenario: str,
    approach: str,
    perturbed: bool,
    model: str,
) -> Path:
    """Save results to organized directory structure."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    perturb_str = "perturbed" if perturbed else "non_perturbed"

    # Create directory structure: results/{scenario}/{approach}/{perturb_str}/{model}/
    safe_model = model.replace("/", "_").replace(":", "_")
    output_path = Path(output_dir) / scenario / approach / perturb_str / safe_model
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"{timestamp}.json"
    filepath = output_path / filename

    serializable_results = []
    for r in results:
        d = r.__dict__.copy()
        d["expected_tools"] = list(d["expected_tools"])
        d["predicted_tools"] = list(d["predicted_tools"])
        d["usage"] = r.usage.__dict__ if r.usage else {}
        serializable_results.append(d)

    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "summary": summary,
                "results": serializable_results,
                "timestamp": timestamp,
            },
            fh,
            indent=2,
        )

    return filepath


def main() -> None:
    args = parse_args()

    auth_token = args.auth_token or os.getenv("SAGE_AUTH_TOKEN")
    if not auth_token:
        print("Missing auth token. Pass --auth-token or set SAGE_AUTH_TOKEN.", file=sys.stderr)
        sys.exit(1)

    # Determine models to evaluate
    if args.models:
        models = args.models
    elif args.model:
        models = [args.model]
    else:
        models = [DEFAULT_MODEL]

    scenario = SCENARIOS[args.scenario]
    client = SageClient(auth_token=auth_token, api_url=args.api_url, timeout=args.timeout, debug=args.debug)

    all_summaries = []

    for model in models:
        print(f"\n{'=' * 60}", file=sys.stderr)
        print(f"Evaluating model: {model}", file=sys.stderr)
        print(f"{'=' * 60}\n", file=sys.stderr)

        results = evaluator.evaluate(
            client=client,
            scenario=scenario,
            approach=args.approach,
            perturbed=args.perturbed,
            replicates=args.replicates,
            model=model,
            sample_limit=args.sample_limit,
            delay_seconds=args.delay_seconds,
            verbose=args.verbose,
        )

        summary: dict[str, Any] = evaluator.summarize(results)
        summary.update(
            {
                "scenario": scenario.name,
                "approach": args.approach,
                "perturbed": args.perturbed,
                "model": model,
                "replicates": args.replicates,
                "sample_limit": args.sample_limit,
                "api_url": args.api_url,
            }
        )

        print(json.dumps(summary, indent=2))
        all_summaries.append(summary)

        if not args.no_save:
            filepath = save_results(
                results=results,
                summary=summary,
                output_dir=args.output_dir,
                scenario=scenario.name,
                approach=args.approach,
                perturbed=args.perturbed,
                model=model,
            )
            print(f"\nResults saved to: {filepath}", file=sys.stderr)

    # Print aggregate summary if multiple models
    if len(models) > 1:
        print(f"\n{'=' * 60}", file=sys.stderr)
        print("AGGREGATE SUMMARY", file=sys.stderr)
        print(f"{'=' * 60}\n", file=sys.stderr)
        for s in all_summaries:
            print(f"{s['model']}: {s['accuracy']:.2%} accuracy, {s['errors']} errors", file=sys.stderr)


if __name__ == "__main__":
    main()
