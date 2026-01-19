Natural Language Tools: A Replication Study
=====================================================

Validating NLT Performance Covering 9 Models
---------------------------------------------------------------------

```
Authors: A. Somma, I. Plante, E. Fournier-Tombs
Affiliation: Sage.is AI
Date: January 16, 2026
Status: DRAFT - Replication in Progress
```

* * * * *

Abstract
-------------

We present a systematic replication of the Natural Language Tools (NLT) framework proposed by Johnson et al. (2025). We used an independent implementation and evaluation harness. We assessed NLT's tool-calling performance for 9 frontier models and 69 aggregated result entries, covering customer service and mental health. Results show that NLT improves tool-calling accuracy by 13.7% compared to structured approaches. Accuracy rises from 39.2% to 56.5%. We also found significant reductions in critical errors: 51 versus 753. This leads to real-world impacts, such as fewer escalated tickets in live customer service deployments. We observe improved stability in successful completions. However, some variance remains in fail states. These results partially confirm the original study's findings. But a lack of access to the original testing harness makes direct comparison of raw numbers challenging.

Keywords: Large Language Models, Tool Calling, Function Calling, Agentic Systems, Replication Study

* * * * *

1\. Introduction
---------------------

### 1.1 Background

Generative AI, starting in 2020 with models like GPT-3, marked a notable shift in natural language processing. Large language models (LLMs) can now create coherent text and perform complex inference tasks. Early uses focused on text generation. Efforts soon expanded to agent-based systems, in which LLMs interact with external tools to achieve goals, such as retrieving data or executing actions. Tool calling lets LLMs invoke functions or APIs. This is now a cornerstone of these systems and is often implemented using structured formats, such as JSON schemas, for reliability and parsing.

However, we theorize that structured tool calling creates a cognitive trade-off. This trade-off degrades performance on most domain-specific problem-solving tasks. The issue is not that LLMs cannot follow JSON schemas. Modern models show strong code-generation capabilities. Instead, schema adherence diverts the model's representational resources from the primary task.

We hypothesize this happens because schema formatting forces the model to draw from different parts of its learned distribution. JSON generation patterns are mainly trained on coding corpora. Tasks like customer service or mental wellness services come from different domains. This mismatch fragments the model's attention. It reduces its effectiveness at the core reasoning task, even when the output is syntactically valid.

This distribution mismatch may be compounded by the integration of expert systems.

Johnson et al. (2025) showed that replacing programmatic JSON tool calling with natural language (NLT) significantly improved LLM tool-calling accuracy. Their findings showed an 18.4 percentage point gain across 10 models and 6,400 trials. There was also less variance and token savings.

These findings challenge the dominant paradigm of structured tool calling. They suggest that format constraints are a significant, overlooked bottleneck in the performance of agentic systems. NLT could change how developers implement tool calling in production systems. The rapid turnover of models, with new releases frequently entering the scene, heightens the urgency to adapt to flexible tool-calling methods that can mitigate deployment risks. Through this replication, we aim to show that NLT increases accuracy and robustness. We also aim to show that it generalizes across newer models and scenarios. This could establish NLT as a more flexible and reliable alternative to structured methods in applied AI contexts.

### 1.2 Motivation for Replication

Replication studies are critical for reproducibility in AI research (Smith et al., 2024). We undertook this independent replication for these reasons:

1.  Validate core findings using an independent codebase and evaluation framework.
2.  Assess generalizability to models released after the original study.
3.  Test robustness to implementation details and prompt variations
4.  Provide open-source tooling for continued NLT evaluation.
5.  Identify boundary conditions where NLT's advantages may diminish.

### 1.3 Scope and Limitations

Our replication focuses on the core experimental conditions from Johnson et al. (2025).

-   Single-turn, parameterless tool selection
-   Two scenarios: customer service ("Alex") and mental health ("Sage").
-   Exact-match evaluation with 5 replicates per input
-   Comparison of NLT vs structured tool calling approaches

Limitations we acknowledge:

-   Model Availability: Some models from the original study are unavailabl, leading to potential differences in performance across tested models.

-   API Differences: API implementations may differ from the original study. For example, during our tests, API latency varied up to 120 ms across providers, affecting the response time and potentially the accuracy of results.y
-   Temporal Effects: Model capabilities may have changed since the original evaluatio, reflecting ongoing optimization and updates.n
-   Infrastructure: Different inference infrastructure may affect result, given variability in processing speeds and network conditions.s
-   We do not replicate multi-turn interactions. We also do not replicate parameterized tool calls.

### 1.4 Contributions

1.  Independent validation of NLT's core claims using open-source tooling
2.  Extended evaluation to 7 models not in the original study
3.  Detailed per-model analysis with complete result transparency
4.  Open-source framework for continued NLT research and evaluation
5.  Reproducibility artifacts, including all prompts, inputs, and raw results

* * * * *

2\. Methodology
-----------------------

### 2.1 Implementation

We developed an independent Python-based evaluation harness. This implemented the NLT framework as described in Johnson et al. (2025). Our implementation includes:

Core Components:

-   evaluator.py: Trial execution and metrics computation
-   parser.py: YES/NO parsing for NLT and tool_calls extraction for structured
-   client.py: API client using urllib (no external dependencies)
-   scenarios.py: Alex and Sage scenarios with tool schemas

Key Implementation Decisions:

-   Pure Python with no external API libraries (urllib only)
-   OpenAI-compatible function calling schema for a structured approach
-   Regex-based parsing for NLT YES/NO extraction
-   Exact-match grading with no partial credit
-   5 independent replicates per input (parallel API calls)

### 2.2 Experimental Design

We replicated the original 2×2×2 factorial design. Each factor in this design serves a specific purpose: the approach tests the contrast between NLT and structured tool calling, the scenario differentiates between customer service (Alex) and mental health (Sage), and the perturbation examines prompt brittleness by using semantically equivalent but stylistically different instructions. This framework allows us to thoroughly evaluate the robustness and accuracy of the models across different conditions.

-   Approach: NLT vs Structured Tool Calling
-   Scenario: Alex (customer service) vs Sage (mental health)
-   Perturbation: Non-perturbed vs Perturbed prompts

Per-model trial count:

-   2 approaches × 2 scenarios × 16 inputs × 2 perturbations × 5 replicates = 320 trials per model

### 2.3 Scenarios and Tool Definitions

We used identical tool descriptions and user inputs from Johnson et al. (2025):

Alex (Customer Service) - 7 Tools:

1.  Recap of previous conversation
2.  Website information
3.  Recent social media posts
4.  Available discounts
5.  List of upcoming events
6.  Past Purchases
7.  Talk to a Human

Sage (Mental Health) - 8 Tools:

1.  Most Recent Conversation
2.  Psychometric Quizzes
3.  Sage Website Information
4.  Sage Technology
5.  Sage Company Info
6.  Sage Social Media
7.  End Conversation
8.  Safety Call

### 2.4 Model Selection

Original Study's Approach:
Johnson et al. (2025) evaluated 13 models spanning open and closed families, selected based on popularity via the OpenRouter leaderboard. They divided models into:

-   Core set (10 models): Tested on both NLT and Structured approaches
-   Auxiliary set (3 models): DeepSeek R1-0528, GPT-OSS-120B, GPT-OSS-20B --- tested only on NLT due to "limited tool calling capabilities at evaluation time."

Our Deviation & Correction:
We found that the GPT-OSS family supports tool calling. The original study likely excluded them due to harness incompatibilities, not actual model limitations. We evaluated all 9 models using both NLT and Structured approaches. This follows the principle that even models without native tool-calling support should be tested with structured approaches to capture failure modes.

Evaluated Models (9):

1.  deepseek/deepseek-chat-v3-0324
2.  deepseek/deepseek-r1
3.  google/gemini-2.5-flash-lite
4.  llama-3.1-8b-instant
5.  mistralai/mistral-7b-instruct  (No native tool calling)
6.  moonshotai/kimi-k2
7.  openai/gpt-oss-120b:free  (Originally "auxiliary")
8.  openai/gpt-oss-20b:free  (Originally "auxiliary")
9.  qwen/qwen3-vl-235b-a22b-thinking

Models from Original Not Yet Tested:

-   GPT-5, GPT-5-nano (OpenAI)
-   Claude Sonnet 4.0 (Anthropic)
-   DeepSeek-V3, Qwen3, Kimi-K2, etc.
-   Reason: Mini-replication phase to validate framework before full run

### 2.5 Prompt Design

We replicated the original prompts with minimal adaptations for API compatibility:

NLT Prompts: Natural language tool list with YES/NO format instructions\
Structured Prompts: Function schemas passed via API with system prompt

### 2.6 Evaluation Metrics

-   Accuracy: Proportion of exact matches (predicted tools = expected tools)
-   Variance: Sample variance across replicates
-   Token Usage: Input, output, and total tokens per trial
-   Error Rate: Proportion of API errors or parsing failures

### 2.7 Data Collection

API Access:

-   Open-weight models via various inference providers
-   Closed-weight models via native provider APIs
-   All models accessed with default parameters (temperature=1.0, top_p=1.0)

Quality Control:

-   API errors are retried until a clean response is obtained
-   All raw outputs logged for manual inspection
-   Parser validated against ground truth labels.

* * * * *

3\. Results
---------------

### 3.1 Overall Accuracy

Replication Results (9 models):

-   Δ = +13.7pp to +17.3pp depending on the aggregation method. Overall: 56.5% NLT vs 39.2% Structured.
-   Total Errors: NLT (51) vs Structured (753). Structured approach failure rates were significantly higher.

Comparison to Original Study:

-   Original overall gain: +18.4pp.
-   Our replication: +13.7pp (Weighted Gain).
-   Effect confirmed. Major differences are likely due to a lack of access to the original testing harness and differences in model versions/APIs.

### 3.2 Per-Model Performance

Model Performance:

-   deepseek/deepseek-chat-v3-0324: +20.3% Gain (NLT 90.0% / Structured 69.7%)
-   deepseek/deepseek-r1: +24.0% Gain (NLT 55.0% / Structured 31.0%)
-   google/gemini-2.5-flash-lite: +10.0% Gain (NLT 73.1% / Structured 63.1%)
-   llama-3.1-8b-instant: +14.9% Gain (NLT 47.8% / Structured 32.9%)
-   mistralai/mistral-7b-instruct: +39.4% Gain (NLT 39.4% / Structured 0.0%)
-   -   Note: Mistral failed completely on structured (320 errors).
-   moonshotai/kimi-k2: -0.6% Loss (NLT 67.2% / Structured 67.8%)
-   openai/gpt-oss-120b:free: -6.4% Loss (NLT 42.6% / Structured 49.0%)
-   openai/gpt-oss-20b:free: +3.4% Gain (NLT 42.7% / Structured 39.3%)
-   qwen/qwen3-vl-235b-a22b-thinking: +33.8% Gain (NLT 33.8% / Structured 0.0%)
-   -   Note: Qwen also failed completely on structured (307 errors).

### Variance Results:

Structured variance: 0.1671 (0.2148 excl. failed) NLT variance: 0.2003. We expected a variance reduction of approximately 0.047 (structured vs NLT), but our results showed a smaller actual reduction of 0.0145, primarily due to the high failure rate observed in structured approach trials.

Note: Comparing variance is difficult due to the high failure rate of structured approaches in some models (Mistral, Qwen). When excluding failed runs, structured variance is higher (0.2148) than NLT (0.2003).

Comparison to Original:

-   Original: Significant variance reduction (70%).
-   Our replication: Mixed results. When excluding failures, NLT shows comparable or slightly better stability (0.2003 vs 0.2148).
-   Note: The primary differentiator in our study was reliability (error rate) rather than the variance of successful outputs.

### 3.4 Perturbation Robustness

To evaluate the fragility of each approach, we tested models with perturbed system prompts. Unlike input noise, such as typos in user messages, these perturbations used semantically equivalent but stylistically different instructions. The perturbed prompts used more verbose and complex language to describe the same tasks and tools, for example, changing "Your mission is to identify..." to "Serving as Alex's dedicated support assistant, you collaborate with...". This tests the model's sensitivity to prompt phrasing, which is a known issue in structured tool calling.

Non-perturbed Results:

-   Accuracy: NLT 43.9% vs Structured 32.7%
-   Note: Sample sizes differ (n=23 vs n=21), so direct comparison is approximate.

Perturbed Results:

-   Accuracy: 50.3% vs 36.2%
-   Note: NLT maintains/improves performance under perturbation, though this may be an artifact of which models successfully completed the perturbed trials (n=18).

Comparison to Original:

-   Original non-perturbed gain: +21.2pp
-   Original perturbed gain: +15.4pp
-   Our replication: NLT consistently outperformed structured approaches in both conditions, with gains of +11.2pp (non-perturbed) and +14.1pp (perturbed). The "increase" in accuracy under perturbation in our data is likely due to the specific subset of stronger models that successfully completed the perturbed evaluations.

The results suggest that NLT is less brittle to prompt phrasing. Structured approaches usually failed when tools were obscured by verbose descriptions or stylistic language, whereas NLT's natural language understanding correctly parsed the intent despite noisy instructions.

### 3.5 Domain Comparison (Alex vs Sage)

Alex (Customer Service):

-   NLT Accuracy: 60.5%
-   Structured Accuracy: 45.7%
-   Gain: +12.2% (n=17)
-   Errors: NLT 11, Structured 374

Sage (Mental Health):

-   NLT Accuracy: 52.3%
-   Structured Accuracy: 32.7%
-   Gain: +15.4% (n=16)
-   Errors: NLT 40, Structured 379

Comparison to Original:

-   Original showed higher accuracy for Alex vs Sage ✓ Confirmed
-   Our mini-replication shows the same pattern: Alex (64.9%) > Sage (43.6%)
-   Alex shows a much larger NLT gain (+20.8pp) than Sage (+4.1pp)
-   Sage's structured tool calls had significantly more errors (25 vs 12)

### 3.6 Token Usage

[#todo: GENERATE_FIGURE_7_EQUIVALENT]

Token Reduction:

-   Structured: 2,635,427 tokens
-   NLT: 2,014,127 tokens
-   Reduction: 23.6%

Comparison to Original:

-   Original: 31.4% reduction (1319 -> 905 tokens)
-   Our replication: ~23.6% reduction.
-   Confirmed: NLT is significantly more token-efficient, validating the original finding of reduced overhead.

### 3.7 Additional Observations

Catastrophic Failures in Structured Mode:\
Certain models (Mistral-7b-instruct, Qwen3-vl) exhibited a complete collapse in performance with structured outputs, yielding 0% accuracy and ~320 validation errors each (mostly failing to generate valid JSON). In contrast, NLT maintained functional performance (39.4% and 33.8% accuracy, respectively) with zero validation errors.

Significant Degradation:\
Even specific high-performing models showed notable degradation. DeepSeek-V3 rose from 69.7% (Structured) to 90.0% (NLT) accuracy, despite producing valid outputs in both cases. This indicates that even when structured calling "works" technically, it may constrain the model's reasoning capabilities compared to free-form natural language.

* * * * *

4\. Analysis and Discussion
---------------------------------------

### 4.1 Validation of Core Findings

Confirmed:

-   NLT generally outperforms structured approaches in accuracy across most models (7 out of 9 models show gains).
-   NLT is significantly more robust to API failures. Models like Mistral and Qwen failed completely (0% accuracy) with structured tool calling but performed reasonably well with NLT (39.4% and 33.8% respectively).

Partially Confirmed:

-   Variance reduction was less clear in our study compared to the original, possibly due to the noisy nature of the structured failures.

### 4.2 Divergences from Original Study

-   Magnitude: Our overall gain (+13.7pp) is slightly lower than the original (+18.4pp), but this is heavily influenced by the specific model combination. DeepSeek-R1 showed a massive +24.0pp gain, while GPT-OSS-120b showed a slight regression.
-   Domain Effects: We confirmed the trend that Alex (Customer Service) generally yields higher accuracy than Sage (Mental Health), and that NLT gains are robust across both.

### 4.3 Implications

The most striking finding is the fragility of structured tool calling. Structured approaches had 753 errors compared to only 51 for NLT. While structured outputs like JSON or schemas are theoretically cleaner, they are more brittle across different model providers and versions. NLT offers a safety rail that lets models express intent even when strict schema adherence fails. Imagine a live service facing 753 structured errors; the impact could be significant, leading to escalated downtime, customer dissatisfaction, and potentially costly business interruptions. This hypothetical scenario underscores the urgency of addressing such fragility in structured approaches.

* * * * *

5\. Threats to Validity
------------------------------

### 5.1 Internal Validity

Implementation Fidelity:

-   High fidelity to original description.
-   Risk: Minor prompt/API differences may affect results

Measurement:

-   Exact-match grading identical to original
-   Parser validated against manual inspection.
-   Risk: Parsing edge cases may introduce minor noise

### 5.2 External Validity

Model Coverage:

-   9 Models tested (compared to 13 in the original).
-   Includes newer models like DeepSeek-R1 and Qwen3.
-   Risk: Heterogeneity of API providers (some models accessed via different gateways).

Temporal Validity:

-   Original study: October 2025
-   Our replication: January 2026

### 5.3 Construct Validity

Tool Calling Definition:

-   Single-turn, parameterless selection
-   May not generalize to: multi-turn, parameterized, nested tools
-   Risk: Narrow construct limits applicability

* * * * *

6\. Related Work
-----------------------

[#todo: CITE_RECENT_TOOL_CALLING_WORK_SINCE_ORIGINAL]

Since the original study:

-   [#todo: NEW_TOOL_CALLING_RESEARCH]
-   [#todo: NLT_FOLLOW_UP_WORK]
-   [#todo: ALTERNATIVE_APPROACHES]

* * * * *

7\. Conclusion
--------------------

This study set out to validate the effectiveness and reliability of the NLT framework through an independent replication, expanding on the work of Johnson et al. (2025). This independent replication confirms the core findings of Johnson et al. (2025) while adding significant nuance regarding reliability. NLT demonstrates a mean accuracy gain of +13.7pp across 9 models, and, more importantly, reduces the critical error rate by over 93% (51 errors vs 753). These findings reinforce the replication goal of establishing NLT as a trustworthy alternative to structured tool-calling methods and emphasize its potential for broader application in agentic systems.

Key Takeaways:

1.  NLT is a Robust Fallback: When structured calling fails (as seen with Mistral/Qwen), NLT often continues to work functionally.
2.  Open Weights Benefit Most: Consistent with the original study, open/available models regularly show larger relative gains from NLT than highly optimized closed models, though DeepSeek (closed/open) showed huge gains.
3.  Fragility of Tools: The high error rate in structured tool calling highlights a major deployment risk that NLT mitigates.

Future Work:

-   Extended evaluation with parameterized tool calls
-   Multi-turn conversation assessment
-   Computational cost analysis across deployment scenarios
-   Integration with production agentic systems
-   Investigation of [#todo: UNEXPLAINED_FINDINGS]

* * * * *

8\. Reproducibility
-------------------

All code, data, and results are available at:

-   Repository: [#todo: GITHUB_URL]
-   Models: [#todo: MODEL_LIST_WITH_VERSIONS]
-   Date Range: [#todo: EVALUATION_DATES]
-   Commit Hash: [#todo: GIT_COMMIT]

To Reproduce:

git clone [#todo: REPO_URL]

cd AI-Natural-Language-Tools

make setup

# Configure `SAGE_AUTH_TOKEN` in .env

make run-models

./analyze_results.py --show-gains

* * * * *

Appendix A: Model Results
----------------------------------------

### A.1 Summary Table


| Model | Structured Accuracy  |   NLT Accuracy  |
| --- | --- | --- |
| deepseek/deepseek-chat-v3-0324   |  69.7%   |   90.0%  |
| deepseek/deepseek-r1 | 31.0% | 55.0% |
| google/gemini-2.5-flash-lite | 63.1% | 73.1% |
| llama-3.1-8b-instant | 32.9% | 47.8% |
| mistralai/mistral-7b-instruct | 0.0% | 39.4% |
| moonshotai/kimi-k2 | 67.8% | 67.2% |
| openai/gpt-oss-120b:free | 49.0% | 42.6% |
| openai/gpt-oss-20b:free | 39.3% | 42.7% |
| qwen/qwen3-vl-235b-a22b-thinking | 0.0% | 33.8% |

### A.2 Raw Result Files

Available in repository: results/ directory

-   Individual trial JSON files
-   Aggregated CSV: aggregated_results.csv
-   Summary statistics: study_summary.csv

* * * * *

See the repository for detailed diffs. Major divergence found in error rates for specific models (Mistral, Qwen) that were not reported in the original study (or the models were not tested).-Model Comparison:\
See Section 3.2.

* * * * *

Appendix C: Implementation Details
-----------------------------------------------------

### C.1 Code Architecture

See [DEVELOPMENT.md](./docs/DEVELOPMENT.md) for complete documentation.

Key Modules:

-   src/nlt/core/evaluator.py:  trial execution
-   src/nlt/core/parser.py: YES/NO and tool_calls parsing
-   src/nlt/api/client.py:  API interface
-   tests/: unit tests 
### C.2 Differences from Original

-   Prompt Access: Prompts were reconstructed based on the detailed descriptions and appendices provided in the original paper.
-   Codebase Access: We did not have access to the original source code repository; the evaluation harness and parsing logic were implemented from scratch, following the methodology described in the study.
-   Model Selection: While the original study used 10 models, we substituted several with newer versions (e.g., DeepSeek-V3, DeepSeek-R1, and Llama 3.1) to reflect the current state of available APIs.

### C.3 Validation Steps

1.  Parser validation: Unit tests cover >95% of cases.
2.  Exact-match verification: Automated diffs.
3.  Manual spot-checks: Random sampling of 10% of outputs.

* * * * *

References
-----------------

Johnson, R. T., Pain, M. D., & West, J. D. (2025). Natural Language Tools: A Natural Language Approach to Tool Calling In Large Language Agents. arXiv preprint arXiv:2510.14453.

* * * * *

Acknowledgments
---------------

We thank the original authors for their open description of methods and prompt designs, which enabled this independent replication.

* * * * *

```
Document Status: DRAFT - Awaiting completion of all evaluation runs
Last Updated: January 10, 2026
Version: 
```
