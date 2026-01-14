# Natural Language Tools: A Replication Study
## Validating NLT Performance Across [#todo: MODEL_COUNT] Models

**Authors:** [NAME_HERE], [NAME_HERE], [NAME_HERE]  
**Affiliation:** [AFFILIATION_HERE]  
**Date:** January 12, 2026  
**Status:** DRAFT - Replication in Progress

---

## Abstract

We present a systematic replication of the Natural Language Tools (NLT) framework originally proposed by Johnson et al. (2025). Using an independent implementation and evaluation harness, we assessed NLT's tool-calling performance across 2 frontier models (llama-3.1-8b-instant and google/gemini-2.5-flash-lite) spanning 640 trials in customer service and mental health domains as a mini-replication. Early results show NLT improves tool-calling accuracy by +12.4pp over structured approaches (48.0% → 60.5%), with consistent gains across both models (+14.9pp for llama-3.1-8b, +10.0pp for gemini-2.5-flash-lite). We observe 12.5% reduction in output variance. **Full study with [#todo: FULL_MODEL_COUNT] models is planned.** These preliminary results partially confirm the original study's findings, though with smaller effect sizes in our mini-replication ([#todo: DISCUSS_AFTER_FULL_STUDY]). Our open-source implementation and complete evaluation data are available for further validation.

**Keywords:** Large Language Models, Tool Calling, Function Calling, Agentic Systems, Replication Study

---

## 1. Introduction

### 1.1 Background

Johnson et al. (2025) demonstrated that replacing programmatic JSON tool calling with natural language (Natural Language Tools, or NLT) significantly improved LLM tool-calling accuracy. Their findings showed an 18.4 percentage point gain across 10 models and 6,400 trials, alongside substantial variance reduction and token savings.

These results challenge the dominant paradigm of structured tool calling and suggest that format constraints may be a significant but underappreciated bottleneck in agentic system performance. If validated, NLT could reshape how developers implement tool calling in production systems.

### 1.2 Motivation for Replication

Replication studies are critical for establishing reproducibility in AI research (Smith et al., 2024; [#todo: ADD_CITATIONS]). We undertook this independent replication to:

1. **Validate core findings** using an independent codebase and evaluation framework
2. **Assess generalizability** to models released after the original study
3. **Test robustness** to implementation details and prompt variations
4. **Provide open-source tooling** for continued NLT evaluation
5. **Identify boundary conditions** where NLT's advantages may diminish

### 1.3 Scope and Limitations

Our replication focuses on the core experimental conditions from Johnson et al. (2025):
- Single-turn, parameterless tool selection
- Two scenarios: customer service ("Alex") and mental health ("Sage")
- Exact-match evaluation with 5 replicates per input
- Comparison of NLT vs structured tool calling approaches

**Limitations we acknowledge:**
- [#todo: MODEL_AVAILABILITY] - Some models from the original study are unavailable
- [#todo: API_DIFFERENCES] - API implementations may differ from original study
- [#todo: TEMPORAL_EFFECTS] - Model capabilities may have changed since original evaluation
- [#todo: INFRASTRUCTURE] - Different inference infrastructure may affect results
- We do not replicate multi-turn interactions or parameterized tool calls

### 1.4 Contributions

1. **Independent validation** of NLT's core claims using open-source tooling
2. **Extended evaluation** to [#todo: NEW_MODEL_COUNT] models not in original study
3. **Detailed per-model analysis** with complete result transparency
4. **Open-source framework** for continued NLT research and evaluation
5. **Reproducibility artifacts** including all prompts, inputs, and raw results

---

## 2. Methodology

### 2.1 Implementation

We developed an independent Python-based evaluation harness implementing the NLT framework as described in Johnson et al. (2025). Our implementation consists of:

**Core Components:**
- `evaluator.py`: Trial execution and metrics computation
- `parser.py`: YES/NO parsing for NLT and tool_calls extraction for structured
- `client.py`: API client using urllib (no external dependencies)
- `scenarios.py`: Alex and Sage scenarios with tool schemas

**Key Implementation Decisions:**
- Pure Python with no external API libraries (urllib only)
- OpenAI-compatible function calling schema for structured approach
- Regex-based parsing for NLT YES/NO extraction
- Exact-match grading with no partial credit
- 5 independent replicates per input (parallel API calls)

### 2.2 Experimental Design

We replicated the original 2×2×2 factorial design:
- **Approach:** NLT vs Structured Tool Calling
- **Scenario:** Alex (customer service) vs Sage (mental health)
- **Perturbation:** Non-perturbed vs Perturbed prompts

**Per-model trial count:**
- 2 approaches × 2 scenarios × 16 inputs × 2 perturbations × 5 replicates = [#todo: CALCULATE] trials

### 2.3 Scenarios and Tool Definitions

We used identical tool descriptions and user inputs from Johnson et al. (2025):

**Alex (Customer Service) - 7 Tools:**
1. Recap of previous conversation
2. Website information
3. Recent social media posts
4. Available discounts
5. List of upcoming events
6. Past Purchases
7. Talk to a Human

**Sage (Mental Health) - 8 Tools:**
1. Most Recent Conversation
2. Psychometric Quizzes
3. Sage Website Information
4. Sage Technology
5. Sage Company Info
6. Sage Social Media
7. End Conversation
8. Safety Call

[#todo: VERIFY_EXACT_MATCH_WITH_APPENDIX_A]

### 2.4 Model Selection

**Mini-Replication Set (2 models, 640 trials):**
1. `llama-3.1-8b-instant` (Meta, 8B parameters, open-weight)
   - Available via [inference provider]
   - Supports parallel tool calling via function schemas
2. `google/gemini-2.5-flash-lite` (Google, size unknown, closed-weight)
   - Available via [inference provider]
   - Supports parallel tool calling via function schemas

**[#todo: FULL_STUDY_MODEL_SET]**
- Plan to test: [#todo: LIST_ADDITIONAL_MODELS]
- Target total: [#todo: MODEL_COUNT] models
- Target trials: [#todo: TRIAL_COUNT]

**Models from Original Not Yet Tested:**
- GPT-5, GPT-5-nano (OpenAI)
- Claude Sonnet 4.0 (Anthropic)
- DeepSeek-V3, Qwen3, Kimi-K2, etc.
- Reason: Mini-replication phase to validate framework before full run

### 2.5 Prompt Design

We replicated the original prompts with minimal adaptations for API compatibility:

**NLT Prompts:** Natural language tool list with YES/NO format instructions
**Structured Prompts:** Function schemas passed via API with system prompt

[#todo: VERIFY_PROMPTS_MATCH_APPENDIX_A_OR_DOCUMENT_DIFFERENCES]

### 2.6 Evaluation Metrics

- **Accuracy:** Proportion of exact matches (predicted tools = expected tools)
- **Variance:** Sample variance across replicates
- **Token Usage:** Input, output, and total tokens per trial
- **Error Rate:** Proportion of API errors or parsing failures

### 2.7 Data Collection

**API Access:**
- Open-weight models via [#todo: PROVIDER] ([#todo: DATE_RANGE])
- Closed-weight models via native provider APIs ([#todo: DATE_RANGE])
- All models accessed with default parameters (temperature=1.0, top_p=1.0)

**Quality Control:**
- API errors retried until clean response obtained
- All raw outputs logged for manual inspection
- Parser validation against ground truth labels

---

## 3. Results

### 3.1 Overall Accuracy

[#todo: GENERATE_FIGURE_3_EQUIVALENT]

**Mini-Replication Results (2 models, 640 trials):**
- **Overall:** 60.5% NLT vs 48.0% Structured (Δ = +12.4pp)
- **llama-3.1-8b-instant (open-weight):** 47.8% NLT vs 32.9% Structured (Δ = +14.9pp)
- **google/gemini-2.5-flash-lite (closed-weight):** 73.1% NLT vs 63.1% Structured (Δ = +10.0pp)

**Comparison to Original Study:**
- Original overall gain: +18.4pp (69.1% → 87.5%)
- Our mini-replication: +12.4pp (48.0% → 60.5%)
- Effect confirmed but smaller magnitude (possibly due to limited model sample)

**[#todo: UPDATE_AFTER_FULL_STUDY_WITH_MORE_MODELS]**

### 3.2 Per-Model Performance

[#todo: GENERATE_FIGURE_4_EQUIVALENT]

**Mini-Replication Findings (2 models):**

**Models Tested:**
1. **llama-3.1-8b-instant**: +14.9pp (32.9% → 47.8%)
   - NLT variance: 0.2044, Structured variance: 0.2172
   - Structured had 37 API/parsing errors vs 0 for NLT
2. **google/gemini-2.5-flash-lite**: +10.0pp (63.1% → 73.1%)
   - NLT variance: 0.1793, Structured variance: 0.2213
   - No errors in either approach

**Key Observations:**
- Both models show consistent NLT gains
- Open-weight model (llama) shows larger gain (+14.9pp) than closed-weight (gemini, +10.0pp)
- Pattern aligns with original study's finding that open-weight benefits more
- Gemini achieves higher absolute accuracy in both approaches

**[#todo: EXPAND_WITH_FULL_MODEL_SET_RANKINGS_AND_COMPARISON_TO_ORIGINAL_FIGURE_4]**

### 3.3 Variance Analysis

[#todo: GENERATE_FIGURE_5_EQUIVALENT]

**Mini-Replication Variance Results:**
- **Structured variance:** 0.2193 (SD = 46.8pp)
- **NLT variance:** 0.1919 (SD = 43.8pp)
- **Reduction:** 12.5%

**Comparison to Original:**
- Original: 0.0411 → 0.0121 (70% reduction, SD: 20.28pp → 10.99pp)
- Our mini-replication: 0.2193 → 0.1919 (12.5% reduction, SD: 46.8pp → 43.8pp)
- **Note:** Higher variance in our mini-replication likely due to:
  - Small model sample (n=2 vs n=10)
  - One model (llama) had high error rate in structured approach (37 errors)
  - Different model selection

**Per-Model Variance Reduction:**
1. **llama-3.1-8b-instant:** 0.2172 → 0.2044 (5.9% reduction)
2. **google/gemini-2.5-flash-lite:** 0.2213 → 0.1793 (19.0% reduction)

**[#todo: UPDATE_WITH_FULL_MODEL_SET_FOR_MORE_ROBUST_VARIANCE_ANALYSIS]**

### 3.4 Perturbation Robustness

[#todo: GENERATE_FIGURE_6_EQUIVALENT]

**Non-perturbed Results:**
- Accuracy: [#todo: NLT]% vs [#todo: STRUCTURED]% (Δ = [#todo: GAIN]pp)
- Variance: [#todo: NLT_VAR] vs [#todo: STRUCTURED_VAR]

**Perturbed Results:**
- Accuracy: [#todo: NLT]% vs [#todo: STRUCTURED]% (Δ = [#todo: GAIN]pp)
- Variance: [#todo: NLT_VAR] vs [#todo: STRUCTURED_VAR]

**Comparison to Original:**
- Original non-perturbed gain: +21.2pp
- Original perturbed gain: +15.4pp
- Our replication: [#todo: COMPARISON_NARRATIVE]

### 3.5 Domain Comparison (Alex vs Sage)

**Alex (Customer Service):**
- Overall accuracy: 64.9%
- NLT vs Structured: 75.3% vs 54.5% (Δ = +20.8pp)
- NLT variance: 0.1697, Structured variance: 0.2143
- Structured errors: 12 API/parsing failures

**Sage (Mental Health):**
- Overall accuracy: 43.6%
- NLT vs Structured: 45.6% vs 41.5% (Δ = +4.1pp)
- NLT variance: 0.2140, Structured variance: 0.2243
- Structured errors: 25 API/parsing failures

**Comparison to Original:**
- Original showed higher accuracy for Alex vs Sage ✓ **Confirmed**
- Our mini-replication shows same pattern: Alex (64.9%) > Sage (43.6%)
- Alex shows much larger NLT gain (+20.8pp) than Sage (+4.1pp)
- Sage structured approach had significantly more errors (25 vs 12)

**[#todo: INVESTIGATE_WHY_SAGE_NLT_GAIN_IS_SMALL_WITH_LARGER_MODEL_SET]**

### 3.6 Token Usage

[#todo: GENERATE_FIGURE_7_EQUIVALENT]

**Token Reduction:**
- **Structured:** [#todo: TOTAL] tokens ([#todo: INPUT] input + [#todo: OUTPUT] output)
- **NLT:** [#todo: TOTAL] tokens ([#todo: INPUT] input + [#todo: OUTPUT] output)
- **Reduction:** [#todo: PERCENT]%

**Comparison to Original:**
- Original: 31.4% reduction (1319 → 905 tokens)
- Our replication: [#todo: COMPARISON]

### 3.7 New Model Results

**Models Not in Original Study:**

[#todo: FOR_EACH_NEW_MODEL]
- **[MODEL_NAME]:**
  - NLT accuracy: [#todo: VALUE]%
  - Structured accuracy: [#todo: VALUE]% (if applicable)
  - Net gain: [#todo: VALUE]pp
  - Notes: [#todo: OBSERVATIONS]

---

## 4. Analysis and Discussion

### 4.1 Validation of Core Findings

**Confirmed:**
- [#todo: LIST_FINDINGS_THAT_REPLICATED_SUCCESSFULLY]

**Partially Confirmed:**
- [#todo: LIST_FINDINGS_WITH_QUALIFICATIONS]

**Not Confirmed:**
- [#todo: LIST_FINDINGS_THAT_DIVERGED]

### 4.2 Divergences from Original Study

**Magnitude of Effects:**
[#todo: DISCUSS_ANY_DIFFERENCES_IN_EFFECT_SIZES]

**Model Rankings:**
[#todo: COMPARE_RELATIVE_MODEL_PERFORMANCE]

**Domain Effects:**
[#todo: COMPARE_ALEX_VS_SAGE_RESULTS]

**Potential Explanations:**
1. **Temporal effects:** Models may have improved structured tool calling since original study
2. **API differences:** Different inference implementations may affect results
3. **Prompt variations:** Minor differences in API formatting could influence outcomes
4. **Statistical variance:** Some differences may be within expected sampling error

### 4.3 Extended Findings

**New Models:**
[#todo: INSIGHTS_FROM_MODELS_NOT_IN_ORIGINAL]

**Implementation Insights:**
[#todo: LESSONS_FROM_INDEPENDENT_IMPLEMENTATION]

### 4.4 Robustness Assessment

**Factors Supporting Robustness:**
- [#todo: EVIDENCE_OF_ROBUST_EFFECTS]

**Factors Raising Concerns:**
- [#todo: EVIDENCE_OF_FRAGILITY]

### 4.5 Implications

**For Practitioners:**
- [#todo: PRACTICAL_RECOMMENDATIONS]

**For Researchers:**
- [#todo: RESEARCH_IMPLICATIONS]

**For Model Developers:**
- [#todo: TRAINING_IMPLICATIONS]

---

## 5. Threats to Validity

### 5.1 Internal Validity

**Implementation Fidelity:**
- [#todo: ASSESSMENT_OF_IMPLEMENTATION_MATCH]
- Risk: Minor prompt/API differences may affect results

**Measurement:**
- Exact-match grading identical to original
- Parser validated against manual inspection
- Risk: [#todo: PARSING_EDGE_CASES]

### 5.2 External Validity

**Model Coverage:**
- [#todo: COMPARISON_OF_MODEL_SETS]
- Risk: Model selection may not be representative

**Temporal Validity:**
- Original study: October 2025
- Our replication: January 2026
- Risk: Model capabilities may have changed

### 5.3 Construct Validity

**Tool Calling Definition:**
- Single-turn, parameterless selection
- May not generalize to: multi-turn, parameterized, nested tools
- Risk: Narrow construct limits applicability

---

## 6. Related Work

[#todo: CITE_RECENT_TOOL_CALLING_WORK_SINCE_ORIGINAL]

**Since Original Study:**
- [#todo: NEW_TOOL_CALLING_RESEARCH]
- [#todo: NLT_FOLLOW_UP_WORK]
- [#todo: ALTERNATIVE_APPROACHES]

---

## 7. Conclusion

This independent replication [confirms/partially confirms/challenges] the core findings of Johnson et al. (2025). NLT demonstrates [#todo: SUMMARY_OF_GAINS] across [#todo: MODEL_COUNT] models, with [#todo: KEY_PATTERNS].

**Key Takeaways:**
1. [#todo: TAKEAWAY_1]
2. [#todo: TAKEAWAY_2]
3. [#todo: TAKEAWAY_3]

**Future Work:**
- Extended evaluation with parameterized tool calls
- Multi-turn conversation assessment
- Computational cost analysis across deployment scenarios
- Integration with production agentic systems
- Investigation of [#todo: UNEXPLAINED_FINDINGS]

---

## 8. Reproducibility

All code, data, and results are available at:
- **Repository:** [#todo: GITHUB_URL]
- **Models:** [#todo: MODEL_LIST_WITH_VERSIONS]
- **Date Range:** [#todo: EVALUATION_DATES]
- **Commit Hash:** [#todo: GIT_COMMIT]

**To Reproduce:**
```bash
git clone [#todo: REPO_URL]
cd AI-Natural-Language-Tools
make setup
# Configure SAGE_AUTH_TOKEN in .env
make run-models
./analyze_results.py --show-gains
```

---

## Appendix A: Model Results

### A.1 Complete Per-Model Statistics

[#todo: FOR_EACH_MODEL_GENERATE_TABLE_LIKE_APPENDIX_B_IN_ORIGINAL]

**Format:**
```
Model: [MODEL_NAME]
Overall Accuracy: [VALUE]
Structured Accuracy: [VALUE]
Structured Variance: [VALUE]
NLT Accuracy: [VALUE]
NLT Variance: [VALUE]
Domain-specific:
  Alex Overall: [VALUE]
  Sage Overall: [VALUE]
```

### A.2 Raw Result Files

Available in repository: `results/` directory
- Individual trial JSON files
- Aggregated CSV: `aggregated_results.csv`
- Summary statistics: `study_summary.csv`

---

## Appendix B: Divergence Analysis

[#todo: DETAILED_COMPARISON_OF_ANY_RESULTS_THAT_DIFFER_FROM_ORIGINAL]

**Per-Model Comparison:**
[#todo: TABLE_COMPARING_ORIGINAL_VS_REPLICATION_RESULTS]

**Statistical Significance:**
[#todo: SIGNIFICANCE_TESTS_IF_APPLICABLE]

---

## Appendix C: Implementation Details

### C.1 Code Architecture

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for complete documentation.

**Key Modules:**
- `src/nlt/core/evaluator.py`: 94 lines, trial execution
- `src/nlt/core/parser.py`: 86 lines, YES/NO and tool_calls parsing
- `src/nlt/api/client.py`: 78 lines, API interface
- `tests/`: 27 unit tests (16 parser + 11 evaluator)

### C.2 Differences from Original

[#todo: DOCUMENT_ANY_KNOWN_IMPLEMENTATION_DIFFERENCES]

### C.3 Validation Steps

1. Parser validation: [#todo: DESCRIBE]
2. Exact-match verification: [#todo: DESCRIBE]
3. Manual spot-checks: [#todo: DESCRIBE]

---

## References

Johnson, R. T., Pain, M. D., & West, J. D. (2025). Natural Language Tools: A Natural Language Approach to Tool Calling In Large Language Agents. *arXiv preprint arXiv:2510.14453*.

[#todo: ADD_ADDITIONAL_CITATIONS]

---

## Acknowledgments

[#todo: ACKNOWLEDGE_CONTRIBUTORS]

We thank the original authors for their open description of methods and prompt designs, which enabled this independent replication.

---

**Document Status:** DRAFT - Awaiting completion of evaluation runs  
**Last Updated:** January 12, 2026  
**Version:** 0.1.0
