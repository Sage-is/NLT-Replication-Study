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
  --auth-token "$SAGE_TOKEN" \
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

## Documentation
- [REPLICATION.md](docs/REPLICATION.md) - Complete guide to replicating the full NLT study
- [DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md) - Startr development standards

## Notes
- The harness uses only Python's standard library (urllib) for HTTP calls.
- NLT parsing expects the YES/NO grid shown in the prompts. Structured parsing looks for the documented `check_*` function names in the model output.
- Dataset, prompts, and expected tool calls are defined in code under `src/nlt/data/scenarios.py`.
- Results auto-save to `results/{scenario}/{approach}/{perturbed}/{model}/{timestamp}.json`.
