Natural Language Tools: A Replication Study
=====================================================

Validating NLT Performance Across 14 Models
---------------------------------------------------------------------

```
Authors: A. Somma, I. Plante, E. Fournier-Tombs
Affiliation: Sage.is AI
Date: February 18, 2026
Status: Complete — Follow-up Study Planned
```

* * * * *

![[xkcd-2116-norm-format.png]]
*[xkcd #2116: .NORM Normal File Format](https://xkcd.com/2116/) — Randall Munroe, CC BY-NC 2.5*
*Why are we making the language model stop speaking language?*

* * * * *

Abstract
-------------

We present a systematic replication of the Natural Language Tools (NLT) framework proposed by Johnson et al. (2025). Using an independent implementation and evaluation harness, we assessed NLT's tool-calling performance across 14 models spanning 8,560 trials and 107 aggregated result entries, covering customer service and mental health scenarios. Results show that NLT improves tool-calling accuracy by 14.9 percentage points compared to structured approaches, with accuracy rising from 47.4% to 62.3%. NLT outperformed structured tool calling in 11 of 14 models tested. We also found dramatic reductions in critical errors: 51 for NLT versus 755 for structured approaches — a 93% reduction. NLT achieved a 25.2% reduction in token usage. These results confirm the core findings of the original study while revealing important nuance: highly optimized frontier models (e.g., GPT-5, Gemini 2.0 Flash) show near-parity between approaches, while reasoning models, smaller models, and models without native tool-calling support benefit most from NLT. A lack of access to the original testing harness makes direct comparison of raw numbers challenging. Given these findings, we are planning a more expansive follow-up study to further investigate the boundary conditions of NLT's advantages.

Note on accuracy reporting: Raw accuracy is computed only over valid (non-error) trials. When a model errors on the vast majority of trials (e.g., 76 out of 80), the few surviving responses can produce misleadingly high accuracy figures — a survivorship bias. In this study, we correct for this by treating any condition with errors on 70 or more of 80 trials as an effective 0% accuracy, reflecting operational failure rather than selective success.

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

These findings challenge the dominant paradigm of structured tool calling. They suggest that format constraints are a significant, overlooked bottleneck in the performance of agentic systems. NLT could change how developers implement tool calling in production systems. The rapid turnover of models, with new releases frequently entering the scene, heightens the urgency to adapt to flexible tool-calling methods that can mitigate deployment risks. Through this replication, we aim to validate these claims using a broader model set that includes frontier, reasoning, and open-weight models released since the original study. The results presented here form the basis for a planned follow-up study that will expand the experimental scope beyond the original paper's conditions.

### 1.2 Motivation for Replication

Replication studies are critical for reproducibility in AI research (Smith et al., 2024). We undertook this independent replication for these reasons:

1. Validate core findings using an independent codebase and evaluation framework.
2. Assess generalizability to models released after the original study.
3. Test robustness to implementation details and prompt variations
4. Provide open-source tooling for continued NLT evaluation.
5. Identify boundary conditions where NLT's advantages may diminish.

### 1.3 Scope and Limitations

Our replication focuses on the core experimental conditions from Johnson et al. (2025).

- Single-turn, parameterless tool selection
- Two scenarios: customer service ("Alex") and mental health ("Sage").
- Exact-match evaluation with 5 replicates per input
- Comparison of NLT vs structured tool calling approaches

Limitations we acknowledge:

- Model Availability: Some models from the original study are unavailable, leading to potential differences in performance across tested models. Two of our 14 models have partial data (Gemini 2.5 Pro and Qwen3-VL) due to API availability during the evaluation window.

- API Differences: API implementations may differ from the original study. For example, during our tests, API latency varied up to 120 ms across providers, affecting the response time and potentially the accuracy of results.
- Temporal Effects: Model capabilities may have changed since the original evaluation, reflecting ongoing optimization and updates.
- Infrastructure: Different inference infrastructure may affect results, given variability in processing speeds and network conditions.
- We do not replicate multi-turn interactions. We also do not replicate parameterized tool calls.

### 1.4 Contributions

1. Independent validation of NLT's core claims using open-source tooling
2. Extended evaluation to 14 models, including 5 not in the original study
3. Detailed per-model analysis revealing a capability-dependent pattern in NLT gains
4. Open-source framework for continued NLT research and evaluation
5. Reproducibility artifacts, including all prompts, inputs, and raw results
6. Identification of boundary conditions for a planned follow-up study

* * * * *

2\. Methodology
-----------------------

### 2.1 Implementation

We developed an independent Python-based evaluation harness. This implemented the NLT framework as described in Johnson et al. (2025). Our implementation includes:

Core Components:

- evaluator.py: Trial execution and metrics computation
- parser.py: YES/NO parsing for NLT and tool_calls extraction for structured
- client.py: API client using urllib (no external dependencies)
- scenarios.py: Alex and Sage scenarios with tool schemas

Key Implementation Decisions:

- Pure Python with no external API libraries (urllib only)
- OpenAI-compatible function calling schema for a structured approach
- Regex-based parsing for NLT YES/NO extraction
- Exact-match grading with no partial credit
- 5 independent replicates per input (parallel API calls)

### 2.2 Experimental Design

We replicated the original 2×2×2 factorial design. Each factor in this design serves a specific purpose: the approach tests the contrast between NLT and structured tool calling, the scenario differentiates between customer service (Alex) and mental health (Sage), and the perturbation examines prompt brittleness by using semantically equivalent but stylistically different instructions. This framework allows us to thoroughly evaluate the robustness and accuracy of the models across different conditions.

- Approach: NLT vs Structured Tool Calling
- Scenario: Alex (customer service) vs Sage (mental health)
- Perturbation: Non-perturbed vs Perturbed prompts

Per-model trial count (for models with complete data):

- 2 approaches × 2 scenarios × 16 inputs × 2 perturbations × 5 replicates = 640 trials per model
- Total: 8,560 trials across 14 models (107 aggregated entries)

### 2.3 Scenarios and Tool Definitions

We used identical tool descriptions and user inputs from Johnson et al. (2025):

Alex (Customer Service) - 7 Tools:

1. Recap of previous conversation
2. Website information
3. Recent social media posts
4. Available discounts
5. List of upcoming events
6. Past Purchases
7. Talk to a Human

Sage (Mental Health) - 8 Tools:

1. Most Recent Conversation
2. Psychometric Quizzes
3. Sage Website Information
4. Sage Technology
5. Sage Company Info
6. Sage Social Media
7. End Conversation
8. Safety Call

### 2.4 Model Selection

Original Study's Approach:
Johnson et al. (2025) evaluated 13 models spanning open and closed families, selected based on popularity via the OpenRouter leaderboard. They divided models into:

- Core set (10 models): Tested on both NLT and Structured approaches
- Auxiliary set (3 models): DeepSeek R1-0528, GPT-OSS-120B, GPT-OSS-20B — tested only on NLT due to "limited tool calling capabilities at evaluation time."

Our Approach:
We evaluated 14 models using both NLT and Structured approaches. We found that the GPT-OSS family supports tool calling; the original study likely excluded them due to harness incompatibilities, not actual model limitations. We tested all models with both approaches, including those without native tool-calling support, to capture failure modes. Our model set includes frontier closed-weight models (GPT-5, Claude Sonnet 4, Gemini 2.5 Pro), mid-tier models (Gemini 2.0 Flash, Gemini 2.5 Flash Lite, DeepSeek-V3, Kimi-K2), reasoning models (DeepSeek-R1), and smaller open-weight models (Llama 3.1 8B, Mistral 7B).

Evaluated Models (14):

1. anthropic/claude-sonnet-4
2. deepseek/deepseek-chat-v3-0324
3. deepseek/deepseek-r1
4. google/gemini-2.0-flash-001
5. google/gemini-2.5-flash-lite
6. google/gemini-2.5-pro
7. llama-3.1-8b-instant
8. mistralai/mistral-7b-instruct (No native tool calling)
9. moonshotai/kimi-k2
10. openai/gpt-5
11. openai/gpt-5-nano
12. openai/gpt-oss-120b:free (Originally "auxiliary")
13. openai/gpt-oss-20b:free (Originally "auxiliary")
14. qwen/qwen3-vl-235b-a22b-thinking

Data Completeness: 12 of 14 models have complete data across all 8 conditions. Two models have partial data: Google Gemini 2.5 Pro (6 of 8 conditions) and Qwen3-VL (5 of 8 conditions) due to API availability during the evaluation window.

### 2.5 Prompt Design

We replicated the original prompts with minimal adaptations for API compatibility:

NLT Prompts: Natural language tool list with YES/NO format instructions\
Structured Prompts: Function schemas passed via API with system prompt

### 2.6 Evaluation Metrics

- Accuracy: Proportion of exact matches (predicted tools = expected tools)
- Corrected Accuracy: When a condition produces errors on ≥70 of 80 trials, we treat it as an effective 0% accuracy. Raw accuracy over only surviving trials introduces a survivorship bias — a model that errors on 76/80 trials but gets the remaining 4 correct would report 100% accuracy, misrepresenting what is effectively a catastrophic failure. This correction affects 4 of 107 entries (all Qwen structured conditions and all Mistral structured conditions).
- Variance: Sample variance across replicates
- Token Usage: Input, output, and total tokens per trial
- Error Rate: Proportion of API errors or parsing failures

### 2.7 Data Collection

API Access:

- Open-weight models via various inference providers
- Closed-weight models via native provider APIs
- All models accessed with default parameters (temperature=1.0, top_p=1.0)

Quality Control:

- API errors are retried until a clean response is obtained
- All raw outputs logged for manual inspection
- Parser validated against ground truth labels.

* * * * *

3\. Results
---------------

### 3.1 Overall Accuracy

![[nlt-hero-gains.png]]
*Charts generated by [generate-charts.py](./assets/generate-charts.py)*

Replication Results (14 models, 107 entries, 8,560 trials):

- NLT accuracy: 62.3% vs Structured accuracy: 47.4% (corrected).
- Δ = +14.9pp overall gain.
- Total Errors: NLT (51) vs Structured (755). Structured approach failure rates were dramatically higher — a 93% error reduction with NLT.
- NLT outperformed structured approaches in 11 of 14 models.

![[nlt-error-cliff.png]]

Note: Structured accuracy uses corrected figures. Raw structured accuracy was 51.9%, but this is inflated by survivorship bias in conditions where nearly all trials errored (see Section 2.6). For example, Qwen's structured Alex non-perturbed condition errored on 76 of 80 trials but reported 100% accuracy on the 4 surviving responses. We correct such conditions (errors ≥ 70/80) to 0% accuracy.

Comparison to Original Study:

- Original overall gain: +18.4pp across 10 models and 6,400 trials.
- Our replication: +14.9pp across 14 models and 8,560 trials (corrected).
- The effect is confirmed. The remaining gap is primarily explained by the inclusion of frontier models (GPT-5, Gemini 2.5 Pro) that have been heavily optimized for structured tool calling, showing near-parity or reversed gains. Differences are also likely due to model selection, lack of access to the original testing harness, and improvements in structured tool-calling support in newer model generations.

### 3.2 Per-Model Performance

Model Performance (sorted by NLT gain):

- anthropic/claude-sonnet-4: **+43.1pp** Gain (NLT 61.9% / Structured 18.8%)
  - Note: Largest NLT gain in our study. Claude's structured accuracy was exceptionally low despite being a frontier model.
- mistralai/mistral-7b-instruct: **+39.4pp** Gain (NLT 39.4% / Structured 0.0%)
  - Note: Mistral failed completely on structured (320 errors). No native tool-calling support.
- deepseek/deepseek-r1: **+24.0pp** Gain (NLT 55.0% / Structured 31.0%)
  - Note: Reasoning model shows large NLT gains, suggesting chain-of-thought interferes with structured output.
- deepseek/deepseek-chat-v3-0324: **+20.3pp** Gain (NLT 90.0% / Structured 69.7%)
- openai/gpt-5-nano: **+19.7pp** Gain (NLT 79.1% / Structured 59.4%)
- llama-3.1-8b-instant: **+14.9pp** Gain (NLT 47.8% / Structured 32.9%)
- google/gemini-2.5-flash-lite: **+10.0pp** Gain (NLT 73.1% / Structured 63.1%)
- google/gemini-2.0-flash-001: **+5.5pp** Gain (NLT 85.0% / Structured 79.5%)
- openai/gpt-oss-20b:free: **+3.4pp** Gain (NLT 42.7% / Structured 39.3%)
- openai/gpt-5: **+1.6pp** Gain (NLT 81.9% / Structured 80.3%)
  - Note: Near-parity. GPT-5's structured tool calling is highly optimized.
- moonshotai/kimi-k2: **−0.6pp** Loss (NLT 67.2% / Structured 67.8%)
- openai/gpt-oss-120b:free: **−6.4pp** Loss (NLT 42.6% / Structured 49.0%)
- qwen/qwen3-vl-235b-a22b-thinking: **+33.8pp** Gain (NLT 33.8% / Structured 0.0% corrected)
  - Note: Partial data (1 NLT entry vs 4 structured). Structured had 307 errors out of 320 trials. Raw accuracy was 60.7% due to survivorship bias — the few non-error responses happened to be correct. We correct to 0% as all 4 conditions had ≥ 73 errors out of 80 trials, representing operational failure.
- google/gemini-2.5-pro: **−33.7pp** Loss (NLT 48.3% / Structured 82.1%)
  - Note: Partial data (3 entries each). Gemini 2.5 Pro is the strongest outlier favoring structured tool calling.

![[nlt-paired-accuracy.png]]

### 3.3 Variance Results

NLT variance: 0.1913. Structured variance: 0.1702.

Unlike the original study, which reported a 70% variance reduction with NLT, our results show comparable variance between approaches. This is primarily because structured approach failures (755 errors producing 0% accuracy) compress the measured variance. When a model fails entirely on structured (e.g., Mistral with 0% accuracy and zero variance), it artificially deflates the aggregate structured variance. The variance comparison is therefore less meaningful than the error rate comparison.

Comparison to Original:

- Original: Significant variance reduction (70%) with NLT.
- Our replication: Mixed results. NLT variance (0.1913) is slightly higher than structured (0.1702), but this is confounded by systematic structured failures.
- The primary differentiator in our study was reliability (error rate) rather than the variance of successful outputs.

### 3.4 Perturbation Robustness

To evaluate the fragility of each approach, we tested models with perturbed system prompts. Unlike input noise, such as typos in user messages, these perturbations used semantically equivalent but stylistically different instructions. The perturbed prompts used more verbose and complex language to describe the same tasks and tools, for example, changing "Your mission is to identify..." to "Serving as Alex's dedicated support assistant, you collaborate with...". This tests the model's sensitivity to prompt phrasing, which is a known issue in structured tool calling.

Non-perturbed Results (n=26 NLT, n=27 Structured):

- NLT: 62.4% vs Structured: 46.1% (corrected)
- Gain: +16.4pp

Perturbed Results (n=26 NLT, n=28 Structured):

- NLT: 62.2% vs Structured: 48.8% (corrected)
- Gain: +13.4pp

Comparison to Original:

- Original non-perturbed gain: +21.2pp
- Original perturbed gain: +15.4pp
- Our replication: NLT consistently outperformed structured approaches in both conditions, with corrected gains of +16.4pp (non-perturbed) and +13.4pp (perturbed). NLT accuracy was stable across perturbation states (62.4% vs 62.2%), demonstrating robustness to prompt phrasing. Structured accuracy also remained relatively stable after correction (46.1% vs 48.8%), suggesting the perturbation effect is less pronounced in our model set than in the original study.

### 3.5 Domain Comparison (Alex vs Sage)

Alex (Customer Service):

- NLT Accuracy: 66.2% (n=26, 11 errors)
- Structured Accuracy: 52.7% (n=27, 374 errors, corrected)
- Gain: +13.4pp

Sage (Mental Health):

- NLT Accuracy: 58.5% (n=26, 40 errors)
- Structured Accuracy: 42.4% (n=28, 381 errors, corrected)
- Gain: +16.1pp

Comparison to Original:

- Original showed higher accuracy for Alex vs Sage. ✓ Confirmed.
- Alex (66.2%) > Sage (58.5%) across both approaches. ✓ Confirmed.
- NLT gain is larger for Sage (+16.1pp) than Alex (+13.4pp), suggesting NLT provides greater benefit in the more complex mental health domain where structured approaches struggle most.
- Error counts are nearly equal across domains (NLT: 11 vs 40; Structured: 374 vs 381), indicating structured fragility is domain-independent.

### 3.6 Token Usage

Token Reduction:

- NLT: 3,384,196 tokens
- Structured: 4,522,651 tokens
- Reduction: 25.2%

![[nlt-token-savings.png]]

Comparison to Original:

- Original: 31.4% reduction (1,319 → 905 tokens per trial).
- Our replication: 25.2% reduction.
- Confirmed: NLT is significantly more token-efficient, validating the original finding of reduced overhead. The slightly lower reduction may reflect model-specific differences in response verbosity across our expanded model set.

### 3.7 Additional Observations

Catastrophic Failures in Structured Mode:\
Certain models (Mistral-7B-Instruct, Qwen3-VL) exhibited complete collapse in performance with structured outputs, yielding 0% accuracy and hundreds of validation errors (mostly failing to generate valid JSON). In contrast, NLT maintained functional performance (39.4% and 33.8% accuracy, respectively) with zero validation errors. This pattern was also observed, unexpectedly, with Claude Sonnet 4, which achieved only 18.8% structured accuracy despite being a frontier model — suggesting that even highly capable models may have suboptimal structured tool-calling implementations depending on the API integration path.

Frontier Model Convergence:\
GPT-5 and Gemini 2.0 Flash showed near-parity between NLT and structured approaches (+1.6pp and +5.5pp respectively), with both achieving over 80% accuracy in both modes. This suggests that highly optimized frontier models may have narrowed the distribution mismatch that NLT exploits, through extensive tool-calling fine-tuning. Gemini 2.5 Pro went further, showing a strong structured advantage (−33.7pp), indicating that some models have been specifically optimized for structured output to the point where NLT is disadvantageous.

Reasoning Model Penalty:\
DeepSeek-R1, a reasoning model, showed a large NLT gain (+24.0pp). Reasoning models generate extended chain-of-thought sequences before producing output. When constrained to structured formats, this reasoning process may conflict with the format requirements, degrading accuracy. NLT's free-form output accommodates the reasoning trace naturally.

* * * * *

4\. Analysis and Discussion
---------------------------------------

### 4.1 Validation of Core Findings

Confirmed:

- NLT outperforms structured approaches in accuracy across the majority of models (11 of 14 models show gains after correcting for survivorship bias).
- NLT is significantly more robust to API failures. Models like Mistral and Qwen failed completely (0% effective accuracy) with structured tool calling but performed reasonably well with NLT (39.4% and 33.8% respectively). Claude Sonnet 4, despite being a frontier model, achieved only 18.8% structured accuracy versus 61.9% with NLT.
- NLT reduces token usage (25.2% reduction), consistent with the original finding (31.4%).
- Alex (customer service) yields higher accuracy than Sage (mental health) across both approaches.

Partially Confirmed:

- Variance reduction was not observed in our study. NLT variance (0.1913) was slightly higher than structured (0.1702), though this comparison is confounded by systematic structured failures that compress measured variance.

Not Confirmed:

- Universal NLT advantage. Three models showed structured advantages after correction (Gemini 2.5 Pro, GPT-OSS-120B, Kimi-K2). Qwen3-VL originally appeared to favor structured (+60.7%), but this was a survivorship artifact — with 307 of 320 trials erroring, the corrected structured accuracy is 0%, reversing its direction to a +33.8pp NLT gain.

### 4.2 Divergences from Original Study

- Magnitude: Our corrected overall gain (+14.9pp) is close to the original (+18.4pp). The remaining gap is partly explained by the inclusion of frontier models that have been heavily optimized for structured tool calling (GPT-5 at +1.6pp, Gemini 2.5 Pro at −33.7pp). The original study's model set may have been more susceptible to the distribution mismatch that NLT addresses.
- Direction: The original study showed NLT gains across all tested models. Our study shows 3 models where structured genuinely outperforms NLT (Gemini 2.5 Pro, GPT-OSS-120B, Kimi-K2), suggesting that structured tool-calling optimization in newer model generations can eliminate or reverse the NLT advantage for specific models. A fourth model (Qwen3-VL) initially appeared to favor structured, but this was an artifact of survivorship bias in near-total structured failure.
- Variance: The original study found a 70% variance reduction with NLT. Our study found no meaningful variance difference, likely due to the different composition of models tested and the high structured failure rate.

### 4.3 Emerging Patterns

The most striking finding is the heterogeneity of the NLT effect across model types:

1. **Models without native tool calling** (Mistral 7B): NLT provides an essential capability that structured approaches cannot deliver. These models show the highest NLT gains by eliminating complete structured failure.

2. **Reasoning models** (DeepSeek-R1): NLT accommodates chain-of-thought reasoning naturally, while structured formats conflict with extended reasoning traces. Large NLT gains (+24.0pp).

3. **Mid-tier models** (DeepSeek-V3, Gemini Flash Lite, GPT-5-nano): NLT provides consistent, moderate gains (+10–20pp), suggesting these models have some structured capability but still benefit from the reduced format burden.

4. **Frontier models** (GPT-5, Gemini 2.0 Flash): Near-parity, suggesting extensive tool-calling fine-tuning has narrowed the distribution mismatch. NLT still maintains an edge in error rates.

5. **Structured-optimized models** (Gemini 2.5 Pro): Strong structured advantage, suggesting that specific optimization for structured output can reverse the NLT effect entirely.

![[nlt-capability-gradient.png]]

### 4.4 Implications

The fragility of structured tool calling remains the most deployment-relevant finding. Structured approaches produced 755 errors compared to only 51 for NLT — a 93% reduction. In a production environment, this error rate differential translates directly to service reliability. While structured outputs like JSON or schemas are theoretically cleaner, they are more brittle across different model providers and versions. NLT offers a safety rail that lets models express intent even when strict schema adherence fails.

The pattern of frontier model convergence raises an important question for the field: as models continue to be optimized for structured tool calling, will NLT's accuracy advantage diminish entirely? Our data suggests this is already happening for the most capable models, but NLT's error-rate advantage persists even when accuracy converges. This warrants further investigation in our planned follow-up study.

* * * * *

5\. Threats to Validity
------------------------------

### 5.1 Internal Validity

Implementation Fidelity:

- High fidelity to original description.
- Risk: Minor prompt/API differences may affect results

Measurement:

- Exact-match grading identical to original
- Parser validated against manual inspection.
- Risk: Parsing edge cases may introduce minor noise

### 5.2 External Validity

Model Coverage:

- 14 models tested (compared to 13 in the original), with 12 having complete data.
- Includes newer models: GPT-5, GPT-5-nano, Claude Sonnet 4, Gemini 2.5 Pro, DeepSeek-R1, Kimi-K2.
- Risk: Heterogeneity of API providers (some models accessed via different gateways).
- Risk: Two models with partial data (Gemini 2.5 Pro, Qwen3-VL) may not fully represent their capabilities.

Temporal Validity:

- Original study: October 2025
- Our replication: January–February 2026

### 5.3 Construct Validity

Tool Calling Definition:

- Single-turn, parameterless selection
- May not generalize to: multi-turn, parameterized, nested tools
- Risk: Narrow construct limits applicability

* * * * *

6\. Related Work
-----------------------

The NLT framework sits at the intersection of tool calling, prompt engineering, and agentic systems research. Since the original study by Johnson et al. (2025), the field has continued to evolve rapidly. Structured tool calling remains the dominant paradigm in production systems, with OpenAI, Google, and Anthropic all providing native function-calling APIs. However, the reliability challenges we document here echo broader concerns in the literature about the brittleness of constrained generation formats. Our findings are consistent with recent work on prompt sensitivity in LLMs, where minor phrasing changes can significantly affect model behavior, and with research on the tension between format compliance and task performance in instruction-following models.

* * * * *

7\. Conclusion
--------------------

This independent replication confirms the core findings of Johnson et al. (2025) while significantly expanding the evidence base. Across 14 models and 8,560 trials, NLT demonstrates a corrected mean accuracy gain of +14.9pp over structured tool calling, with 11 of 14 models showing improvements. More importantly, NLT reduces the critical error rate by 93% (51 errors vs 755), establishing it as a substantially more reliable approach to tool calling in production environments.

Our expanded model set reveals important nuance not present in the original study. The NLT advantage is not uniform — it follows a clear pattern related to model capability and optimization:

Key Takeaways:

1. **NLT as a Reliability Mechanism**: The 93% error reduction is the most deployment-relevant finding. Even when accuracy converges (as with GPT-5), NLT maintains lower error rates.
2. **Capability-Dependent Gains**: Models without native tool calling, reasoning models, and smaller models benefit most from NLT. Frontier models with extensive tool-calling fine-tuning show diminished or reversed gains.
3. **Open-Weight Models Benefit Most**: Consistent with the original study, open and smaller models regularly show larger relative gains from NLT, reinforcing its value as an equalizer across model tiers.
4. **Structured Fragility Persists**: Despite advances in structured tool-calling support, the high error rate (755 errors) highlights ongoing deployment risks that NLT mitigates.

### Follow-up Study

Given these findings, which broadly support the claims of Johnson et al. (2025), we are planning a more expansive follow-up study that will:

- Extend the evaluation to multi-turn interactions and parameterized tool calls
- Investigate the capability-dependent pattern more systematically across a wider range of model sizes
- Assess NLT performance in production-scale agentic systems
- Conduct computational cost analysis across deployment scenarios
- Explore hybrid approaches that combine NLT's reliability with structured output's parseability
- Test with additional scenarios beyond customer service and mental health

* * * * *

8\. Reproducibility
-------------------

All code, data, and results are available at:

- Repository: https://github.com/Sage-Future/AI-Natural-Language-Tools
- Models: 14 models (see Section 2.4 and models.csv)
- Date Range: January 12 – February 17, 2026
- Total Trials: 8,560 across 107 aggregated entries

To Reproduce:

```bash
git clone https://github.com/Sage-Future/AI-Natural-Language-Tools.git
cd AI-Natural-Language-Tools
make setup
# Configure SAGE_AUTH_TOKEN in .env
make run-models
python src/scripts/analyze_results.py --show-gains
```

* * * * *

Appendix A: Model Results
----------------------------------------

### A.1 Summary Table

| Model | NLT Accuracy | Structured Accuracy | Gain | NLT Errors | Struct Errors |
| --- | --- | --- | --- | --- | --- |
| anthropic/claude-sonnet-4 | 61.9% | 18.8% | **+43.1pp** | 0 | 0 |
| deepseek/deepseek-chat-v3-0324 | 90.0% | 69.7% | **+20.3pp** | 0 | 0 |
| deepseek/deepseek-r1 | 55.0% | 31.0% | **+24.0pp** | 0 | 1 |
| google/gemini-2.0-flash-001 | 85.0% | 79.5% | **+5.5pp** | 0 | 2 |
| google/gemini-2.5-flash-lite | 73.1% | 63.1% | **+10.0pp** | 0 | 0 |
| google/gemini-2.5-pro* | 48.3% | 82.1% | −33.7pp | 0 | 0 |
| llama-3.1-8b-instant | 47.8% | 32.9% | **+14.9pp** | 0 | 37 |
| mistralai/mistral-7b-instruct | 39.4% | 0.0% | **+39.4pp** | 0 | 320 |
| moonshotai/kimi-k2 | 67.2% | 67.8% | −0.6pp | 0 | 0 |
| openai/gpt-5 | 81.9% | 80.3% | **+1.6pp** | 0 | 0 |
| openai/gpt-5-nano | 79.1% | 59.4% | **+19.7pp** | 0 | 0 |
| openai/gpt-oss-120b:free | 42.6% | 49.0% | −6.4pp | 21 | 54 |
| openai/gpt-oss-20b:free | 42.7% | 39.3% | **+3.4pp** | 30 | 34 |
| qwen/qwen3-vl-235b-a22b-thinking* | 33.8% | 0.0%† | **+33.8pp** | 0 | 307 |

\* Partial data. See Section 2.4 for details.

† Corrected for survivorship bias. Raw structured accuracy was 60.7%, computed over only the few non-error responses out of 320 trials (307 errors). See Section 2.6.

### A.2 Raw Result Files

Available in repository: results/ directory

- Individual trial JSON files
- Aggregated CSV: aggregated_results.csv
- Summary statistics: study_summary.csv

* * * * *

See Appendix A for the full summary table and the repository for detailed diffs. Notable divergences include the catastrophic structured failure modes for Mistral and Qwen (320 and 307 errors respectively, both corrected to 0% effective accuracy), the unexpected structured weakness of Claude Sonnet 4 (18.8%), and the strong structured advantage shown by Gemini 2.5 Pro (82.1% structured vs 48.3% NLT).

* * * * *

Appendix C: Implementation Details
-----------------------------------------------------

### C.1 Code Architecture

See [DEVELOPMENT.md](./docs/DEVELOPMENT.md) for complete documentation.

Key Modules:

- src/nlt/core/evaluator.py:  trial execution
- src/nlt/core/parser.py: YES/NO and tool_calls parsing
- src/nlt/api/client.py:  API interface
- tests/: unit tests

### C.2 Differences from Original

- Prompt Access: Prompts were reconstructed based on the detailed descriptions and appendices provided in the original paper.
- Codebase Access: We did not have access to the original source code repository; the evaluation harness and parsing logic were implemented from scratch, following the methodology described in the study.
- Model Selection: We tested 14 models, compared to 13 in the original. Our set includes models released after the original study (GPT-5, GPT-5-nano, Claude Sonnet 4, Gemini 2.5 Pro) and differs in some models from the original set. All models were tested with both NLT and structured approaches, including the "auxiliary" models that the original study tested only with NLT.

### C.3 Validation Steps

1. Parser validation: Unit tests cover >95% of cases.
2. Exact-match verification: Automated diffs.
3. Manual spot-checks: Random sampling of 10% of outputs.

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
Document Status: Complete — Follow-up Study Planned
Last Updated: Feb 18, 2026
Version: 1.0
```
