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

### Single Configuration Example
```bash
# NLT approach, Alex scenario, non-perturbed, 5 replicates
.venv/bin/python -m nlt.cli \
  --scenario alex \
  --approach nlt \
  --model llama-3.1-8b-instant \
  --replicates 5
```

### Full Factorial Design

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

### Batch Evaluation with Multiple Models

```bash
# Test multiple models in one command
.venv/bin/python -m nlt.cli \
  --scenario alex \
  --approach nlt \
  --models llama-3.1-8b-instant google/gemini-2.5-flash-lite \
  --replicates 5 \
  --delay-seconds 0.5
```

## Results Organization

Results auto-save to:
```
results/
  {scenario}/          # alex or sage
    {approach}/        # nlt or structured
      {perturbed}/     # perturbed or non_perturbed
        {model}/       # sanitized model name
          {timestamp}.json
```

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

### Aggregate Results Across Models

```bash
# Example: Collect all NLT accuracy scores for Alex scenario
find results/alex/nlt/non_perturbed -name "*.json" \
  -exec jq -r '"\(.summary.model): \(.summary.accuracy)"' {} \;
```

### Compare NLT vs Structured

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

Always validate with a small sample first:

```bash
# Quick 2-input test across all conditions
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
