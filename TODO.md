# TODO - NLT Replication Study

> **Convention** — Sections below map to kanban columns. Inline source-code
> tags use the same vocabulary so items stay cross-referenced between this
> file and the codebase. `KANBAN.canvas` auto-generates from this file and
> inline tags — do not hand-edit it.
>
> | Column      | Markdown section  | Inline tag  |
> |-------------|-------------------|-------------|
> | Backlog     | `## Backlog`      |             |
> | TODO        | `## TODO`         | `# TODO:`   |
> | In Progress | `## In Progress`  | `# FIXME:`  |
> | Bugs        | `## Bugs`         | `# BUG:`    |
> | Done        | `- [x]` items / `## Done` | —   |
>
> `# DEPRECATED:` tags should be tracked as TODO items for removal at the
> stated version.

## In Progress

- [ ] **🔶 Re-run live API smoke test once a fresh SAGE_AUTH_TOKEN is provisioned**
  - [ ] Create `.env` with valid `SAGE_AUTH_TOKEN`
  - [ ] `make demo` and `make demo-structured` (live round-trip, NLT + structured)
  - [ ] `make run-models-quick` (batch runner end-to-end)
  - [ ] Verify new results append correctly to aggregated_results.csv (15-col schema)
  - [ ] Monitor early-abort behavior on this first live run (last automated-only check for Issue 2, below)

## TODO

- [ ] **TodoScope Alignment**: Finish aligning this repo with TodoScope conventions
  - [x] Restructure TODO.md to conventions
  - [x] Create `.todoscope-exclude.csv` (`.venv`, `.pytest_cache`, `__pycache__`, `src/nlt.egg-info`, `arxiv`, `results`, `.obsidian`)
  - [x] Run the TodoScope scanner and verify the kanban board matches expectations
  - [ ] Migrate inline tags to `TODO:` / `FIXME:` / `BUG:` convention as they're introduced (none found in source yet)

## Backlog

- [ ] **arXiv Submission**: Upload the compile-verified package to arXiv.org and publish #critical
  - [ ] Rebuild immediately before submitting (`make arxiv`) to pick up any last-minute edits to REPLICATION_STUDY.md
  - [ ] Confirm arXiv account/endorsement status for the submitting author
  - [ ] Upload `arxiv/arxiv-submission.tar.gz` via the arXiv submission portal
  - [ ] Select primary category (e.g. cs.CL / cs.AI) and cross-list if applicable
  - [ ] Fill in title, authors, and abstract (pre-validated at 1,719/1,920 chars)
  - [ ] Review arXiv's auto-compiled PDF and TeX log for warnings before finalizing
  - [ ] Submit and wait for moderation
  - [ ] Record the assigned arXiv ID once published
  - [ ] Update README.md / REPLICATION_STUDY.md citation block with the live arXiv link
  - [ ] Cross-post per SOCIAL_SHARES.md plan

## Bugs

_No known bugs. Use `# BUG:` inline tags to flag defects in source._

## Done

### Week of July 1, 2026

- [x] **Verify the study end-to-end and repair issues**: Full offline verification of harness, pipeline, data, and docs
  - [x] Rewrite tests/test_evaluator.py against current evaluator API (client-based, TrialResult dataclass) — suite green (27 passed)
  - [x] Fix doc/script path mismatches (`python src/scripts/analyze_results.py`, `bash src/scripts/run_study.sh`), `$SAGE_AUTH_TOKEN`, §8 clone URL, stale 10-col CSV schema → real 15-col schema
  - [x] Correct REPLICATION_STUDY.md §2.6 survivorship count: 4 → 8 of 107 entries (2 models), verified against aggregated_results.csv
  - [x] .gitignore: stop ignoring tracked `results/` reproducibility data; add .pytest_cache/, build/, dist/, *.bak
  - [x] Declare chart deps as `viz` extra in pyproject.toml (`uv pip install -e ".[viz]"`)
  - [x] `chmod +x src/scripts/{clean_aborted.py,run_study.sh}`; add `src/nlt/api/__init__.py`
- [x] **arXiv submission pipeline**: `make arxiv` converts REPLICATION_STUDY.md (Obsidian vault source of truth) to an arXiv-ready LaTeX package
  - [x] src/scripts/md_to_arxiv.py: programmatic handling of Obsidian embeds, Notion-split tables, bogus/relative links, LaTeX-hostile Unicode, metadata + abstract extraction
  - [x] Compile-verified with tectonic (28-page PDF); tarball at arxiv/arxiv-submission.tar.gz
  - [x] Validates arXiv's 1,920-char abstract limit (currently 1,719) and package size
- [x] **Add analysis notebook for visuals**: `notebooks/analysis_visuals.ipynb` plots per-approach/model metrics and gains
  - [x] Generate accuracy and variance box/violin plots for NLT vs structured
  - [x] Plot error counts and aborted runs per model
  - [x] Export charts to `results/figures/` (12 PNGs) for reports/README/REPLICATION_STUDY
  - [x] Test/verify step — executed end-to-end via `jupyter nbconvert --execute`, zero errors
  - [x] Documentation update — linked in README.md with an Open-in-Colab badge
  - [x] Colab/Kaggle compatible: pip-based dep install via `sys.executable`, environment detection, GitHub raw-CSV fallback when the repo isn't checked out locally

### Week of January 18, 2026

- [x] **Clean up repository structure**: Move scripts to src/, keep only essential files in root
  - [x] Move analyze_results.py, run_models.py, backfill_tokens.py, run_study.sh to src/scripts/
  - [x] Move test_cleaning.py, validate_cleaning.py to tests/
  - [x] Update all scripts to use PROJECT_ROOT for path resolution
  - [x] Update Makefile to reference new script locations (src/scripts/)
  - [x] Test all Makefile targets work correctly
  - [x] Root now contains only: Makefile, models.csv, aggregated_results.csv, CONVENTION.instructions.md, README.md, TODO.md, pyproject.toml, and core directories
- [x] **Issue 1 - Misleading stats when all trials error**: Fixed accuracy/variance reporting
  - [x] When all trials error (valid_trials=0), accuracy/variance now report as `None` instead of 0.0
  - [x] Added `valid_trials` and `aborted` fields to summary and aggregated results
  - [x] Updated analysis scripts to handle None values correctly
  - [x] Updated tests for new behavior
- [x] **Issue 2 - Early abort on repeated errors**: Implemented early stopping to save money/tokens
  - [x] Added `MAX_CONSECUTIVE_ERRORS = 5` threshold
  - [x] Evaluator now returns `(results, aborted)` tuple
  - [x] When 5+ consecutive errors occur, evaluation stops and reports "aborted"
  - [x] Aborted flag stored in aggregated results for tracking
  - [x] Automated regression coverage: `test_evaluate_aborts_after_consecutive_errors` in tests/test_evaluator.py
- [x] **Full Study Replication**: Ran the complete 2×2×2 factorial design across 14 models
  - [x] Document replication methodology (REPLICATION.md)
  - [x] Create study execution script (run_study.sh)
  - [x] Create aggregation tools (analyze_results.py)
  - [x] Add --quick and --force options to study script
  - [x] Execute full evaluation — 14 models, 107 aggregated entries, 8,560 trials (12 of 14 with complete 8-condition coverage)
  - [x] Compare with original paper findings (REPLICATION_STUDY.md §Discussion vs. Johnson et al. 2025)
  - [x] Document model-specific insights (capability-dependent gains, survivorship-corrected per-model breakdown)
- [x] **CSV Tracking System**: Build model tracking and aggregated results system
  - [x] Configure Black for linting and formatting
  - [x] Add pytest configuration
  - [x] Write parser unit tests (NLT YES/NO extraction, structured function parsing)
  - [x] Write evaluator tests (accuracy/variance calculation)
  - [x] Add CLI smoke test
  - [x] Test/verify step
  - [x] Documentation update
- [x] **Testing Infrastructure**: Build comprehensive test suite
  - [x] Configure Black for linting and formatting
  - [x] Write parser unit tests (16 tests - NLT YES/NO, tool_calls, exact match, statistics)
  - [x] Write evaluator unit tests (11 tests - single trials, batch eval, error handling)
  - [x] Add pytest configuration to pyproject.toml
  - [x] Add test and test-coverage Makefile targets
  - [x] All tests passing
- [x] **Comprehensive Documentation**: Update all docs with new CSV/batch workflow
  - [x] Update README with batch evaluation section
  - [x] Update README with Makefile targets reference
  - [x] Overhaul REPLICATION.md with CSV-first workflow
  - [x] Add results organization section (3 CSVs + JSON files)
  - [x] Create DEVELOPMENT.md with developer guide
  - [x] Add troubleshooting and performance optimization guides
  - [x] Document CSV tracking system thoroughly

### Week of January 11, 2026

- [x] **NLT MVP codebase setup**: Scaffold a clean Python package for the Natural Language Tools framework and sample scenarios
  - [x] Define package layout (core modules for prompts, parsing, orchestration, and sample data)
  - [x] Implement selector/parser pipeline skeleton with Alex/Sage scenarios
  - [x] Add CLI demo for running a selector and parser pass
  - [x] Multi-model support with organized result storage
  - [x] Test/verify step - smoke tests passing
  - [x] Documentation update
- [x] **Linting & Testing**: Add Black for linting/formatting and pytest for unit tests
  - [x] Configure Black for linting and formatting
  - [x] Add pytest configuration
  - [x] Write parser unit tests (NLT YES/NO extraction, structured function parsing)
  - [x] Write evaluator tests (accuracy/variance calculation)
  - [x] Add CLI smoke test
  - [x] Test/verify step
  - [x] Documentation update
- [x] **Environment & tooling (uv)**: Initialize Python project with uv and add core dependencies and lint/test tooling
  - [x] Initialize uv project metadata and dependencies
  - [x] Make package importable (editable install / packaging metadata)
  - [x] Document autoenv integration in CONVENTION.md
- [x] **Docs & README**: Document architecture, usage, and examples derived from the NLT paper
  - [x] Draft README with quickstart and architecture overview
  - [x] Add example prompts/output formats for Alex and Sage
  - [x] Create REPLICATION.md for full study methodology
  - [x] Update CONVENTION.md with autoenv details
