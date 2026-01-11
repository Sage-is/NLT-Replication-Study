from __future__ import annotations

import re
from collections.abc import Iterable

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


def parse_structured_calls(output: str, function_names: dict[str, str]) -> set[str]:
    """Parse function-name mentions and map them to tool names.

    We treat any occurrence of a function name (case-insensitive) as a tool selection.
    """

    predicted: set[str] = set()
    lowered = output.lower()

    for func_name, tool_name in function_names.items():
        if func_name.lower() in lowered:
            predicted.add(tool_name)

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
