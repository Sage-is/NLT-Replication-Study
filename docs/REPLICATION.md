# Replicating the NLT Study

This guide explains how to replicate the Natural Language Tools evaluation study using Sage-hosted models.

## Study Design Overview

The original study used a **2 × 2 × 2 factorial design**:
- **Approach**: NLT vs. Structured tool calling
- **Scenario**: Alex (customer service) vs. Sage (mental health)
- **Perturbation**: Non-perturbed vs. Perturbed prompts

Each scenario contains **16 synthetic user inputs** covering:
- Zero-tool cases (no tools needed)
- Single-tool cases
- Multi-tool parallel selection cases

**Replication count**: 5 independent API calls per input (as per original paper)

**Evaluation**: Exact-match grading (no partial credit)

## Model Selection

The original paper evaluated 10 like-for-like models. For Sage-hosted replication, we recommend:

### Tested Models (validated on Sage)
```
llama-3.1-8b-instant
google/gemini-2.5-flash-lite
deepseek/deepseek-r1-0528-qwen3-8b
xiaomi/mimo-v2-flash:free
```

### Additional Sage Models (check availability)
Query Sage for current models:
```bash
curl -s https://sage.startr.cloud/api/models \
  -H "Authorization: Bearer $SAGE_AUTH_TOKEN" | \
  python -m json.tool | grep '"id"'
```

## Running the Full Study

### Quick Start with CSV Batch System (recommended)

The batch runner reads `models.csv`, runs every enabled model across all 8 conditions, and updates the result CSVs as it goes.

**1. Choose which models to run:**
Set `run=yes` for the models you want in `models.csv` (and `run=no` to skip).

**2. Run batch evaluation:**
```bash
# Run all models where run=yes, skip completed evaluations
make run-models

# Force rerun everything (ignores completion status)
make run-models-force

# Quick smoke test (2 inputs, 1 replicate, non-perturbed only)
make run-models-quick
```

**3. Analyze results:**
```bash
# View summary statistics
python src/scripts/analyze_results.py

# Show NLT gains over structured approach
python src/scripts/analyze_results.py --show-gains

# Export summary to CSV
python src/scripts/analyze_results.py --export summary.csv
```

**4. Track progress:**
- `models.csv` - Shows which scenario/approach combinations are complete per model
- `aggregated_results.csv` - All evaluation summaries in one file
- `results/` directory - Individual JSON files with full details

**5. Clean up bad runs (if needed):**
```bash
make clean-aborted        # Dry-run: see what's broken
make clean-aborted-apply  # Fix it: delete bad files + update CSV
make run-models           # Re-queue cleaned conditions
```

### Alternative: Shell Script Wrapper

For a complete study run with automatic analysis:
```bash
# Full study (5 replicates, all perturbations)
bash src/scripts/run_study.sh

# Quick test run
bash src/scripts/run_study.sh --quick

# Force rerun everything
bash src/scripts/run_study.sh --force
```

This script:
1. Runs all enabled models from models.csv
2. Executes all 8 conditions per model (2×2×2 factorial)
3. Aggregates results
4. Generates summary statistics and exports to CSV

### Manual Single Configuration

For running individual configurations (useful for debugging):
```bash
# NLT approach, Alex scenario, non-perturbed, 5 replicates
.venv/bin/python -m nlt.cli \
  --scenario alex \
  --approach nlt \
  --model llama-3.1-8b-instant \
  --replicates 5
```

### Legacy: Full Factorial Design Script

> **Note**: The CSV batch system above is now the recommended approach. This manual script is kept for reference.

Run all 8 conditions per model (2 scenarios × 2 approaches × 2 perturbations):

```bash
#!/bin/bash
# save as: run_full_study.sh

MODELS=(
  "llama-3.1-8b-instant"
  "google/gemini-2.5-flash-lite"
  "deepseek/deepseek-r1-0528-qwen3-8b"
  "xiaomi/mimo-v2-flash:free"
)

SCENARIOS=("alex" "sage")
APPROACHES=("nlt" "structured")
REPLICATES=5

for model in "${MODELS[@]}"; do
  for scenario in "${SCENARIOS[@]}"; do
    for approach in "${APPROACHES[@]}"; do
      # Non-perturbed
      .venv/bin/python -m nlt.cli \
        --scenario "$scenario" \
        --approach "$approach" \
        --model "$model" \
        --replicates $REPLICATES \
        --delay-seconds 0.5

      # Perturbed
      .venv/bin/python -m nlt.cli \
        --scenario "$scenario" \
        --approach "$approach" \
        --model "$model" \
        --replicates $REPLICATES \
        --perturbed \
        --delay-seconds 0.5
    done
  done
done

echo "Study complete. Results saved to results/"
```

**Usage**:
```bash
chmod +x run_full_study.sh
./run_full_study.sh
```

**Expected runtime**: ~15-30 minutes per model (depends on API latency and rate limits)

## Results Organization

The batch system maintains three result locations.

### 1. Individual JSON Files
```
results/
  {scenario}/          # alex or sage
    {approach}/        # nlt or structured
      {perturbed}/     # perturbed or non_perturbed
        {model}/       # sanitized model name
          {timestamp}.json
```

### 2. Aggregated Results CSV

`aggregated_results.csv` contains one row per (model, scenario, approach, perturbed) combination:
```csv
model_id,scenario,approach,perturbed,accuracy,variance,total,errors,timestamp,result_file
llama-3.1-8b-instant,alex,nlt,no,0.7875,0.1673,80,0,20260112_120343,results/alex/nlt/non_perturbed/llama-3.1-8b-instant/20260112_120343.json
```

This file is automatically updated by `run_models.py` after each evaluation.

### 3. Model Tracking CSV

`models.csv` tracks completion status:
```csv
run,model_id,provider,size,has_tool_calling,alex_nlt_done,alex_structured_done,sage_nlt_done,sage_structured_done,notes
yes,llama-3.1-8b-instant,meta,8b,yes,yes,yes,no,no,Llama 3.1 with tool calling
```

Status columns automatically update to `yes` after successful completion.

### Result File Format

Each JSON file contains:
```json
{
  "summary": {
    "accuracy": 0.875,
    "variance": 0.0121,
    "total": 80,
    "errors": 0,
    "scenario": "alex",
    "approach": "nlt",
    "perturbed": false,
    "model": "llama-3.1-8b-instant",
    "replicates": 5
  },
  "results": [
    {
      "input_id": 1,
      "expected_tools": ["Website information", "Past Purchases"],
      "predicted_tools": ["Website information", "Past Purchases"],
      "success": true,
      "raw_output": "...",
      "usage": {
        "prompt_tokens": 500,
        "completion_tokens": 120,
        "total_tokens": 620
      }
    }
  ]
}
```

## Analysis

### Using analyze_results.py (recommended)

```bash
# View summary statistics
python src/scripts/analyze_results.py

# Include NLT vs Structured gains
python src/scripts/analyze_results.py --show-gains

# Export to CSV for spreadsheet analysis
python src/scripts/analyze_results.py --export summary.csv
```

**Output includes:**
- Overall accuracy by approach (NLT vs Structured)
- Per-model breakdown with both approaches
- Per-scenario statistics
- NLT accuracy gains (percentage point improvement over structured)

**Example output:**
```
================================================================================
SUMMARY BY APPROACH
================================================================================

NLT:
  Evaluations: 8
  Mean Accuracy: 78.8%
  Mean Variance: 0.1673
  Total Errors: 0

STRUCTURED:
  Evaluations: 8
  Mean Accuracy: 62.5%
  Mean Variance: 0.2341
  Total Errors: 2
```

### Manual Analysis with CSV

Use standard CSV tools to analyze `aggregated_results.csv`:

```bash
# Filter to NLT results only
grep ",nlt," aggregated_results.csv

# Calculate mean accuracy for a specific model
grep "llama-3.1-8b-instant" aggregated_results.csv | \
  awk -F',' '{sum+=$5; count++} END {print sum/count}'

# Find all errors
awk -F',' '$8 > 0' aggregated_results.csv
```

### Manual Analysis with JSON Files

Collect NLT accuracy scores for a single scenario:
```bash
# Example: Collect all NLT accuracy scores for Alex scenario
find results/alex/nlt/non_perturbed -name "*.json" \
  -exec jq -r '"\(.summary.model): \(.summary.accuracy)"' {} \;
```

Compare NLT vs Structured across all runs:
```python
import json
from pathlib import Path
from collections import defaultdict

def analyze_results(results_dir="results"):
    """Compare NLT vs Structured approaches."""
    accuracies = defaultdict(lambda: {"nlt": [], "structured": []})

    for json_file in Path(results_dir).rglob("*.json"):
        with open(json_file) as f:
            data = json.load(f)

        model = data["summary"]["model"]
        approach = data["summary"]["approach"]
        accuracy = data["summary"]["accuracy"]

        accuracies[model][approach].append(accuracy)

    for model, approaches in accuracies.items():
        nlt_mean = sum(approaches["nlt"]) / len(approaches["nlt"])
        struct_mean = sum(approaches["structured"]) / len(approaches["structured"])
        gain = nlt_mean - struct_mean

        print(f"{model}:")
        print(f"  NLT: {nlt_mean:.2%}")
        print(f"  Structured: {struct_mean:.2%}")
        print(f"  Gain: {gain:+.2%}")
        print()

if __name__ == "__main__":
    analyze_results()
```

## Rate Limiting

If you encounter rate limits:
1. Increase `--delay-seconds` (e.g., `--delay-seconds 1.0`)
2. Run models sequentially instead of using `--models`
3. Use `--sample-limit` for initial testing

## Smoke Testing Before Full Run

Always validate setup with a small sample first:

```bash
# Quick test via Makefile (recommended)
make run-models-quick

# Or manual CLI test across all conditions
for scenario in alex sage; do
  for approach in nlt structured; do
    .venv/bin/python -m nlt.cli \
      --scenario "$scenario" \
      --approach "$approach" \
      --model llama-3.1-8b-instant \
      --sample-limit 2 \
      --replicates 1
  done
done
```

**Checklist before full run:**
- [ ] `SAGE_AUTH_TOKEN` is set in `.env`
- [ ] Virtual environment is activated
- [ ] Quick test runs without errors
- [ ] Results appear in `results/` directory
- [ ] `models.csv` has correct models with `run=yes`

## Expected Outcomes (Original Paper)

### Overall Results
- **NLT accuracy**: 87.5% (avg across all models)
- **Structured accuracy**: 69.1%
- **Net gain**: +18.4 percentage points

### Variance Reduction
- **Structured variance**: 0.0411 (SD = 20.28 pp)
- **NLT variance**: 0.0121 (SD = 10.99 pp)

### Domain Differences
- **Alex (customer service)**: Higher accuracy overall
- **Sage (mental health)**: More challenging (safety tools, boundary setting)

### Perturbation Robustness
- **Non-perturbed NLT**: +21.2 pp gain
- **Perturbed NLT**: +15.4 pp gain (still significant)

## Troubleshooting

### Cleaning Up Failed Runs

If API outages (e.g. Cloudflare blocks) or interrupted runs leave bad data:

```bash
# Preview what would be cleaned (safe, no changes)
make clean-aborted

# Delete aborted/incomplete files, fix aggregated CSV, prune empty dirs
make clean-aborted-apply
```

This detects:
- **Aborted runs** — `summary.aborted=True` (all trials errored)
- **Incomplete runs** — test/smoke results with `total < 80` trials
- **Orphan CSV rows** — `aggregated_results.csv` entries with missing files

After cleanup, `make run-models` will re-queue the cleaned conditions.

### Model Not Found
- Check available models via Sage API
- Verify model name format (provider/model-name)

### Low Accuracy
- Inspect raw outputs in JSON files
- Check parser is extracting YES/NO correctly
- Verify prompts match scenario expectations

### API Errors
- Check `SAGE_AUTH_TOKEN` is valid
- Review error field in results JSON
- Increase delay between requests

## Next Steps

After collecting results:
1. Aggregate summaries per model
2. Calculate mean accuracy and variance per approach
3. Generate comparison tables and charts
4. Document model-specific findings
5. Compare with original paper results
