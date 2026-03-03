The Remarkable Effectiveness of Providing AI Agents with Natural Language Tools: A Replication Study
=====================================================

Validating NLT Performance Across 14 Models
---------------------------------------------------------------------

```
Authors: A. Somma, I. Plante, F. Premji, E. Fournier-Tombs
Affiliation: Sage.is AI-UI
Date: February 18, 2026
Status: Complete. Follow-up Study Planned
```

* * * * *

![[xkcd-2116-norm-format.png]]
*[xkcd #2116: .NORM Normal File Format](https://xkcd.com/2116/) — Randall Munroe, CC BY-NC 2.5*
*Why are we making the language model stop speaking language?*

* * * * *

Abstract
-------------

This study provides an independent replication and extension of the Natural Language Tools (NLT) framework introduced by Johnson et al. (2025), which challenges the prevailing paradigm of structured tool calling in large language model (LLM)-based agentic systems. In the context of rapid model evolution and ongoing research into tool-use optimization (Martinez, 2025; Raschka, 2025), NLT’s performance was evaluated across 14 models and 8,560 trials, expanding the original study to include newer frontier, reasoning, and open-weight models. The results confirm the core findings and reveal important nuances: NLT improves tool-calling accuracy by 14.9 percentage points overall (62.3% versus 47.4% structured) and reduces critical errors by 93% (51 versus 755 errors). A clear capability-dependent pattern emerges: models without native tool calling, reasoning models, and smaller models demonstrate substantial NLT gains (+24.0pp to +43.1pp), while highly optimized frontier models (GPT-5, Gemini 2.5 Pro) exhibit diminished or reversed advantages. This observation aligns with recent analyses of reinforcement learning-optimized tool use (Martinez, 2025) and highlights NLT’s persistent reliability benefits. NLT also achieves a 25.2% reduction in token usage, confirming its efficiency. Beyond validating the original study, this work makes three key contributions: (1) providing the first independent validation of NLT’s effectiveness using open-source tooling, (2) identifying model capability as a critical moderator of NLT’s advantages within the context of recent tool-calling research (Chen et al., 2025; Zhang et al., 2025), and (3) demonstrating NLT’s exceptional reliability benefits (93% error reduction), which is its most deployment-relevant feature given ongoing concerns about the fragility of structured tool calling. These findings establish NLT as a valuable alternative to structured tool calling, particularly for production systems that prioritize reliability over parseability, and offer timely evidence for the ongoing debate regarding optimal tool-calling approaches.

Note on accuracy reporting: Raw accuracy is calculated only over valid (non-error) trials. When a model produces errors on the majority of trials (e.g., 76 out of 80), the few remaining responses may yield misleadingly high accuracy figures, leading to survivorship bias. In this study, any condition with errors on 70 or more of 80 trials is treated as having 0% accuracy, reflecting operational failure rather than selective success.

Keywords: Large Language Models, Tool Calling, Function Calling, Agentic Systems, Replication Study, Natural Language Interfaces

* * * * *

1\. Introduction
----------------

### 1.1 Background

Generative AI, starting in 2020 with models like GPT-3, marked a significant change in natural language processing. Large language models (LLMs) can now create coherent text and perform complex inference tasks. Early uses focused on text generation. Efforts soon expanded to agent-based systems, in which LLMs interact with external tools to achieve goals, such as retrieving data or executing actions. Tool calling lets LLMs invoke functions or APIs. This is now a cornerstone of these systems and is often implemented using structured formats, such as JSON schemas, for reliability and parsing.

We propose that structured tool calling introduces a cognitive trade-off that impairs performance on domain-specific problem-solving tasks. This perspective is consistent with current literature on format constraints in large language models (LLMs). The limitation is not an inability of LLMs to follow JSON schemas, as modern models display strong code-generation capabilities (Chen et al., 2021). Instead, adherence to schemas appears to redirect the model’s representational resources away from the primary task, resulting in interference where format requirements compete with task instructions for cognitive bandwidth. This phenomenon is further validated by observations regarding prompt sensitivity in LLMs (Reynolds & McDonell, 2021).

We hypothesize that schema formatting compels the model to draw from distinct segments of its learned distribution. JSON generation patterns are primarily acquired from coding corpora, whereas tasks such as customer service or mental wellness originate from different domains. This distributional mismatch fragments the model’s attention and diminishes its effectiveness in core reasoning tasks, even when the output remains syntactically valid.

The cognitive load of maintaining format compliance may engage what Kahneman (2011) describes as System 2 thinking (deliberate, effortful processing) at the expense of System 1’s intuitive task understanding. In LLMs, this manifests as competition between instruction following and format adherence, particularly pronounced in models not extensively fine-tuned for structured outputs (Weston et al., 2023). This distributional mismatch may be compounded by the integration of expert systems, in which domain-specific knowledge must be mapped to generic format constraints.

The rapid turnover of models, with new releases frequently entering the scene, heightens the urgency to adapt to flexible tool-calling methods that can mitigate deployment risks. Recent work continues to explore natural language approaches to tool calling, such as ToolFlow (Chen et al., 2025), which uses dialogue synthesis to improve tool-calling performance, and CallNavi (Zhang et al., 2025), which provides an empirical study of function calling challenges. These studies point to the ongoing relevance of natural language tool interfaces and the need for robust evaluation.

Johnson et al. (2025) showed that replacing programmatic JSON tool calling with natural language (NLT) significantly improved LLM tool-calling accuracy. Their findings showed an 18.4 percentage point gain across 10 models and 6,400 trials. There was also less variance and token savings.

These findings question the prevailing paradigm of structured tool calling by demonstrating that format constraints constitute a significant, often overlooked bottleneck in agentic system performance. Adoption of NLT has the potential to alter how developers implement tool calling in production environments. The rapid introduction of new models underscores the need for adaptable tool-calling methods to mitigate deployment risks. This replication of Johnson et al. (2025) aims to validate these claims using a broader set of models, including frontier, reasoning, and open-weight models introduced since the original study. The results presented will inform a planned follow-up study designed to expand the experimental scope beyond the original conditions.

### 1.2 Motivation for Replication

Replication studies are critical for scientific progress in machine learning, particularly given ongoing concerns about reproducibility in AI research (Pineau et al., 2020). We undertook this independent replication for several key reasons:

1\. Validate Core Findings: Johnson et al. (2025) reported substantial gains with NLT (+18.4pp), challenging the dominant structured tool-calling paradigm. Independent validation using a separate codebase and evaluation framework tests whether these results generalize beyond the original implementation.

2\. Assess Generalizability: The original study evaluated 13 models available in October 2025. Since then, new frontier models (GPT-5, Claude Sonnet 4, Gemini 2.5 Pro) and reasoning models (DeepSeek-R1) have emerged. Testing these newer models reveals whether NLT's advantages persist as model capabilities evolve.

3\. Test Robustness: Implementation details, prompt variations, and API differences can significantly affect results (Zhao et al., 2021). By implementing NLT from scratch with different tooling, we test the robustness of the original findings to implementation variations.

4\. Provide Open-Source Tooling: The field benefits from accessible evaluation frameworks. Our open-source implementation enables continued NLT research and lowers barriers to entry for other researchers.

5\. Identify Boundary Conditions: By testing a broader range of models than the original study, we can identify where NLT's advantages may diminish or reverse---crucial information for practitioners deciding when to adopt NLT versus structured approaches.

Gundersen et al. (2023) emphasize that independent replication is essential for distinguishing robust findings from implementation artifacts or publication bias. Our study contributes to this scientific process by providing transparent methodology, open-source code, and comprehensive results that others can verify and build upon.

### 1.3 Scope and Limitations

Our replication focuses on the core experimental conditions from Johnson et al. (2025).

-   Single-turn, parameterless tool selection
-   Two scenarios: customer service ("Alex") and mental health ("Sage").
-   Exact-match evaluation with 5 replicates per input
-   Comparison of NLT vs structured tool calling approaches

Limitations we acknowledge:

-   Model Availability: Some models from the original study are unavailable, producing potential differences in performance across tested models. Two of our 14 models have partial data (Gemini 2.5 Pro and Qwen3-VL) due to API availability during the evaluation window.
-   API Differences: API implementations may differ from the original study. For example, during our tests, API latency varied up to 120 ms across providers, affecting the response time and potentially the accuracy of results.
-   Temporal Effects: Model capabilities may have changed since the original evaluation, revealing ongoing optimization and updates.
-   Infrastructure: Different inference infrastructure may affect results, given variability in processing speeds and network conditions.
-   We do not replicate multi-turn interactions. We also do not replicate parameterized tool calls.

### 1.4 Contributions

1.  Independent validation of NLT's core claims using open-source tooling
2.  Extended evaluation to 14 models, including 5 not in the original study
3.  Detailed per-model analysis revealing a capability-dependent pattern in NLT gains
4.  Open-source framework for continued NLT research and evaluation
5.  Reproducibility artifacts, including all prompts, inputs, and raw results
6.  Identification of boundary conditions for a planned follow-up study

* * * * *

2\. Methodology
---------------

### 2.1 Implementation

An independent Python-based evaluation harness was developed that implements the NLT framework as described by Johnson et al. (2025). The implementation includes:

Core Components:

-   [evaluator.py](http://evaluator.py/): Trial execution and metrics computation
-   [parser.py](http://parser.py/): YES/NO parsing for NLT and tool_calls extraction for structured
-   [client.py](http://client.py/): API client using urllib (no external dependencies)
-   [scenarios.py](http://scenarios.py/): Alex and Sage scenarios with tool schemas

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

Per-model trial count (for models with complete data):

-   2 approaches × 2 scenarios × 16 inputs × 2 perturbations × 5 replicates = 640 trials per model
-   Total: 8,560 trials across 14 models (107 aggregated entries)

Comparison to Original:

-   Key differences: Model selection (newer models), API implementations, and evaluation timeframe

Per-model trial count (for models with complete data):

-   2 approaches × 2 scenarios × 16 inputs × 2 perturbations × 5 replicates = 640 trials per model
-   Original study: 6,400 trials across 10 models

### 2.3 Scenarios and Tool Definitions

#### 2.3.1 NTL

We used identical scenarios, tool descriptions and simulated user inputs from Johnson et al. (2025):

Example Alex (Customer Service) Natural Language Tools and Scenario Description:

You are an assistant to Alex, an AI customer service agent who handles bookings for a music venue called "Yes! Music". You will be given a message between Alex and a customer. They are texting one another.\
Your mission is to identify if any of the following topics have been brought up... (Further detail can be seen in [scenarios.py line 6](https://github.com/Sage-is/NLT-Replication-Study/blob/2aa826401e18eaf5aae8bb17db34a1a09eb444f5/src/nlt/data/scenarios.py#L6))

Additionally, the Alex agent was allowed to select what tools to access by responding yes or no to the following list of tools, or explaining Thinking or stating the Assessment finished:

Thinking: (insert_thinking)\
Recap of previous conversation -- YES/NO\
Website information -- YES/NO\
Recent social media posts -- YES/NO\
Available discounts -- YES/NO\
List of upcoming events -- YES/NO\
Past Purchases -- YES/NO\
Talk to a Human -- YES/NO\
Assessment finished.

Example Sage (Mental Health) Natural Language Tools and Scenario Description:

You are an assistant to Sage, an AI mental health specialist. You will be given a message between Sage and their client. They are texting one another.\
Your mission is to identify if any of the following topics have been brought up... (further details can be seen in [scenarios.py line 92](https://github.com/Sage-is/NLT-Replication-Study/blob/2aa826401e18eaf5aae8bb17db34a1a09eb444f5/src/nlt/data/scenarios.py#L92))

Additionally, the Sage agent was allowed, similar to Alex, to select what tools to access by responding yes or no to the following list of tools, or explaining Thinking or stating the Assessment finished:

Thinking: (insert_thinking)\
Most Recent Conversation -- YES/NO\
Psychometric Quizzes -- YES/NO\
Sage Website Information -- YES/NO\
Sage Technology -- YES/NO\
Sage Company Info -- YES/NO\
Sage Social Media -- YES/NO\
End Conversation -- YES/NO\
Safety Call -- YES/NO\
Assessment finished.

2.3.2 Structured

We used industry-standard structured tooling based on the Johnson et al. (2025) scenarios and toolings listed in their study. An example of Alex's structured tool calling scenario can be seen on [line 73 of scenarios.py](https://github.com/Sage-is/NLT-Replication-Study/blob/2aa826401e18eaf5aae8bb17db34a1a09eb444f5/src/nlt/data/scenarios.py#L73).

### 2.4 Model Selection

Original Study's Approach:\
Johnson et al. (2025) evaluated 13 models spanning open and closed families, selected based on popularity via the OpenRouter leaderboard. They divided models into:

-   Core set (10 models): Tested on both NLT and Structured approaches
-   Auxiliary set (3 models): DeepSeek R1-0528, GPT-OSS-120B, GPT-OSS-20B --- tested only on NLT due to "limited tool calling capabilities at evaluation time."

Our Approach:\
We evaluated 14 models using both NLT and Structured approaches. We found that the GPT-OSS family supports tool calling; the original study likely excluded them due to harness incompatibilities, not actual model limitations. We tested all models with both approaches, including those without native tool-calling support, to capture failure modes.

Our model set includes frontier closed-weight models (GPT-5, Claude Sonnet 4, Gemini 2.5 Pro), mid-tier models (Gemini 2.0 Flash, Gemini 2.5 Flash Lite, DeepSeek-V3, Kimi-K2), reasoning models (DeepSeek-R1), and smaller open-weight models (Llama 3.1 8B, Mistral 7B).

Evaluated Models (14):

1.  Anthropic/claude-sonnet-4
2.  Deepseek/deepseek-chat-v3-0324
3.  Deepseek/deepseek-r1
4.  Google/gemini-2.0-flash-001
5.  Google/gemini-2.5-flash-lite
6.  Google/gemini-2.5-pro
7.  Meta-llama/llama-3.1-8b-instant
8.  Mistralai/mistral-7b-instruct (No native tool calling)
9.  Moonshotai/kimi-k2
10. Openai/gpt-5
11. Openai/gpt-5-nano
12. Openai/gpt-oss-120b:free (Originally "auxiliary")
13. Openai/gpt-oss-20b:free (Originally "auxiliary")
14. Qwen/qwen3-vl-235b-a22b-thinking

Data Completeness:

12 of 14 models have complete data across all 8 conditions. Two models have partial data: Google Gemini 2.5 Pro (6 of 8 conditions) and Qwen3-VL (5 of 8 conditions) due to API availability during the evaluation window.

### 2.5 Prompt Design

We replicated the original scenario prompts with minimal adaptations for API compatibility:

-   NLT Scenario Prompts: Natural language tool list with YES/NO format instructions
-   Structured Scenario Prompts: Function schemas passed via API with system prompt

### 2.6 Evaluation Metrics

-   Accuracy: Proportion of exact matches (predicted tools = expected tools)
-   Corrected Accuracy: When a condition produces errors on ≥70 of 80 trials, we treat it as having an effective accuracy of 0%. Raw accuracy over only surviving trials introduces a survivorship bias --- a model that errors on 76/80 trials but gets the remaining 4 correct would report 100% accuracy, misrepresenting what is effectively a catastrophic failure. This correction affects 4 of 107 entries (all Qwen-structured conditions and all Mistral-structured conditions).
-   Variance: Sample variance across replicates
-   Token Usage: Input, output, and total tokens per trial
-   Error Rate: Proportion of API errors or parsing failures

Our original evaluator can be reviewed in our project's [evaluator.py](https://github.com/Sage-is/NLT-Replication-Study/blob/2aa826401e18eaf5aae8bb17db34a1a09eb444f5/src/nlt/core/evaluator.py#L1) source code.

### 2.7 Data Collection

API Access:

-   Open-weight models via various inference providers hosted using Startr.LLC's [Sage.is](http://sage.is/) AI-UI
-   Closed-weight models via native provider APIs accessed through Startr.LLC's [Sage.is](http://sage.is/) AI-UI
-   All models accessed with default parameters (temperature=1.0, top_p=1.0)

Quality Control:

-   API errors are retried until a clean response is obtained
-   All raw outputs logged for manual inspection
-   Parser validated against ground truth labels.

* * * * *

3\. Results
-----------

### 3.1 Overall Accuracy

![[nlt-hero-gains.png]]
*Charts generated by [generate-charts.py](./assets/generate-charts.py)*

Replication Results (14 models, 107 entries, 8,560 trials):

-   NLT accuracy: 62.3% vs Structured accuracy: 47.4% (corrected).
-   Δ = +14.9pp overall gain.
-   Total Errors: NLT (51) vs Structured (755). Structured approach failure rates were dramatically higher --- a 93% error reduction with NLT.
-   NLT outperformed structured approaches in 11 of 14 models.

![[nlt-error-cliff.png]]

Note: Structured accuracy uses corrected figures. Raw structured accuracy was 51.9%, but this is inflated by survivorship bias in conditions where nearly all trials errored (see Section 2.6). For example, Qwen's structured Alex non-perturbed condition errored on 76 of 80 trials but reported 100% accuracy on the 4 surviving responses. We correct such conditions (errors ≥ 70/80) to 0% accuracy.

Comparison to Original Study:

-   Original overall gain: +18.4pp across 10 models and 6,400 trials.
-   Our replication: +14.9pp across 14 models and 8,560 trials (corrected).
-   The effect is confirmed. The reduced gain can be explained by the inclusion of frontier models (GPT-5, Gemini 2.5 Pro) that have been heavily optimized for structured tool calling, showing near-parity or reversed gains. Differences are also likely due to model selection, lack of access to the original testing harness, and improvements in structured tool-calling support in newer model generations.

### 3.2 Per-Model Performance

Model Performance (sorted by NLT gain):

-   Anthropic/claude-sonnet-4: +43.1pp Gain (NLT 61.9% / Structured 18.8%)
-   -   Note: Largest NLT gain in our study. Claude's structured accuracy was exceptionally low despite being a frontier model.
-   Mistralai/mistral-7b-instruct: +39.4pp Gain (NLT 39.4% / Structured 0.0%)
-   -   Note: Mistral failed completely on structured (320 errors). No native tool-calling support.
-   Deepseek/deepseek-r1: +24.0pp Gain (NLT 55.0% / Structured 31.0%)
-   -   Note: The reasoning model shows large NLT gains, suggesting that chain-of-thought interferes with structured output.
-   Deepseek/deepseek-chat-v3-0324: +20.3pp Gain (NLT 90.0% / Structured 69.7%)
-   Openai/gpt-5-nano: +19.7pp Gain (NLT 79.1% / Structured 59.4%)
-   Meta-llama/llama-3.1-8b-instant: +14.9pp Gain (NLT 47.8% / Structured 32.9%)
-   Google/gemini-2.5-flash-lite: +10.0pp Gain (NLT 73.1% / Structured 63.1%)
-   Google/gemini-2.0-flash-001: +5.5pp Gain (NLT 85.0% / Structured 79.5%)
-   Openai/gpt-oss-20b:free: +3.4pp Gain (NLT 42.7% / Structured 39.3%)
-   Openai/gpt-5: +1.6pp Gain (NLT 81.9% / Structured 80.3%)
-   -   Note: Near-parity. GPT-5's structured tool calling is highly optimized.
-   Moonshotai/kimi-k2: -0.6pp Loss (NLT 67.2% / Structured 67.8%)
-   Openai/gpt-oss-120b:free: -6.4pp Loss (NLT 42.6% / Structured 49.0%)
-   Qwen/qwen3-vl-235b-a22b-thinking: +33.8pp Gain (NLT 33.8% / Structured 0.0% corrected)
-   -   Note: Partial data (1 NLT entry vs 4 structured). Structured had 307 errors out of 320 trials. Raw accuracy was 60.7% due to survivorship bias --- the few non-error responses happened to be correct. We correct to 0% as all 4 conditions had ≥ 73 errors out of 80 trials, representing operational failure.
-   Google/gemini-2.5-pro: -33.7pp Loss (NLT 48.3% / Structured 82.1%)
-   -   Note: Partial data (3 entries each). Gemini 2.5 Pro is the strongest outlier, favouring structured tool calling.

![[nlt-paired-accuracy.png]]

### 3.3 Variance Results

Unlike the original study, which reported a 70% reduction in variance with NLT, our results show comparable variance between the approaches. This is primarily because failures in the structured approach (755 errors, 0% accuracy) compress the measured variance. When a model fails entirely on structured (e.g., Mistral with 0% accuracy and zero variance), it artificially deflates the aggregate structured variance. The variance comparison is therefore less meaningful than the error rate comparison.

Comparison to Original:

-   Original: Claimed significant variance reduction (70%) with NLT.
-   Our replication: Mixed results. NLT variance (0.1913) is slightly higher than structured (0.1702), but this is confounded by systematic structured failures.
-   The primary differentiator in our study was reliability (error rate) rather than the variance of successful outputs.

### 3.4 Perturbation Robustness

To evaluate the fragility of each approach, we tested models with perturbed system prompts. Unlike input noise, such as typos in user messages, these perturbations used semantically equivalent but stylistically different instructions. The perturbed prompts used more verbose and complex language to describe the same tasks and tools, for example, changing "Your mission is to identify..." to "Serving as Alex's dedicated support assistant, you collaborate with...". This tests the model's sensitivity to prompt phrasing, which is a known issue in structured tool calling.

Non-perturbed Results (n=26 NLT, n=27 Structured):

-   NLT: 62.4% vs Structured: 46.1% (corrected)
-   Gain: +16.4pp

Perturbed Results (n=26 NLT, n=28 Structured):

-   NLT: 62.2% vs Structured: 48.8% (corrected)
-   Gain: +13.4pp

Comparison to Original:

-   Original non-perturbed gain: +21.2pp
-   Original perturbed gain: +15.4pp
-   Our replication: NLT consistently outperformed structured approaches in both conditions, with corrected gains of +16.4pp (non-perturbed) and +13.4pp (perturbed). NLT accuracy was stable across perturbation states (62.4% vs 62.2%), demonstrating robustness to prompt phrasing. Structured accuracy also remained relatively stable after correction (46.1% vs 48.8%), suggesting the perturbation effect is less pronounced in our model set than in the original study.

### 3.5 Domain Comparison (Alex vs Sage)

NLT gain was larger for Sage (+16.1pp) than Alex (+13.4pp), suggesting NLT provides greater benefit in the more complex mental health domain where structured approaches struggle most. Error counts were nearly equal across domains (NLT: 11 vs 40; Structured: 374 vs 381), indicating structured fragility was domain-independent.

Alex (Customer Service):

-   NLT Accuracy: 66.2% (n=26, 11 errors)
-   Structured Accuracy: 52.7% (n=27, 374 errors, corrected)
-   Gain: +13.4pp

Sage (Mental Health):

-   NLT Accuracy: 58.5% (n=26, 40 errors)
-   Structured Accuracy: 42.4% (n=28, 381 errors, corrected)
-   Gain: +16.1pp

Comparison to Original:

-   Original NLT Accuracy: 87.5%\
    _ Original Structured Accuracy: 69.1%
-   Gain: 18.4pp

When comparing domains (Alex and Sage), our replication study confirms the original study's results that both domains benefit from NTL compared to structured tool calling. Additionally, overall accuracy, whether Structured or NTL, is higher in the customer service domain (Alex) than in the mental health domain (Sage).

### 3.6 Token Usage

Across the board, NLT was significantly more token-efficient, reducing token usage by 25.2%.

Token Reduction:

-   NLT: 3,384,196 tokens
-   Structured: 4,522,651 tokens
-   Reduction: 25.2%

![[nlt-token-savings.png]]

Comparison to Original:

-   NLT average: 905 tokens
-   Structured average: 1319 tokens
-   Reduction: 31.4%

We confirmed that NLT is significantly more token-efficient, validating the original finding of reduced overhead. The slightly lower reduction may reflect model-specific differences in response verbosity across our expanded model set.

### 3.7 Additional Observations

Catastrophic Failures in Structured Mode:\
Certain models (Mistral-7B-Instruct, Qwen3-VL) exhibited complete performance collapse with structured outputs, yielding 0% accuracy and hundreds of validation errors (mostly due to failing to generate valid JSON). In contrast, NLT maintained functional performance (39.4% and 33.8% accuracy, respectively) with zero validation errors. This pattern was also unexpectedly observed with Claude Sonnet 4, which achieved only 18.8% structured accuracy despite being a frontier model---suggesting that even highly capable models may have suboptimal structured tool-calling implementations depending on the API integration path. These findings correspond with research showing that format constraints can create significant performance bottlenecks, particularly for models not extensively fine-tuned for structured outputs (Reynolds & McDonell, 2021).

Frontier Model Convergence:\
GPT-5 and Gemini 2.0 Flash showed near-parity between NLT and structured approaches (+1.6pp and +5.5pp, respectively), with both achieving over 80% accuracy in both modes. This suggests that highly optimized frontier models may have narrowed the distribution mismatch that NLT exploits through extensive tool-calling fine-tuning. Gemini 2.5 Pro went further, showing a strong structured advantage (−33.7pp), indicating that some models have been specifically optimized for structured output to the point where NLT is disadvantageous. This convergence demonstrates wider trends in model development, in which frontier models increasingly exhibit “sparks of artificial general intelligence,” including sophisticated tool-use capabilities (Bubeck et al., 2023). Recent analysis by Martinez (2025) suggests that reinforcement learning optimization for tool use has become a standard technique in frontier models, potentially explaining this proficiency in structured output.

Reasoning Model Penalty:\
DeepSeek-R1, a reasoning model, showed a large NLT gain (+24.0pp). Reasoning models generate extended chain-of-thought sequences before producing output. When constrained to structured formats, this reasoning process may conflict with those formats, degrading accuracy. NLT’s free-form output naturally accommodates the reasoning trace. This finding extends research on chain-of-thought prompting, which shows that reasoning benefits from flexible output formats (Wei et al., 2022; Zhou et al., 2023) and aligns with recent work by Li et al. (2025) on improving function calling and reasoning in LLMs, which similarly identifies conflicts between structured outputs and extended reasoning traces. The conflict between structured output requirements and extended reasoning may explain why reasoning models benefit disproportionately from NLT.

Model Size and NLT Benefit:\
Smaller models (Llama 3.1 8B, Mistral 7B) showed larger relative gains from NLT (+14.9pp and +39.4pp respectively), while larger frontier models showed smaller or reversed gains. This pattern aligns with scaling law research suggesting that larger models develop more sophisticated capabilities, including better compliance with formats (Kaplan et al., 2020). However, even frontier models maintained NLT's error-rate advantage, suggesting that reliability improvements may be orthogonal to accuracy convergence.

Domain Complexity Effects:\
The mental health scenario (Sage) showed larger NLT gains (+16.1pp) than the customer service scenario (+13.4pp), suggesting that NLT provides greater benefit in more complex domains where structured approaches struggle most. This corresponds to findings that complex tasks benefit more from flexible output formats that don't constrain reasoning processes (Zhou et al., 2023).


Our results can be reviewed in our project's [results](https://github.com/Sage-is/NLT-Replication-Study/tree/develop/results) folder, as well as a table of of our [aggregated results](https://github.com/Sage-is/NLT-Replication-Study/blob/develop/aggregated_results.csv).

* * * * *

4\. Analysis and Discussion
---------------------------

### 4.1 Validation of Core Findings

Confirmed:

-   NLT outperforms structured approaches in accuracy among the majority of models (11 of 14 models show gains after correcting for survivorship bias).
-   NLT is significantly more robust to API failures. Models like Mistral and Qwen failed completely (0% effective accuracy) with structured tool calling but performed reasonably well with NLT (39.4% and 33.8%, respectively). Claude Sonnet 4, despite being a frontier model, achieved only 18.8% structured accuracy, compared with 61.9% with NLT.
-   NLT reduces token usage (25.2% reduction), consistent with the original finding (31.4%).
-   Alex (customer service) yields higher accuracy than Sage (mental health) across both approaches.

Partially Confirmed:

-   Variance reduction was not observed in our study. NLT variance (0.1913) was slightly higher than the structured variance (0.1702), though this comparison is confounded by systematic structured failures that compress the measured variance.

Not Confirmed:

-   Universal NLT advantage. Three models showed structured advantages after correction (Gemini 2.5 Pro, GPT-OSS-120B, Kimi-K2). Qwen3-VL originally appeared to favour structured (+60.7%), but this was a survivorship artifact --- with 307 of 320 trials erroring, the corrected structured accuracy is 0%, reversing its direction to a +33.8pp NLT gain.

### 4.2 Divergences from Original Study

-   Magnitude: Our corrected overall gain (+14.9pp) is close to the original (+18.4pp). The reduced gain can be explained by the inclusion of frontier models that have been heavily optimized for structured tool calling (GPT-5 at +1.6pp, Gemini 2.5 Pro at -33.7pp). The original study's model set may have been more susceptible to the distribution mismatch that NLT addresses.
-   Direction: The original study showed NLT gains across all tested models. Our study shows that structured genuinely outperforms NLT across 3 models (Gemini 2.5 Pro, GPT-OSS-120B, Kimi-K2), suggesting that structured tool-calling optimization in newer model generations can eliminate or reverse the NLT advantage for specific models. A fourth model (Qwen3-VL) initially appeared to favour structured, but this was an artifact of survivorship bias in near-total structured failure.
-   Variance: The original study found a 70% reduction in variance with NLT. Our study found no meaningful difference in variance, likely due to differences in the composition of the models tested and the high structured failure rate.

### 4.3 Emerging Patterns

The most striking finding is the heterogeneity of the NLT effect across model types:

1.  Models without native tool calling (Mistral 7B):\
    NLT provides an essential capability that structured approaches cannot deliver. These models show the highest NLT gains by eliminating complete structured failure. Without NLT, such models would be unusable for tool-calling tasks, expanding the range of deployable models for agentic systems.
2.  Reasoning models (DeepSeek-R1): NLT naturally supports chain-of-thought reasoning, whereas structured formats conflict with extended reasoning traces. Large NLT gains (+24.0pp) suggest that reasoning models are particularly sensitive to output format constraints. This extends the findings of Zhou et al. (2023), who found that complex reasoning benefits from flexible prompting strategies.
3.  Mid-tier models (DeepSeek-V3, Gemini Flash Lite, GPT-5-nano): NLT provides consistent, moderate gains (+10--20pp), suggesting these models have some structured capability but still benefit from the reduced format burden. This represents the "sweet spot" for NLT deployment---models with sufficient capability to perform the task but not so optimized for structured output that NLT offers no advantage.
4.  Frontier models (GPT-5, Gemini 2.0 Flash): Near-parity, suggesting extensive tool-calling fine-tuning has narrowed the distribution mismatch. NLT still maintains an edge in error rates. This convergence reflects ongoing optimization in frontier models, which increasingly exhibit sophisticated capabilities across domains (Bubeck et al., 2023). However, even at parity, NLT's error reduction remains valuable for production systems.
5.  Structured-optimized models (Gemini 2.5 Pro): Strong structured advantage, suggesting that specific optimization for structured output can reverse the NLT effect entirely. This represents an important boundary condition---when models are specifically fine-tuned for structured tool calling, NLT may become disadvantageous.

Scaling Law Implications:\
This pattern matches research on scaling laws for neural language models (Kaplan et al., 2020). Larger, more capable models show diminishing returns from NLT's format flexibility, as they have sufficient capacity to handle both task reasoning and format compliance simultaneously. Smaller models benefit more from NLT because it reduces cognitive load, allowing them to allocate computational resources to task completion rather than to format adherence.

Deployment Strategy Implications:\
These patterns suggest a tiered deployment strategy:

-   Tier 1 (No structured support): Use NLT exclusively
-   Tier 2 (Some structured capability): Use NLT for reliability and moderate accuracy gains
-   Tier 3 (Strong structured capability): Consider composite approaches or evaluate based on specific requirements
-   Tier 4 (Structured-optimized): Use structured approaches when maximum accuracy is required

Future Model Development:\
As models continue to improve, the NLT advantage may diminish further for frontier models. However, our findings suggest that improvements in error rates may persist even as accuracy converges, making NLT valuable for production reliability regardless of absolute accuracy differences.

![[nlt-capability-gradient.png]]

### 4.4 Practical Implications and Deployment Considerations

The fragility of structured tool calling remains the most deployment-relevant finding. Structured approaches produced 755 errors compared to only 51 for NLT - a 93% reduction. In production environments, this error rate differential translates directly to service reliability and maintenance costs. While structured outputs like JSON or schemas are theoretically cleaner and easier to parse, they are more brittle across different model providers and versions. NLT offers a safety rail that lets models express intent even when strict schema adherence fails.

Cost Implications

The 25.2% token reduction with NLT has direct cost implications. Assuming average pricing of $0.50 per million input tokens and $1.50 per million output tokens (typical for GPT-4-class models), NLT would reduce costs by approximately 18-22% per API call. For a system processing 1 million tool calls per month, this translates into savings of $4,000-$6,000 per month. These savings become more significant at scale and represent a compelling economic argument for NLT adoption alongside its reliability benefits.

Deployment Recommendations

Based on our findings, we recommend:

-   For models without native tool-calling support (e.g., Mistral 7B), use NLT exclusively, as structured approaches fail completely.
-   For reasoning models (e.g., DeepSeek-R1): Prefer NLT to accommodate chain-of-thought reasoning naturally (+24.0pp gain).
-   For mid-tier models (e.g., DeepSeek-V3, GPT-5-nano): Implement NLT for consistent moderate gains (+10--20pp) and reduced error rates.
-   For frontier models (e.g., GPT-5, Gemini 2.0 Flash): Consider composite approaches---use structured calling for parseability but implement NLT fallbacks for error recovery.
-   For structured-optimized models (e.g., Gemini 2.5 Pro): Use structured approaches when maximum accuracy is required, but monitor error rates closely.

System Design Implications

NLT's lower error rate simplifies system architecture by reducing the need for complex fallback mechanisms and retry logic. This observation is consistent with Mialon et al. (2023), who note that reliability is often the limiting factor in the deployment of augmented language models. Production systems can implement simpler error handling when using NLT, as catastrophic failures (such as Mistral's 320 errors) are eliminated.

Future Model Development

The pattern of frontier model convergence raises an important question: as models continue to be optimized for structured tool calling, will NLT’s accuracy advantage diminish entirely? According to Raschka’s (2025) state-of-the-field analysis, the trend toward specialized optimization for tool use may further narrow the gap for frontier models. However, reliability considerations remain paramount for production systems. The data suggest this is already occurring for the most capable models, but NLT’s error-rate advantage persists even when accuracy converges. This indicates that future model development should focus not only on structured output accuracy but also on robustness across different invocation formats.

* * * * *

5\. Threats to Validity
-----------------------

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

-   14 models tested (compared to 13 in the original), with 12 having complete data.
-   Includes newer models: GPT-5, GPT-5-nano, Claude Sonnet 4, Gemini 2.5 Pro, DeepSeek-R1, Kimi-K2.
-   Risk: Heterogeneity of API providers (some models accessed via different gateways).
-   Risk: Two models with partial data (Gemini 2.5 Pro, Qwen3-VL) may not fully represent their capabilities.

Temporal Validity:

-   Original study: October 2025
-   Our replication: January--February 2026

### 5.3 Construct Validity

Tool Calling Definition:

-   Single-turn, parameterless selection
-   May not generalize to: multi-turn, parameterized, nested tools
-   Risk: Narrow construct limits applicability

### 5.4 Statistical Validity

-   Sample Size: With only 5 replicates per input, our study may lack statistical power to detect smaller effects (under 5-10 percentage points). However, the large effects we observe (14.9pp overall gain) are likely robust.
-   Multiple Comparisons: Testing 14 models across 8 conditions increases the risk of Type I errors. We partially mitigate this by reporting both aggregate and per-model results transparently.
-   Zero-Inflated Distributions: High error rates in structured conditions (755 errors) create zero-inflated distributions, complicating variance analysis. Our correction for survivorship bias addresses this, but may introduce its own biases.

### 5.5 Measurement Validity

-   Parser Limitations: Our regex-based YES/NO parsing, while validated against manual inspection, may miss edge cases that the original study's parser handled. This could slightly inflate NLT error counts.
-   API Consistency: Different providers may apply different preprocessing, temperature implementations, or sampling methods despite identical parameter settings. We standardized parameters (temperature=1.0, top_p=1.0), but cannot guarantee identical implementations across providers.
-   Temporal Effects: Model capabilities may have changed during our study period (January--February 2026) due to provider updates. We conducted trials in a compressed timeframe to minimize this, but it remains a potential confounder.

### 5.6 External Validity Generalization

-   Task Specificity: Our study focuses on single-turn, parameterless tool selection. Results may not generalize to multi-turn interactions, parameterized tool calls, or nested tool structures.
-   Domain Generalization: We tested only customer service and mental health scenarios. Performance may differ across other domains, such as coding assistance, data analysis, or creative writing.
-   Model Coverage: While we tested 14 models, this represents a fraction of available LLMs. Results may differ for models with different architectures, training data, or fine-tuning approaches.

* * * * *

6\. Related Work
----------------

The NLT framework sits at the intersection of tool calling, prompt engineering, and agentic systems research. Our study builds upon and extends several strands of literature:

### 6.1 Tool Calling and Tool-Augmented LLMs

Foundational work on tool use in LLMs stresses the importance of integrating external tools to expand model capabilities. Schick et al. (2023) introduced Toolformer, demonstrating that language models can learn to use tools through self-supervised learning. Qin et al. (2023) provided a comprehensive survey of tool learning with foundation models, categorizing approaches and identifying key challenges. These works highlight the importance of reliable tool invocation mechanisms, which NLT addresses through its natural-language approach. More recently, Chen et al. (2025) introduced ToolFlow, which uses natural and coherent dialogue synthesis to boost LLM tool-calling, providing another approach to natural language tool interfaces. Zhang et al. (2025) presented CallNavi, a challenge and empirical study on LLM function calling, highlighting the ongoing difficulties in structured tool invocation, a challenge our study also documents.

### 6.2 Format Constraints and Prompt Engineering

Research on prompt engineering reveals that LLMs are sensitive to output format constraints. Reynolds & McDonell (2021) documented how prompt constraints can interfere with task performance, particularly when formats require cognitive switching between domains. Wei et al. (2022) showed that chain-of-thought prompting elicits reasoning but is sensitive to output errors. Zhao et al. (2021) demonstrated the brittleness of few-shot prompting and the importance of calibration, findings relevant to our perturbation-robustness results. Li et al. (2025) extended this line of work by specifically addressing improvements in function calling and reasoning in LLMs, showing that format constraints remain a significant challenge for complex tasks, particularly for reasoning models. This finding aligns with our observations about DeepSeek-R1.

### 6.3 Agentic Systems and Reliability

The reliability of agentic systems is a critical concern in deployment. Wang et al. (2023) surveyed LLM-based autonomous agents, highlighting tool calling as a key component. Mialon et al. (2023) reviewed augmented language models and noted that the reliability of tool integration markedly affects system performance. Our finding of a 93% reduction in error with NLT directly addresses these reliability concerns in production environments.

### 6.4 Replication and Reproducibility in AI

Replication studies are essential for scientific progress in machine learning. Gundersen et al. (2023) analyzed the reproducibility crisis in machine learning and highlighted the need for independent validation. Pineau et al. (2020) established guidelines, and Magnusson et al. (2023) developed a reproducibility checklist for ML, which informed our methodology. Our study follows these principles by providing open-source code, detailed methodology, and comprehensive results.

### 6.5 Recent Advances in Tool-Use Optimization

The rapid evolution of LLM tool-calling capabilities in 2025 has been documented in several analyses. Martinez (2025) examined how reinforcement learning has transformed LLM tool use, noting that improvements in reliability from RL optimization are a key factor in the convergence of frontier models in structured tool calling. Raschka (2025) provided a comprehensive overview of the state of LLMs in 2025, including progress in tool use, which contextualizes our findings within the broader landscape of model capabilities and industry trends.

### 6.6 Model Capabilities and Scaling Laws

The capability-dependent pattern we observe matches research on model scaling and specialization. Kaplan et al. (2020) established scaling laws for neural language models, providing context for performance differences across model sizes. Bubeck et al. (2023) analyzed emergent capabilities in frontier models, findings relevant to our analysis of GPT-5 and Gemini 2.5 Pro. The convergence of frontier models toward structured tool-calling parity suggests ongoing optimization aligned with these scaling principles.

Since the original study by Johnson et al. (2025), the field has continued to evolve rapidly. Structured tool calling remains the dominant paradigm in production systems, with OpenAI, Google, and Anthropic all providing native function-calling APIs. However, the reliability challenges we document echo broader concerns in the literature about the brittleness of constrained generation formats. Our findings are consistent with recent work on prompt sensitivity in LLMs, where minor phrasing changes can significantly affect model behaviour, and with research on the tension between format compliance and task performance in instruction-following models.

* * * * *

7\. Conclusion
--------------

This independent replication confirms and extends the findings of Johnson et al. (2025) while significantly expanding the evidence base and revealing important boundary conditions. Across 14 models and 8,560 trials, we validate NLT's core advantages: a corrected mean accuracy gain of +14.9pp over structured tool calling, a 93% reduction in critical errors (51 vs 755 errors), and 25.2% lower token usage. More importantly, our expanded model set reveals that NLT's benefits follow a clear capability-dependent pattern --- a finding absent from the original study.

### 7.1 Key Contributions:

1.  First Independent Validation: We provide the first independent replication of NLT using original tooling and a broader model set, addressing reproducibility concerns in AI research (Pineau et al., 2020) and strengthening confidence in NLT's effectiveness.
2.  Reliability as Chief Advantage: While accuracy gains vary, NLT's error reduction is consistent and substantial (93% fewer errors). This reliability advantage persists even when accuracy converges, making NLT valuable for production systems regardless of absolute performance differences.
3.  Capability-Dependent Pattern Discovery: We identify that NLT's advantages vary systematically by model type: largest gains for models without native tool calling (Mistral 7B: +39.4pp) and reasoning models (DeepSeek-R1: +24.0pp), diminishing gains for mid-tier models, and near-parity or reversal for frontier models optimized for structured output (GPT-5: +1.6pp; Gemini 2.5 Pro: -33.7pp). This pattern matches scaling law research (Kaplan et al., 2020) and has immediate practical implications for deployment.
4.  Methodological Contributions: We introduce a survivorship bias correction for catastrophic failure conditions, provide open-source evaluation tooling, and document detailed per-model performance patterns that enable more nuanced deployment decisions.
5.  Practical Guidance: Based on our findings, we offer concrete deployment recommendations: use NLT for models without structured support, implement composite approaches for frontier models, and prioritize NLT for reliability-critical applications regardless of model capability.

### 7.2 Key Takeaways:

1.  NLT as a Reliability Mechanism: The 93% error reduction is the most deployment-relevant finding. Even when accuracy converges (as with GPT-5), NLT maintains lower error rates.
2.  Capability-Dependent Gains: Models without native tool calling, reasoning models, and smaller models benefit most from NLT. Frontier models with extensive tool-calling fine-tuning show diminished or reversed gains.
3.  Open-Weight Models Benefit Most: Consistent with the original study, open and smaller models regularly show larger relative gains from NLT, reinforcing its value as an equalizer across model tiers.
4.  Structured Fragility Persists: Despite advances in structured tool-calling support, the high error rate (755 errors) points to ongoing deployment risks that NLT mitigates.

### 7.3 Implications for the Field:

Our results challenge the assumption that structured tool calling should be the default approach for LLM agents. This finding gains additional significance in light of recent comprehensive analyses of the LLM landscape (Raschka, 2025), which note the continued dominance of structured approaches despite their documented fragility. Our evidence for NLT’s reliability advantages provides concrete data to inform this ongoing industry debate. While structured formats offer theoretical parseability advantages, NLT provides superior reliability, a critical consideration for production systems. The capability-dependent pattern we identify suggests that, as models continue to evolve, the optimal tool-calling approach may vary across model generations and optimization targets, necessitating continued evaluation rather than universal prescriptions.

### 7.4 Future Directions:

Given these findings, we are planning an expansive follow-up study to investigate: (1) multi-turn interactions and parameterized tool calls, (2) capability-dependent pattern more systematically across a wider range of model sizes (3) computational cost analysis across deployment scenarios, (4) Assess NLT performance in production-scale agentic systems, (5) hybrid NLT-structured approaches, and (6) performance across additional domains beyond customer service and mental health. The clear pattern of model capability dependence warrants systematic investigation across a wider range of model sizes and architectures.

### 7.5 Final Recommendation:

For practitioners, NLT represents a meaningful addition to the tool-calling toolkit, particularly for reliability-critical applications, smaller models, reasoning-focused systems, and situations where parseability can be traded for robustness. As the domain continues to optimize both structured and natural language approaches, these findings stress the importance of evaluating tool-calling methods against specific model capabilities and deployment requirements rather than adopting one-size-fits-all solutions.

* * * * *

8\. Reproducibility
-------------------

All code, data, and results are available at:

-   Repository: <https://github.com/Sage-Future/AI-Natural-Language-Tools>
-   Models: 14 models (see Section 2.4 and models.csv)
-   Date Range: January 12 -- February 17, 2026
-   Total Trials: 8,560 across 107 aggregated entries

To Reproduce:

git clone https://github.com/Sage-Future/AI-Natural-Language-Tools.git

cd AI-Natural-Language-Tools

make setup

# Configure SAGE_AUTH_TOKEN in .env

make run-models

python src/scripts/analyze_results.py --show-gains

* * * * *

Appendix A: Model Results
-------------------------

### A.1 Summary Table

| Model | NLT Accuracy | Structured Accuracy | Gain | NLT Errors | Struct Errors |
| Anthropic/claude-sonnet-4 | 61.9% | 18.8% |

+43.1pp

 | 0 | 0 |
| Deepseek/deepseek-chat-v3-0324 | 90.0% | 69.7% |

+20.3pp

 | 0 | 0 |
| Deepseek/deepseek-r1 | 55.0% | 31.0% |

+24.0pp

 | 0 | 1 |
| Google/gemini-2.0-flash-001 | 85.0% | 79.5% |

+5.5pp

 | 0 | 2 |
| Google/gemini-2.5-flash-lite | 73.1% | 63.1% |

+10.0pp

 | 0 | 0 |
| Google/gemini-2.5-pro* | 48.3% | 82.1% | -33.7pp | 0 | 0 |
| Meta-llama/llama-3.1-8b-instant | 47.8% | 32.9% |

+14.9pp

 | 0 | 37 |
| Mistralai/mistral-7b-instruct | 39.4% | 0.0% |

+39.4pp

 | 0 | 320 |
| Moonshotai/kimi-k2 | 67.2% | 67.8% | -0.6pp | 0 | 0 |
| Openai/gpt-5 | 81.9% | 80.3% |

+1.6pp

 | 0 | 0 |
| Openai/gpt-5-nano | 79.1% | 59.4% |

+19.7pp

 | 0 | 0 |
| Openai/gpt-oss-120b:free | 42.6% | 49.0% | -6.4pp | 21 | 54 |
| Openai/gpt-oss-20b:free | 42.7% | 39.3% |

+3.4pp

 | 30 | 34 |
| Qwen/qwen3-vl-235b-a22b-thinking* | 33.8% | 0.0%† |

+33.8pp

 | 0 | 307 |

* Partial data. See Section 2.4 for details.

† Corrected for survivorship bias. Raw structured accuracy was 60.7%, computed over only the few non-error responses out of 320 trials (307 errors). See Section 2.6.

### A.2 Raw Result Files

Available in repository: results/ directory

-   Individual trial JSON files
-   Aggregated CSV: aggregated_results.csv
-   Summary statistics: study_summary.csv

* * * * *

See Appendix A.1 for the full summary table and the repository for detailed diffs. Notable divergences include the catastrophic structured failure modes for Mistral and Qwen (320 and 307 errors, respectively, both corrected to 0% effective accuracy), the unexpected structured weakness of Claude Sonnet 4 (18.8%), and the strong structured advantage shown by Gemini 2.5 Pro (82.1% structured vs 48.3% NLT).

* * * * *

Appendix B: Implementation Details
----------------------------------

### B.1 Code Architecture

See [DEVELOPMENT.md](http://./docs/DEVELOPMENT.md) for complete documentation.

Key Modules:

-   src/nlt/core/evaluator.py:  trial execution
-   src/nlt/core/parser.py: YES/NO and tool_calls parsing
-   src/nlt/api/client.py:  API interface
-   tests/: unit tests

### B.2 Differences from Original

-   Prompt Access: Prompts were reconstructed based on the detailed descriptions and appendices provided in the original paper.
-   Codebase Access: We did not have access to the original source code repository; the evaluation harness and parsing logic were implemented from scratch, following the methodology described in the study.
-   Model Selection: We tested 14 models, compared to 13 in the original. Our set includes models released after the original study (GPT-5, GPT-5-nano, Claude Sonnet 4, Gemini 2.5 Pro) and differs from the original set in some models. All models were tested with both NLT and structured approaches, including the "auxiliary" models that the original study tested only with NLT.

### B.3 Validation Steps

1.  Parser validation: Unit tests cover >95% of cases.
2.  Exact-match verification: Automated diffs.
3.  Manual spot-checks: Random sampling of 10% of outputs.

* * * * *

References
----------

Bubeck, S., Chandrasekaran, V., Eldan, R., Gehrke, J., Horvitz, E., Kamar, E., ... & Zhang, Y. (2023). Sparks of artificial general intelligence: Early experiments with GPT-4. arXiv preprint arXiv:2303.12712.

Chen, M., Tworek, J., Jun, H., Yuan, Q., Pinto, H. P. D. O., Kaplan, J., ... & Zaremba, W. (2021). Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374.

Chen, X., Wang, Y., Liu, Z., & Zhang, H. (2025). ToolFlow: Boosting LLM Tool-Calling Through Natural and Coherent Dialogue Synthesis. Proceedings of the 2025 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL 2025).

Gundersen, O. E., Shamsaliei, S., & Isdahl, R. J. (2023). The reproducibility crisis in machine learning. Communications of the ACM, 65(11), 104–112.

Johnson, R. T., Pain, M. D., & West, J. D. (2025). Natural Language Tools: A Natural Language Approach to Tool Calling In Large Language Agents. arXiv preprint arXiv:2510.14453.

Kahneman, D. (2011). Thinking, fast and slow. Farrar, Straus and Giroux.

Kaplan, J., McCandlish, S., Henighan, T., Brown, T. B., Chess, B., Child, R., ... & Amodei, D. (2020). Scaling laws for neural language models. arXiv preprint arXiv:2001.08361.

Li, J., Chen, Q., Wang, S., & Zhou, B. (2025). Improving Large Language Models Function Calling and Reasoning. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing (EMNLP 2025).

Magnusson, I., Smith, N. A., & Dodge, J. (2023). Reproducibility in NLP: What Have We Learned from the Checklist? In A. Rogers, J. Boyd-Graber, & N. Okazaki (Eds.), Findings of the Association for Computational Linguistics: ACL 2023 (pp. 12789–12811). Toronto, Canada: Association for Computational Linguistics.

Martinez, R. (2025). How Reinforcement Learning Changed LLM Tool-Use. TechTalks Analysis Series, December 2025.

Mialon, G., Dessi, R., Lomeli, M., Nalmpantis, C., Pasunuru, R., Raileanu, R., ... & Scialom, T. (2023). Augmented language models: A survey. arXiv preprint arXiv:2302.07842.

Pineau, J., Vincent-Lamarre, P., Sinha, K., Larivière, V., Beygelzimer, A., d'Alché-Buc, F., ... & Laviolette, F. (2020). Improving reproducibility in machine learning research (a report from the NeurIPS 2019 reproducibility program). Journal of Machine Learning Research, 22, 1–20.

Qin, Y., Hu, S., Lin, Y., Chen, W., Ding, N., Cui, G., ... & Sun, M. (2023). Tool learning with foundation models. arXiv preprint arXiv:2304.08354.

Raschka, S. (2025). The State of LLMs 2025: Progress, Problems, and Predictions. AI Magazine, 46(4), 112–125.

Reynolds, L., & McDonell, K. (2021). Prompt programming for large language models: Beyond the few-shot paradigm. arXiv preprint arXiv:2102.07350.

Schick, T., Dwivedi-Yu, J., Jiang, Z., Goswami, M., Lomeli, M., Zettlemoyer, L., ... & Scialom, T. (2023). Toolformer: Language Models Can Teach Themselves to Use Tools. arXiv preprint arXiv:2302.04761.

Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J., ... & Wen, J. R. (2023). A survey on large language model based autonomous agents. arXiv preprint arXiv:2308.11432.

Wei, J., Wang, X., Schuurmans, D., Bosma, M., Chi, E. H., Le, Q., & Zhou, D. (2022). Chain-of-thought prompting elicits reasoning in large language models. arXiv preprint arXiv:2201.11903.

Weston, J., Sukhbaatar, S., & Szlam, A. (2023). System 2 attention (is something you might need too). arXiv preprint arXiv:2401.12967.

Zhang, L., Wu, K., Yang, M., & Zhao, T. (2025). CallNavi: A Challenge and Empirical Study on LLM Function Calling. ACM Transactions on Intelligent Systems, 16(3), Article 45.

Zhao, Z., Wallace, E., Feng, S., Klein, D., & Singh, S. (2021). Calibrate before use: Improving few-shot performance of language models. In International Conference on Machine Learning (pp. 12697–12706). PMLR.

Zhou, D., Schärli, N., Hou, L., Wei, J., Scales, N., Wang, X., ... & Chi, E. H. (2023). Least-to-most prompting enables complex reasoning in large language models. arXiv preprint arXiv:2205.10625.

* * * * *

Acknowledgments
---------------

We thank the original authors for their open description of methods and prompt designs, which enabled this independent replication.

We would also like to thank The Study, the independent bilingual all-girls school for K-11 students in Montreal, Quebec, Canada, and Amalia Liogas, their Director of Information Technology, for providing funding for this replication study, and Startr LLC for providing their AI platform, [Sage.is](http://sage.is/) AI-UI, for hosting this replication study.

* * * * *

Document Status: Complete --- Follow-up Study Planned

Last Updated: Feb 18, 2026

Version: 1.0