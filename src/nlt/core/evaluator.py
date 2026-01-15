from __future__ import annotations

import sys
import time
from collections.abc import Iterable

from nlt.api.client import SageClient
from nlt.core import parser
from nlt.core.types import Message, Scenario, TrialResult, Usage


def build_messages(system_prompt: str, user_text: str) -> list[Message]:
    return [
        Message(role="system", content=system_prompt.strip()),
        Message(role="user", content=user_text.strip()),
    ]


def run_single_trial(
    client: SageClient,
    scenario: Scenario,
    approach: str,
    perturbed: bool,
    input_text: str,
    expected_tools: Iterable[str],
    model: str | None,
    delay_seconds: float,
    verbose: bool = False,
) -> TrialResult:
    system_prompt = scenario.prompts[approach]["perturbed" if perturbed else "non_perturbed"]
    messages = build_messages(system_prompt=system_prompt, user_text=input_text)

    if verbose:
        print(f"[VERBOSE] Starting trial with model: {model or 'default'}", file=sys.stderr)
        print(f"[VERBOSE] Input text: {input_text[:100]}{'...' if len(input_text) > 100 else ''}", file=sys.stderr)

    # Structured approach always uses tool calling
    tools = scenario.tool_schemas if approach == "structured" else None

    try:
        if verbose:
            print(f"[VERBOSE] Making API call...", file=sys.stderr)
        response = client.chat_completion(messages=messages, model=model, tools=tools)
        raw_output = response.content
        if verbose:
            print(f"[VERBOSE] Got response: {len(raw_output)} characters", file=sys.stderr)
    except Exception as exc:  # pragma: no cover - network
        if verbose:
            print(f"[VERBOSE] API call failed: {exc}", file=sys.stderr)
        return TrialResult(
            scenario=scenario.name,
            approach=approach,
            perturbed=perturbed,
            model=model or client.default_model,
            input_id=-1,
            expected_tools=set(expected_tools),
            predicted_tools=set(),
            success=False,
            raw_output="",
            usage=Usage(),
            error=str(exc),
        )

    if delay_seconds:
        time.sleep(delay_seconds)

    if approach == "nlt":
        decisions = parser.parse_nlt_output(raw_output, scenario.tools)
        predicted = {name for name, value in decisions.items() if value}
    else:
        # Structured approach uses OpenAI-style tool calling only
        predicted = parser.parse_tool_calls(response.tool_calls, scenario.structured_function_map)

    expected = set(expected_tools)
    success = parser.exact_match(expected, predicted)

    return TrialResult(
        scenario=scenario.name,
        approach=approach,
        perturbed=perturbed,
        model=model or client.default_model,
        input_id=-1,
        expected_tools=expected,
        predicted_tools=predicted,
        success=success,
        raw_output=raw_output,
        usage=response.usage,
    )


def evaluate(
    client: SageClient,
    scenario: Scenario,
    approach: str,
    perturbed: bool,
    replicates: int,
    model: str | None = None,
    sample_limit: int | None = None,
    delay_seconds: float = 0.0,
    verbose: bool = False,
) -> list[TrialResult]:
    results: list[TrialResult] = []
    inputs = scenario.inputs[:sample_limit] if sample_limit else scenario.inputs
    
    if verbose:
        total_trials = len(inputs) * replicates
        print(f"[VERBOSE] Starting evaluation: {total_trials} total trials ({len(inputs)} inputs × {replicates} replicates)", file=sys.stderr)

    for i, scenario_input in enumerate(inputs, 1):
        if verbose:
            print(f"[VERBOSE] Processing input {i}/{len(inputs)}: {scenario_input.text[:50]}{'...' if len(scenario_input.text) > 50 else ''}", file=sys.stderr)
        
        for rep in range(replicates):
            if verbose:
                print(f"[VERBOSE] Replicate {rep + 1}/{replicates}", file=sys.stderr)
            
            trial = run_single_trial(
                client=client,
                scenario=scenario,
                approach=approach,
                perturbed=perturbed,
                input_text=scenario_input.text,
                expected_tools=scenario_input.expected_tools,
                model=model,
                delay_seconds=delay_seconds,                verbose=verbose,            )
            trial.input_id = scenario_input.id
            results.append(trial)

    return results


def summarize(results: list[TrialResult]) -> dict:
    success_flags = [r.success for r in results if r.error is None]
    summary = parser.accuracy_and_variance(success_flags)
    summary["total"] = len(results)
    summary["errors"] = sum(1 for r in results if r.error)
    return summary
