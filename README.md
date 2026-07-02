# Natural Language Tools (NLT) Harness

This repository provides a minimal, dependency-free evaluation harness for Natural Language Tools (NLT) against the Sage API. It supports both NLT and structured-style prompts, ships the Alex and Sage scenarios, and computes accuracy/variance over multiple replications.

## Prerequisites
- Python 3.10+
- `uv` for environment management (no third-party packages are required).
- A Sage API token with access to the target models.

## Quickstart
1) Create and activate an environment with uv:
```bash
uv venv
source .venv/bin/activate
```
2) Install the package in editable mode (ensures `nlt` is importable):
```bash
uv pip install -e .
```

3) Run the CLI (token loads from .env if you use autoenv/direnv):
```bash
python -m nlt.cli \
  --auth-token "$SAGE_AUTH_TOKEN" \
  --model "llama-3.1-8b-instant" \
  --scenario alex \
  --approach nlt \
  --replicates 1
```

## CLI options
- `--auth-token` (required): Sage bearer token.
- `--model` (default: `llama-3.1-8b-instant`): any Sage-supported model.
- `--scenario` (`alex`|`sage`).
- `--approach` (`nlt`|`structured`).
- `--perturbed` flag: use perturbed prompts.
- `--replicates` (default: 1): number of independent runs per input.
- `--sample-limit`: run only the first N inputs (useful for smoke tests).
- `--api-url` (default: `https://sage.startr.cloud/api/chat/completions`).

## Batch Evaluation

### Model Tracking (models.csv)
Models are tracked in [models.csv](models.csv) with completion status:
```csv
run,model_id,provider,size,has_tool_calling,alex_nlt_done,alex_structured_done,sage_nlt_done,sage_structured_done,notes
yes,llama-3.1-8b-instant,meta,8b,yes,no,no,no,no,Llama 3.1 with tool calling
```

- Set `run=yes` to include model in batch runs, `run=no` to skip
- Status columns automatically update to `yes` after successful completion
- Lines starting with `#` are comments

### Running Batch Evaluations
```bash
make run-models         # Run all models where run=yes, skip completed
make run-models-force   # Rerun all models where run=yes
make run-models-quick   # Quick test with 2 inputs, 1 replicate
```

### Cleaning Up Bad Results
If runs are interrupted (e.g. API outages, Cloudflare blocks) or stale test/smoke runs remain:
```bash
make clean-aborted       # Dry-run — shows what would be cleaned
make clean-aborted-apply # Actually delete bad files + update CSV
```

This removes:
- **Aborted runs** — all trials errored (`summary.aborted=True`)
- **Incomplete runs** — test/smoke runs with `total < 80` trials
- **Orphan CSV rows** — entries pointing to deleted result files
- **Empty directories** — leftover from deleted results

### Results Analysis
Results are aggregated in `aggregated_results.csv` with accuracy/variance per (model, scenario, approach, perturbed).

View summary statistics:
```bash
python src/scripts/analyze_results.py                    # Print summary to terminal
python src/scripts/analyze_results.py --show-gains       # Include NLT vs Structured gains
python src/scripts/analyze_results.py --export summary.csv  # Export to CSV
```

For charts (accuracy/variance distributions, per-model error and abort counts, token usage,
NLT gains), see [notebooks/analysis_visuals.ipynb](notebooks/analysis_visuals.ipynb) —
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Sage-is/NLT-Replication-Study/blob/develop/notebooks/analysis_visuals.ipynb).
Runs locally, on Colab, or on Kaggle (falls back to downloading `aggregated_results.csv` from
GitHub when the repo isn't checked out locally); figures save to `results/figures/`.

## Documentation
- [REPLICATION.md](docs/REPLICATION.md) - Complete guide to replicating the full NLT study
- [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Developer guide with tools, testing, and workflow
- [DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md) - Startr development standards

## Makefile Targets

```bash
make setup               # Create venv and install dependencies
make demo                # Quick NLT smoke test
make demo-structured     # Quick structured tool calling test
make run-models          # Batch evaluation (skip completed)
make run-models-force    # Batch evaluation (rerun all)
make run-models-quick    # Quick test (2 inputs, 1 replicate)
make clean-aborted       # Dry-run: show aborted/incomplete results to clean
make clean-aborted-apply # Delete bad results, clean CSV, prune dirs
make format              # Auto-format with black
make test                # Run pytest suite
make clean               # Remove build artifacts
```

See `make help` for full list.

## Notes
- The harness uses only Python's standard library (urllib) for HTTP calls.
- NLT parsing expects the YES/NO grid shown in the prompts. Structured parsing looks for the documented `check_*` function names in the model output.
- Dataset, prompts, and expected tool calls are defined in code under `src/nlt/data/scenarios.py`.
- Results auto-save to `results/{scenario}/{approach}/{perturbed}/{model}/{timestamp}.json`.
