from __future__ import annotations

import re
from collections.abc import Iterable

from nlt.core.types import ToolCall

YES_NO_PATTERN = re.compile(r"\b(YES|NO)\b", re.IGNORECASE)


def parse_nlt_output(output: str, tool_names: Iterable[str]) -> dict[str, bool]:
    """Parse the NLT YES/NO grid for each tool name.

    The parser looks for lines containing the tool name and the last YES/NO token on that line.
    If a tool is missing, it defaults to False.
    """

    decisions: dict[str, bool] = dict.fromkeys(tool_names, False)
    lines = output.splitlines()

    for name in tool_names:
        pattern = re.compile(re.escape(name), re.IGNORECASE)
        for line in lines:
            if not pattern.search(line):
                continue
            yes_no = YES_NO_PATTERN.findall(line)
            if not yes_no:
                continue
            decisions[name] = yes_no[-1].upper() == "YES"
            break

    return decisions


def parse_tool_calls(tool_calls: list[ToolCall], function_names: dict[str, str]) -> set[str]:
    """Parse OpenAI-style tool_calls and map to tool names.

    Extracts function names from tool_calls and maps them to tool names.
    """

    predicted: set[str] = set()

    for tool_call in tool_calls:
        func_name = tool_call.function.get("name", "")
        if func_name in function_names:
            predicted.add(function_names[func_name])

    return predicted


def exact_match(expected: set[str], predicted: set[str]) -> bool:
    return expected == predicted


def accuracy_and_variance(results: list[bool]) -> dict[str, float]:
    if not results:
        return {"accuracy": 0.0, "variance": 0.0}

    n = len(results)
    mean = sum(1 for r in results if r) / n
    variance = sum((int(r) - mean) ** 2 for r in results) / n
    return {"accuracy": mean, "variance": variance}
