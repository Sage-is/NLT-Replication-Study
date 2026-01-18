# 🔥 This Week (January 16, 2026)

### 🔥 Planned: Reporting & Visualization Improvements
- [ ] **Add analysis notebook for visuals**: Build Jupyter notebook to plot per-approach/model metrics and gains
  - [ ] Generate accuracy and variance box/violin plots for NLT vs structured
  - [ ] Plot error counts and aborted runs per model
  - [ ] Export charts for reports/README/REPLICATION_STUDY
  - [ ] Test/verify step (notebook runs cleanly)
  - [ ] Documentation update (link notebook in README/docs)

### 🔥 In Progress: Fix Data Quality Issues
- [x] **Issue 1 - Misleading stats when all trials error**: Fixed accuracy/variance reporting
  - [x] When all trials error (valid_trials=0), accuracy/variance now report as `None` instead of 0.0
  - [x] Added `valid_trials` and `aborted` fields to summary and aggregated results
  - [x] Updated analysis scripts to handle None values correctly
  - [x] Updated tests for new behavior
- [ ] **Issue 2 - Early abort on repeated errors**: Implemented early stopping to save money/tokens
  - [x] Added `MAX_CONSECUTIVE_ERRORS = 5` threshold
  - [x] Evaluator now returns `(results, aborted)` tuple
  - [x] When 5+ consecutive errors occur, evaluation stops and reports "aborted"
  - [x] Aborted flag stored in aggregated results for tracking
  - [ ] Run tests and validate behavior in real evaluation
  - [ ] Monitor first run to ensure abort logic works correctly

### ✅ CSV Tracking & Batch Evaluation System - COMPLETE
- [x] **CSV Tracking System**: Build model tracking and aggregated results system
  - [x] Configure Black for linting and formatting
  - [x] Add pytest configuration
  - [x] Write parser unit tests (NLT YES/NO extraction, structured function parsing)
  - [x] Write evaluator tests (accuracy/variance calculation)
  - [x] Add CLI smoke test
  - [x] Test/verify step
  - [x] Documentation update

### 🔶 High Priority: Full Study Replication
- [ ] **Full Study Replication**: Run complete 2×2×2 factorial design across multiple models.
  - [x] Document replication methodology (REPLICATION.md)
  - [x] Create study execution script (run_study.sh)
  - [ ] Execute full evaluation (4+ models × 8 conditions × 5 replicates)
  - [x] Aggregate results and compute summary statistics (analyze_results.py)
  - [x] Add --quick and --force options to study script

### ✅ Testing Infrastructure - COMPLETE
- [x] **Testing Infrastructure**: Build comprehensive test suite
  - [x] Configure Black for linting and formatting
  - [x] Write parser unit tests (16 tests - NLT YES/NO, tool_calls, exact match, statistics)
  - [x] Write evaluator unit tests (11 tests - single trials, batch eval, error handling)
  - [x] Add pytest configuration to pyproject.toml
  - [x] Add test and test-coverage Makefile targets
  - [x] All tests passing

### ✅ Documentation Overhaul - COMPLETE
- [x] **Comprehensive Documentation**: Update all docs with new CSV/batch workflow
  - [x] Update README with batch evaluation section
  - [x] Update README with Makefile targets reference
  - [x] Overhaul REPLICATION.md with CSV-first workflow
  - [x] Add results organization section (3 CSVs + JSON files)
  - [x] Create DEVELOPMENT.md with developer guide
  - [x] Add troubleshooting and performance optimization guides
  - [x] Document CSV tracking system thoroughly
# Week of January 11, 2026

## 🔥 This Week (January 11, 2026)
### ✅ NLT MVP codebase setup - COMPLETE
- [x] **NLT MVP codebase setup**: Scaffold a clean Python package for the Natural Language Tools framework and sample scenarios.
  - [x] Define package layout (core modules for prompts, parsing, orchestration, and sample data)
  - [x] Implement selector/parser pipeline skeleton with Alex/Sage scenarios
  - [x] Add CLI demo for running a selector and parser pass
  - [x] Multi-model support with organized result storage
  - [x] Test/verify step - smoke tests passing
  - [x] Documentation update
✅ High Priority: Linting & Testing - COMPLETE
- [x] **Linting & Testing**: Add Black for linting/formatting and pytest for unit tests.
  - [x] Configure Black for linting and formatting
  - [x] Add pytest configuration
  - [x] Write parser unit tests (NLT YES/NO extraction, structured function parsing)
  - [x] Write evaluator tests (accuracy/variance calculation)
  - [x] Add CLI smoke test
  - [x] Test/verify step
  - [x] Documentation update

### ✅ High Priority: Full Study Replication - COMPLETE (Preparation Phase)
- [x] **Full Study Replication**: Run complete 2×2×2 factorial design across multiple models.
  - [x] Document replication methodology (REPLICATION.md)
  - [x] Create study execution script (run_study.sh)
  - [x] Create aggregation tools (analyze_results.py)
  - [ ] Execute full evaluation (4+ models × 8 conditions × 5 replicates) - IN PROGRESS
  - [ ] Compare with original paper findings - PENDING RESULTS
  - [ ] Document model-specific insights - PENDING RESULTSings
  - [ ] Document model-specific insights

### ✅ Environment & tooling (uv) - COMPLETE
- [x] **Environment & tooling (uv)**: Initialize Python project with uv and add core dependencies and lint/test tooling.
  - [x] Initialize uv project metadata and dependencies
  - [x] Make package importable (editable install / packaging metadata)
  - [x] Document autoenv integration in CONVENTION.md

### ✅ Docs & README - COMPLETE
- [x] **Docs & README**: Document architecture, usage, and examples derived from the NLT paper.
  - [x] Draft README with quickstart and architecture overview
  - [x] Add example prompts/output formats for Alex and Sage
  - [x] Create REPLICATION.md for full study meth

## Previous Weeks

### Week of January 11, 2026odology
  - [x] Update CONVENTION.md with autoenv details
