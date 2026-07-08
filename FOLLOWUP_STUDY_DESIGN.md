From Selection to Agency: Natural Language Tools for Parameterized, Long-Horizon Agentic Work
==============================================================================================

A Follow-Up Study Design (NLT-2)
--------------------------------

```
Status:   Draft for team review
Builds on: Sage-is/NLT-Replication-Study (Somma, Plante & Premji, 2026)
Informed by: Johnson et al. (2025); Intelligent Internet, "From RALPH to Zenith" (2026)
```

* * * * *

Abstract (planned)
------------------

Our replication study validated Natural Language Tools (NLT) for single-turn, parameterless tool selection: +14.9pp accuracy, 93% fewer critical errors, 25.2% fewer tokens, with gains concentrated in non-frontier, reasoning, and open-weight models. This follow-up extends NLT past its validated construct into the territory where agentic systems actually live: parameterized calls, multi-turn loops, and long-horizon tasks governed by a plain markdown control plane. We test whether the NLT advantage survives parameterization (H1, H2), whether it interacts with harness design strongly enough to make non-frontier models viable for long-horizon work (H3), whether capability-based multi-model routing beats any single model (H4), and whether small targeted fine-tunes (LoRA) close the remaining gap for lagging models (H5). The design goal throughout is poka-yoke: prevent tool-calling errors at the source instead of absorbing them downstream with retries and fallback machinery.

* * * * *

1. Background and Motivation
----------------------------

Two results motivate this study.

**Ours.** NLT-1 established that structured (JSON-schema) invocation taxes exactly the models the world most needs to work: models without native tool calling collapsed entirely under structured calling (Mistral 7B: 320 errors, 0% effective accuracy) yet functioned under NLT; reasoning models paid a large format penalty (DeepSeek-R1: +24.0pp under NLT); and the error-rate advantage (93% reduction) persisted even where accuracy converged. The boundary condition was just as clear: structured-optimized frontier models (Gemini 2.5 Pro) can reverse the effect.

**Theirs.** The Zenith technical report (Intelligent Internet, 2026) ran an ablation ladder of harness designs on long-horizon tasks and isolated the control mechanisms that matter: repeated gap-finding (RALPH), just-in-time milestone planning, *independent* verification as the completion contract, and explicit stopping rules. Every rung of that ladder, though, was climbed on frontier backbones (opus-4.6, gpt5.4), the tier where our capability gradient says the structured-call tax is already near zero.

The untested intersection is the thesis of NLT-2:

> **Long-horizon agentic reliability is a product of the call layer and the control layer. Frontier labs fixed the call layer with RL and bought the control layer with compute. NLT fixes the call layer with language; a clear, simple markdown control plane supplies the control layer. Together they should make non-frontier and open-weight models viable knowledge-work agents.**

If H3 holds, the result is more consequential than either prior finding alone: capable agentic systems become deployable without frontier pricing or frontier lock-in, and without the data-governance strings attached to frontier APIs.

* * * * *

2. Research Questions and Hypotheses
------------------------------------

RQ1. Does the NLT advantage survive parameterization?

- **H1.** On parameterized tool calls, NLT maintains a lower critical-error rate than structured calling across Tier 1–2 models, with accuracy gains concentrated in argument *presence/selection* rather than argument *transcription*.
- **H1a (boundary).** For arguments requiring verbatim fidelity (paths, IDs, code snippets), a composite convention (NL selection + fenced-block arguments) outperforms both pure NLT and pure JSON.

RQ2. Does the NLT advantage compound over multi-turn loops?

- **H2.** Per-call error differences compound: across an N-call chain, task-level survival for structured calling degrades approximately as (1 − e_s)^N versus (1 − e_n)^N for NLT, so NLT's task-level advantage *exceeds* its per-call advantage. We predict the largest divergence on Tier 1–2 models at N ≥ 20.

RQ3. Do call format and harness design interact?

- **H3.** Format × harness interaction: under a one-session harness the format effect matches NLT-1; under a Milestone-RALPH-style markdown harness, NLT-equipped non-frontier models complete long-horizon tasks that the same models cannot complete under structured calling *at any harness setting*, because structured call failures starve the loop before gap-finding can act.

RQ4. Is multi-model routing better than any single model?

- **H4.** A router that assigns roles by measured capability (e.g., mid-tier NLT model as worker, reasoning model as planner, strongest available model as independent verifier) achieves ≥90% of the best single frontier-model score at ≤40% of its cost. Roles are format-assigned per our Tier map: Tier 1–2 roles run NLT; Tier 4 roles may run structured.

RQ5. Where NLT is insufficient, does targeted fine-tuning close the gap?

- **H5.** A small LoRA trained on NLT-convention transcripts (selection grids + fenced arguments + verifier interactions) lifts a lagging Tier 1 model's parameterized-call accuracy by ≥10pp at <$500 training cost, without degrading general instruction following (measured on a held-out non-tool suite).

RQ6 (secondary). Does moving the checkbox reduce false completion?

- **H6.** In markdown-todo harness runs, requiring an independent verifier session to flip `- [ ]` → `- [x]` (workers may only append evidence) reduces the false-done rate versus worker self-ticking, replicating Zenith's completion-contract finding in a plain-markdown setting.

* * * * *

3. The NLT-A Convention (what we are actually testing)
------------------------------------------------------

NLT-1 tested a YES/NO selection grid. NLT-A ("agentic") extends the convention minimally. Every extension follows one poka-yoke rule: **make the correct call the easiest thing to write, and make ambiguity impossible to silently pass.**

### 3.1 Parameterized calls

Selection stays natural language; arguments ride in labeled lines or fenced blocks. One decision per line. Bounded vocabulary for enums. Example:

````
Thinking: (insert_thinking)

Read file — YES/NO
  path: src/nlt/core/evaluator.py

Write file — YES/NO
  path: (insert_path)
  content:
  ```
  (insert_content)
  ```

Run command — YES/NO
  command: (insert_command)
  timeout_seconds: 30 | 120 | 600

Ask a human — YES/NO
Assessment finished.
````

Design rules (the poka-yoke set, each independently ablatable):

- **P1. One decision per line.** No nested objects; nesting is where JSON errors concentrated in NLT-1's failure logs.
- **P2. Fenced verbatim arguments.** Anything requiring exact transcription (paths, code, IDs) goes in a fence; the parser takes it byte-for-byte.
- **P3. Bounded enums inline.** Legal values are printed in the prompt (`30 | 120 | 600`); anything else is a soft error returned *in language*, not a stack trace.
- **P4. Echo-back on destructive calls.** Writes/deletes/sends require the model to restate the target on a confirmation line; mismatch aborts the call.
- **P5. Refuse-ambiguity path.** "Ask a human" / "I cannot determine X" is a first-class, always-available response, so the format never forces a guess.
- **P6. Reasoning lane.** The `Thinking:` line is preserved and ungraded, accommodating reasoning traces (the R1 finding) without polluting parsing.

### 3.2 The markdown control plane

The harness state is plain files in the workspace, human-greppable, no database:

```
mission/
  MISSION.md          # original request, verbatim; never edited
  DONE-CRITERIA.md    # success criteria + required evidence, extracted at kickoff
  MILESTONES.md       # coarse milestones only (JIT-plan details per milestone)
  TODO.md             # active milestone's task list
  EVIDENCE/           # worker-appended proof, one file per task
  SKILLS/             # markdown skills appended when a lesson repeats
  VERDICTS.md         # verifier-only file; the only place checkboxes flip
```

Loop (deliberately dumb; a shell script, not a coordinator):

1. Fresh **worker** session: read MISSION + TODO, do one unchecked task using NLT-A calls, append evidence. Workers cannot edit VERDICTS.md.
2. Fresh **verifier** session: attempt to *invalidate* the task against DONE-CRITERIA. Pass → tick in VERDICTS.md. Fail → append a new TODO item.
3. Milestone gate: all items ticked → JIT-plan the next milestone from the *current* repo state (never from the original plan).
4. Stop when DONE-CRITERIA evidence is complete, or budget cutoff (recorded as a distinct outcome, never conflated with completion).

This imports Zenith's three validated mechanisms (independent verification, JIT milestone planning, explicit stopping) at markdown-harness complexity, and directly avoids Plan-RALPH's two documented failure modes (stale upfront lists, self-ticked false-done labels).

* * * * *

4. Experimental Design
----------------------

### 4.1 Factors

| Factor | Levels |
|---|---|
| Invocation format | NLT-A · Structured (OpenAI-schema) · Composite (NL selection + JSON args) |
| Harness | One-session · MD-Milestone (Section 3.2) |
| Model tier | T1 (no native tools: Mistral 7B class) · T2 (mid/reasoning: DeepSeek-V3, R1, Llama 3.x, gpt-5-nano class) · T4 (structured-optimized frontier: 1–2 models as ceiling reference) |
| Routing (Phase C only) | Single-model · Capability-routed ensemble |
| LoRA (Phase D only) | Base · +NLT-A LoRA |

Tier 3 (strong structured capability) has no model arm of its own; NLT-1's recommendation for that tier was composite calling, which enters the design as the Composite format instead.

Full crossing is unaffordable; we run three phases plus one micro-bench, each answering its hypothesis with the minimum viable crossing.

### 4.2 Phase A — Parameterized call micro-bench (H1, H1a)

Single-turn, but parameterized. Extend the Alex/Sage scenarios plus one technical scenario ("Dev": file ops, command runs, patch application) so argument types cover: enum, free string, verbatim path, verbatim code block, integer-with-bounds.

- 3 formats × 3 scenarios × 20 inputs × 2 perturbations × 5 replicates per model. 12 models (reuse NLT-1 roster availability), ≈ 21,600 trials.
- Grading: exact match on selection; per-argument exact match for verbatim fields; normalized match (whitespace/case) for free strings, both reported.
- Carry over NLT-1 conventions unchanged: temperature 1.0, corrected accuracy with the ≥70/80-error → 0% survivorship rule, all raw outputs logged.

### 4.3 Phase B — Chain reliability and harness interaction (H2, H3, H6)

Long-horizon tasks, scaled to be affordable but genuinely multi-milestone. Three tasks, one per family (mirroring Zenith's family logic at ~1/10 scope):

1. **Build:** small browser game from a multi-file spec (~25 requirements).
2. **Repo:** implement a CLI tool matching a reference's behavior on a fixed command/exit-code test matrix.
3. **Analysis:** data pipeline + written report against a rubric.

Design: 2 formats (NLT-A, Structured) × 2 harnesses × 3 models (2×T2, 1×T1) × 3 tasks × 3 seeds = 108 fully crossed runs, budget-capped per run. The T4 reference model runs a reduced grid on top of that; its exact cells get fixed before any runs start.

Measured per run:

- Task score against a fixed rubric (blind-graded; grader never sees format).
- Per-call error rate and **chain survival**: longest uninterrupted call sequence; retries; unrecoverable states.
- **False-done rate:** items ticked done that the final audit fails (H6: compare worker-tick vs verifier-tick arms on a subset).
- Cost, tokens, wall-clock; stopping outcome (criteria-met vs budget-cut).

### 4.4 Phase C — Capability-routed ensemble (H4)

On the same three tasks: best single-model configuration from Phase B versus a routed ensemble (T2-NLT workers, R1-NLT planner, strongest-available verifier in its best format). 3 tasks × 3 seeds × 2 arms = 18 runs. Report score ratio and cost ratio against the T4 single-model reference.

### 4.5 Phase D — LoRA arm (H5)

Pick the weakest Phase A open-weight model. Train a LoRA on ~2–5k NLT-A transcript examples synthesized from Phase A/B logs (correct calls, corrected calls, refuse-ambiguity exemplars). Re-run Phase A for that model, plus a held-out general-instruction suite to check for regression. Report Δpp, train cost, and regression delta. This phase is deliberately small: it answers "is fine-tuning *called for*," not "what is the best fine-tune."

* * * * *

5. Metrics and Analysis Plan
----------------------------

Primary: corrected accuracy (Phase A), task score (Phase B/C), critical-error rate (all phases). Secondary: tokens, cost, chain survival, false-done rate, stopping quality. All corrections and exclusions pre-registered in this document; the survivorship correction from NLT-1 §2.6 applies unchanged.

Pre-registered comparisons:

1. H1: paired per-model NLT-A vs Structured on Phase A (selection accuracy and argument accuracy reported separately).
2. H2: fitted per-call error rates vs observed chain survival; report whether the compounding model within its confidence band explains task-level gaps.
3. H3: format × harness interaction on Phase B task score, per tier. The headline test: count of T1/T2 runs reaching a "usable" score threshold (pre-set per task) by format.
4. H4/H5: as stated in hypotheses, with cost on the same axis.

We will report negative results with the same prominence as positive ones. NLT-1's credibility rests on having documented the Gemini 2.5 Pro reversal, and NLT-2 keeps that standard. Plausible negative outcomes we explicitly anticipate: verbatim-argument transcription favoring JSON (which would support the composite convention, H1a), and frontier-model runs showing no harness × format interaction (expected; consistent with the capability gradient).

* * * * *

6. Threats to Validity (known at design time)
---------------------------------------------

- **Construct creep.** NLT-A is not NLT-1's construct; we mitigate by keeping Phase A's selection-only subset directly comparable to NLT-1.
- **Grader leakage.** Long-horizon scoring is judgment-heavy; graders are blinded to format/harness and rubrics are frozen before runs.
- **Parser as confounder.** The NLT-A parser is now a research object. It is pure-stdlib, frozen per phase, and every parse failure is logged with the raw output so reviewers can audit whether errors are model or parser.
- **Task scale.** 1/10-scale tasks may understate rediscovery costs that favor richer harnesses; we note this and treat Zenith's full-scale numbers as the upper-bound context, not a comparison target.
- **Provider drift.** Compressed run window; provider + date logged per trial.
- **Multiple comparisons.** Phases answer one hypothesis each; secondary metrics are reported descriptively, not tested.

* * * * *

7. Deliverables
---------------

1. `NLT-A-CONVENTION.md` — the call convention + poka-yoke rules (P1–P6), versioned, suitable for direct adoption by the agentic library.
2. Harness code: the markdown control plane + dumb loop, stdlib-only, plus the three benchmark tasks with frozen rubrics.
3. All prompts, raw outputs, `aggregated_results.csv`, and chart generation, matching NLT-1's reproducibility artifacts.
4. The study writeup, same format as REPLICATION_STUDY.md.
5. If H5 holds: the LoRA training recipe and dataset synthesis script.

Suggested sequencing for the team: Phase A can start as soon as the Dev scenario and parser are written (it reuses the NLT-1 evaluator almost directly). Phase B's harness is the same artifact the agentic library needs anyway, so building it counts toward both.

* * * * *

*Why are we making the language model stop speaking language? We're not, anymore. Now we're checking how far that goes.*
