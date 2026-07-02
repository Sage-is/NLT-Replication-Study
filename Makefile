.PHONY: setup demo demo-structured compare-approaches test-phi-4 test-deepseek-r1 test-deepseek-r1-debug run-models run-models-force run-models-quick run-models-debug eval analyze arxiv clean-results clean-aborted help clean test format

# Default target
all: help

help:
	@echo "Available commands:"
	@echo "  make setup               - Create virtual environment and install dependencies"
	@echo "  make demo                - Run a quick smoke test (Alex scenario, NLT approach)"
	@echo "  make demo-structured     - Run a quick smoke test (Alex scenario, tool calling)"
	@echo "  make compare-approaches  - Compare NLT vs structured on mistral-7b (no tool support)"
	@echo "  make test-phi-4          - Test microsoft/phi-4 with both approaches"
	@echo "  make test-deepseek-r1    - Test deepseek/deepseek-r1 with extended timeout"
	@echo "  make test-deepseek-r1-debug - Test deepseek/deepseek-r1 with full debug output"
	@echo "  make run-models          - Run evaluations for models in CSV (skip completed)"
	@echo "  make run-models-force    - Run all models in CSV (rerun completed)"
	@echo "  make run-models-quick    - Quick test run (2 inputs, 1 replicate, no perturbed)"
	@echo "  make run-models-debug    - Run evaluations with verbose debug output"
	@echo "  make eval                - Run full evaluation (custom args supported)"
	@echo "  make analyze             - Analyze aggregated results and show NLT gains"
	@echo "  make arxiv               - Convert REPLICATION_STUDY.md to arXiv LaTeX package"
	@echo "  make clean-results       - Remove results for specific models (use MODELS=model1,model2)"
	@echo "  make clean-aborted       - Remove aborted results, orphan CSV rows, empty dirs (dry-run)"
	@echo "  make clean-aborted-apply - Actually apply cleanup (delete files)"
	@echo "  make format              - Auto-format code with black"
	@echo "  make test                - Run pytest test suite"
	@echo "  make clean               - Remove build artifacts and virtual environment"

setup:
	@echo "Creating virtual environment..."
	uv venv
	@echo "Installing package in editable mode..."
	uv pip install -e .
	@echo "Installing dev dependencies..."
	uv pip install black pytest

demo:
	@echo "Running smoke test (NLT approach)..."
	uv run python -m nlt.cli --scenario alex --approach nlt --replicates 1 --sample-limit 2

demo-structured:
	@echo "Running smoke test (tool calling approach)..."
	uv run python -m nlt.cli --scenario alex --approach structured --replicates 1 --sample-limit 2

eval:
	@echo "Running evaluation..."
	uv run python -m nlt.cli $(ARGS)

format:
	@echo "Formatting code with black..."
	uv run black src tests

test:
	@echo "Running pytest..."
	uv run pytest

compare-approaches:
	@echo "Comparing NLT vs Structured on mistralai/mistral-7b-instruct:free (no native tool calling)..."
	@echo ""
	@echo "=== NLT Approach (text-based YES/NO parsing) ==="
	uv run python -m nlt.cli --scenario alex --approach nlt --model mistralai/mistral-7b-instruct:free --sample-limit 2 --replicates 1
	@echo ""
	@echo "=== Structured Approach (requires tool_calls - should get 0% accuracy) ==="
	uv run python -m nlt.cli --scenario alex --approach structured --model mistralai/mistral-7b-instruct:free --sample-limit 2 --replicates 1

test-phi-4:
	@echo "Testing microsoft/phi-4 with both approaches..."
	@echo ""
	@echo "=== NLT Approach ==="
	uv run python -m nlt.cli --scenario alex --approach nlt --model microsoft/phi-4 --sample-limit 2 --replicates 1
	@echo ""
	@echo "=== Structured Approach ==="
	uv run python -m nlt.cli --scenario alex --approach structured --model microsoft/phi-4 --sample-limit 2 --replicates 1

test-deepseek-r1:
	@echo "Testing deepseek/deepseek-r1 with extended timeout (10 minutes)..."
	@echo ""
	@echo "=== NLT Approach (DeepSeek R1 is very large - may take several minutes) ==="
	uv run python -m nlt.cli --scenario alex --approach nlt --model deepseek/deepseek-r1 --sample-limit 1 --replicates 1 --timeout 600

test-deepseek-r1-debug:
	@echo "Testing deepseek/deepseek-r1 with DEBUG output enabled..."
	@echo ""
	@echo "=== NLT Approach with full debug logging ==="
	uv run python -m nlt.cli --scenario alex --approach nlt --model deepseek/deepseek-r1 --sample-limit 1 --replicates 1 --timeout 600 --debug --verbose

run-models:
	@echo "Running evaluations from models.csv (skip completed)..."
	uv run python src/scripts/run_models.py --timeout 600 --verbose

run-models-force:
	@echo "Running ALL evaluations from models.csv (rerun completed)..."
	uv run python src/scripts/run_models.py --force --timeout 600 --verbose

run-models-quick:
	@echo "Quick test run (2 inputs, 1 replicate, no perturbed)..."
	uv run python src/scripts/run_models.py --sample-limit 2 --replicates 1 --skip-perturbed --timeout 300

run-models-debug:
	@echo "Running evaluations with DEBUG output (verbose logging)..."
	uv run python src/scripts/run_models.py --timeout 600 --debug --verbose
analyze:
	@echo "Analyzing results..."
	uv run python src/scripts/analyze_results.py --show-gains

arxiv:
	@echo "Converting REPLICATION_STUDY.md to arXiv LaTeX package..."
	uv run python src/scripts/md_to_arxiv.py

clean-results:
	@if [ -z "$(MODELS)" ]; then \
		echo "Error: MODELS variable not set"; \
		echo "Usage: make clean-results MODELS='model1,model2'"; \
		exit 1; \
	fi
	@echo "Removing results for models: $(MODELS)"
	@cp aggregated_results.csv aggregated_results.csv.bak
	@for model in $(subst comma, ,$(MODELS)); do \
		echo "Cleaning $$model..."; \
		safe_model=$$(echo "$$model" | tr '/:' '__'); \
		find results -type d -name "*$$safe_model*" -exec rm -rf {} + 2>/dev/null || true; \
		grep -F -v "$$model" aggregated_results.csv > aggregated_results.csv.tmp && mv aggregated_results.csv.tmp aggregated_results.csv; \
	done
	@rm -f aggregated_results.csv.bak
	@echo "Done. You can now run 'make run-models' to re-evaluate or 'make analyze' to regenerate analysis."

clean-aborted:
	@echo "Scanning for aborted results (dry run)..."
	uv run python src/scripts/clean_aborted.py -v

clean-aborted-apply:
	@echo "Cleaning up aborted results..."
	uv run python src/scripts/clean_aborted.py --apply -v

clean:
	rm -rf .venv
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
