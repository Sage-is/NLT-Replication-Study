#!/bin/bash
# Full NLT study execution script
#
# This script runs the complete 2×2×2 factorial design:
#   - 2 approaches (NLT, structured)  
#   - 2 scenarios (alex, sage)
#   - 2 perturbation conditions (perturbed, non-perturbed)
#   - 5 replicates per input
#   - All models in models.csv where run=yes
#
# Usage:
#   ./run_study.sh              # Full study (5 replicates)
#   ./run_study.sh --quick      # Quick test (2 inputs, 1 replicate)
#   ./run_study.sh --force      # Rerun everything, ignore completion status

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Parse arguments
FORCE=""
QUICK=""

for arg in "$@"; do
    case $arg in
        --force)
            FORCE="--force"
            shift
            ;;
        --quick)
            QUICK="--sample-limit 2 --replicates 1 --skip-perturbed"
            shift
            ;;
        *)
            echo "Unknown argument: $arg"
            echo "Usage: $0 [--quick] [--force]"
            exit 1
            ;;
    esac
done

echo "========================================="
echo "NLT Study Execution"
echo "========================================="
echo "Started: $(date)"
echo ""

# Ensure environment is set up
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found. Run 'make setup' first."
    exit 1
fi

# Check for auth token
if [ -z "${SAGE_AUTH_TOKEN:-}" ]; then
    echo "ERROR: SAGE_AUTH_TOKEN not set. Create .env with your token."
    exit 1
fi

echo "Configuration:"
echo "  Force rerun: ${FORCE:-no}"
echo "  Quick mode: ${QUICK:-no (full study)}"
echo ""

# Run evaluations using the batch runner
./run_models.py $FORCE $QUICK

# Analyze results
echo ""
echo "========================================="
echo "Generating Analysis"
echo "========================================="
echo ""

if [ -f "aggregated_results.csv" ]; then
    ./analyze_results.py --show-gains --export study_summary.csv
    
    echo ""
    echo "========================================="
    echo "Study Complete"
    echo "========================================="
    echo "Finished: $(date)"
    echo ""
    echo "Results saved to:"
    echo "  - Individual runs: results/{scenario}/{approach}/{perturbed}/{model}/*.json"
    echo "  - Aggregated data: aggregated_results.csv"
    echo "  - Summary stats: study_summary.csv"
else
    echo "WARNING: aggregated_results.csv not found. Check for errors above."
    exit 1
fi
