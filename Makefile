.PHONY: setup demo eval help clean test format

# Default target
all: help

help:
	@echo "Available commands:"
	@echo "  make setup       - Create virtual environment and install dependencies"
	@echo "  make demo        - Run a quick smoke test (Alex scenario, NLT approach)"
	@echo "  make eval        - Run full evaluation (custom args supported)"
	@echo "  make format      - Auto-format code with black"
	@echo "  make test        - Run pytest test suite"
	@echo "  make clean       - Remove build artifacts and virtual environment"

setup:
	@echo "Creating virtual environment..."
	uv venv
	@echo "Installing package in editable mode..."
	uv pip install -e .
	@echo "Installing dev dependencies..."
	uv pip install black pytest

demo:
	@echo "Running smoke test..."
	.venv/bin/python -m nlt.cli --scenario alex --approach nlt --replicates 1 --sample-limit 2

eval:
	@echo "Running evaluation..."
	.venv/bin/python -m nlt.cli $(ARGS)

format:
	@echo "Formatting code with black..."
	.venv/bin/black src tests

test:
	@echo "Running pytest..."
	.venv/bin/pytest

clean:
	rm -rf .venv
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
