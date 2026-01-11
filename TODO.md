## 🔥 This Week (January 11, 2026)
### ✅ NLT MVP codebase setup - COMPLETE
- [x] **NLT MVP codebase setup**: Scaffold a clean Python package for the Natural Language Tools framework and sample scenarios.
  - [x] Define package layout (core modules for prompts, parsing, orchestration, and sample data)
  - [x] Implement selector/parser pipeline skeleton with Alex/Sage scenarios
  - [x] Add CLI demo for running a selector and parser pass
  - [x] Multi-model support with organized result storage
  - [x] Test/verify step - smoke tests passing
  - [x] Documentation update

### 🔥 High Priority: Linting & Testing
- [ ] **Linting & Testing**: Add Black for linting/formatting and pytest for unit tests.
  - [x] Configure Black for linting and formatting
  - [ ] Add pytest configuration
  - [ ] Write parser unit tests (NLT YES/NO extraction, structured function parsing)
  - [ ] Write evaluator tests (accuracy/variance calculation)
  - [ ] Add CLI smoke test
  - [ ] Test/verify step
  - [ ] Documentation update

### 🔶 High Priority: Full Study Replication
- [ ] **Full Study Replication**: Run complete 2×2×2 factorial design across multiple models.
  - [x] Document replication methodology (REPLICATION.md)
  - [ ] Create study execution script (run_full_study.sh)
  - [ ] Execute full evaluation (4+ models × 8 conditions × 5 replicates)
  - [ ] Aggregate results and compute summary statistics
  - [ ] Compare with original paper findings
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
  - [x] Create REPLICATION.md for full study methodology
  - [x] Update CONVENTION.md with autoenv details
