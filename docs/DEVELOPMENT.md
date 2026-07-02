# Development Guide

## Quick Reference

### Running Evaluations

```bash
# Single model, single configuration
python -m nlt.cli --scenario alex --approach nlt --model llama-3.1-8b-instant --replicates 5

# Batch evaluation (recommended)
make run-models              # Run all models where run=yes, skip completed
make run-models-force        # Rerun everything
make run-models-quick        # Quick test (2 inputs, 1 replicate)

# Full study with automatic analysis
bash src/scripts/run_study.sh               # Full 2×2×2 factorial
bash src/scripts/run_study.sh --quick       # Quick test
bash src/scripts/run_study.sh --force       # Force rerun
```

### Analyzing Results

```bash
# View summary statistics
python src/scripts/analyze_results.py

# Include NLT vs Structured gains
python src/scripts/analyze_results.py --show-gains

# Export summary to CSV
python src/scripts/analyze_results.py --export summary.csv
```

### Development Tools

```bash
make format                  # Auto-format with black
make test                    # Run all unit tests
make demo                    # Quick NLT smoke test
make demo-structured         # Quick structured smoke test
```

## Project Structure

```
src/nlt/
├── __init__.py
├── cli.py                   # Command-line interface
├── api/
│   ├── __init__.py
│   └── client.py            # Sage API client (urllib only)
├── core/
│   ├── __init__.py
│   ├── evaluator.py         # Run trials and compute metrics
│   ├── parser.py            # Parse YES/NO and tool_calls
│   └── types.py             # Type definitions (dataclasses)
└── data/
    ├── __init__.py
    └── scenarios.py         # Alex/Sage prompts and schemas

tests/
├── test_parser.py           # Parser unit tests (16 tests)
└── test_evaluator.py        # Evaluator unit tests (11 tests)

results/                     # Auto-generated evaluation results
├── alex/
│   ├── nlt/
│   │   ├── non_perturbed/
│   │   │   └── {model}/
│   │   │       └── {timestamp}.json
│   │   └── perturbed/
│   └── structured/
└── sage/

models.csv                   # Model tracking with completion status
aggregated_results.csv       # All results in one CSV
run_models.py                # Batch evaluation runner
run_study.sh                 # Full study execution script
analyze_results.py           # Results analysis tool
```

## Testing Workflow

### Unit Tests

```bash
# Run all tests
make test

# Run specific test file
.venv/bin/python -m pytest tests/test_parser.py -v

# Run with coverage
.venv/bin/python -m pytest --cov=nlt --cov-report=html
```

**Test coverage:**
- `test_parser.py`: 16 tests covering NLT parsing, tool_calls parsing, exact match, statistics
- `test_evaluator.py`: 11 tests covering single trials, batch evaluation, error handling

### Integration Testing

```bash
# Quick smoke test (2 inputs, both approaches)
make demo
make demo-structured

# Test model without tool calling support
make compare-approaches      # Uses mistral-7b

# Test specific model
make test-phi-4              # Uses microsoft/phi-4
```

## Code Style

**Formatting**: Black with 120 character line length
```bash
make format                  # Auto-format all Python files
```

**Conventions:**
- Type hints on all functions
- Dataclasses for structured data (see `types.py`)
- No external dependencies (stdlib only for HTTP)
- Results auto-save as JSON with timestamps
- Exact-match grading (no partial credit)

## Adding New Models

1. Add to `models.csv`:
```csv
yes,your-model-id,provider,size,yes/no,no,no,no,no,Description
```

2. Set `run=yes` to include in batch runs

3. Run evaluation:
```bash
make run-models              # Runs only new models
```

4. Check results:
```bash
python src/scripts/analyze_results.py --show-gains
```

## Adding New Scenarios

1. Define in `src/nlt/data/scenarios.py`:
```python
NEW_SCENARIO = Scenario(
    name="new_scenario",
    system_prompt_nlt="Your NLT prompt...",
    system_prompt_structured="Your structured prompt...",
    available_tools=["Tool A", "Tool B"],
    tool_schemas=[...],          # OpenAI-style function definitions
    function_name_map={...},     # Map function names to tool names
    inputs=[...],                # Test inputs with expected tools
)
```

2. Update CLI in `src/nlt/cli.py` to include new scenario

3. Add tests in `tests/`

## CSV Tracking System

### models.csv

Tracks which models to run and completion status:

```csv
# Comments start with #
run,model_id,provider,size,has_tool_calling,alex_nlt_done,alex_structured_done,sage_nlt_done,sage_structured_done,notes
yes,model-id,provider,size,yes/no,no,no,no,no,Description
```

**Columns:**
- `run`: yes/no toggle (only `yes` models are evaluated)
- `model_id`: Full model identifier for API
- Status columns: Auto-update to `yes` after successful completion
- `notes`: Human-readable description

### aggregated_results.csv

One row per (model, scenario, approach, perturbed) combination:

```csv
model_id,scenario,approach,perturbed,accuracy,variance,total,errors,timestamp,result_file
llama-3.1-8b-instant,alex,nlt,no,0.7875,0.1673,80,0,20260112_120343,results/...
```

Auto-updated by `run_models.py` after each evaluation.

## Batch Evaluation System

**run_models.py** features:
- Reads `models.csv` and filters by `run=yes`
- Scans `results/` to skip completed evaluations
- Updates both CSVs after successful runs
- Supports `--force` to rerun everything
- Supports `--sample-limit` and `--skip-perturbed` for quick tests

**Smart skip logic:**
- Checks if (model, scenario, approach, perturbed) already has results
- Skips unless `--force` is used
- Still updates `aggregated_results.csv` for skipped runs (pulls from existing JSON)

**clean_aborted.py** handles result hygiene:
- Scans all result JSONs for `summary.aborted=True` (API failures)
- Detects incomplete test runs (`total < 80` trials)
- Removes bad files, cleans `aggregated_results.csv`, prunes empty dirs
- Always dry-run by default; pass `--apply` to execute
- Use `--expected-total N` to override the 80-trial threshold

## Results Analysis

**analyze_results.py** generates:
- Overall accuracy by approach (NLT vs Structured)
- Per-model breakdown
- Per-scenario statistics
- NLT accuracy gains (percentage point improvement)
- Optional CSV export for spreadsheet analysis

**Usage patterns:**
```bash
# Quick terminal summary
python src/scripts/analyze_results.py

# Include gain analysis
python src/scripts/analyze_results.py --show-gains

# Export for Excel/Google Sheets
python src/scripts/analyze_results.py --export summary.csv
```

## Study Execution

**Full study script (`run_study.sh`):**
1. Validates environment and auth token
2. Runs batch evaluation via `run_models.py`
3. Generates analysis with `analyze_results.py`
4. Exports summary to `study_summary.csv`

**Study design:** 2×2×2 factorial
- 2 approaches: NLT, Structured
- 2 scenarios: Alex (customer service), Sage (mental health)
- 2 perturbations: Non-perturbed, Perturbed
- 5 replicates per input (16 inputs per scenario)
- = 8 conditions × N models × 80 trials each

## Troubleshooting

### Tests failing
```bash
# Check formatting
make format

# Run specific test
.venv/bin/python -m pytest tests/test_parser.py::test_parse_nlt_output_all_yes -v
```

### API errors in results
```bash
# Check error count
python src/scripts/analyze_results.py | grep "Total Errors"

# Inspect individual result
cat results/alex/nlt/non_perturbed/model-name/*.json | jq '.results[] | select(.error != null)'

# Clean up aborted runs (e.g. after Cloudflare outage)
make clean-aborted       # Preview what would be cleaned
make clean-aborted-apply # Delete aborted files + fix aggregated CSV
```

### CSV tracking issues
```bash
# Manually check completion status
cat models.csv | grep -v "^#"

# Clean up aborted/incomplete results and fix CSV
make clean-aborted       # Dry-run first to see what would be removed
make clean-aborted-apply # Actually delete + update aggregated_results.csv
```

### Model not running
- Check `run=yes` in models.csv
- Verify model_id is correct
- Check SAGE_AUTH_TOKEN is set
- Look for errors in terminal output

## Performance Optimization

**For faster development:**
```bash
# Use sample limit
make run-models-quick        # 2 inputs, 1 replicate

# Single scenario
python -m nlt.cli --scenario alex --approach nlt --model MODEL --sample-limit 2
```

**For production runs:**
- Full replicates (5)
- All scenarios
- Both perturbation conditions
- Multiple models in parallel (not currently implemented)

## Contributing

Before committing:
1. Run `make format` to ensure consistent style
2. Run `make test` to verify all tests pass
3. Update documentation if adding features
4. Add tests for new functionality
5. Update `models.csv` if testing new models
