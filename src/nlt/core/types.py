from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    role: str
    content: str


@dataclass
class ChatCompletionRequest:
    model: str
    messages: list[Message]
    stream: bool = False

    def to_wire(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "stream": self.stream,
            "messages": [message.__dict__ for message in self.messages],
        }


@dataclass
class Usage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass
class ChatCompletionResponse:
    content: str
    raw: dict[str, Any]
    usage: Usage = field(default_factory=Usage)


@dataclass
class TrialResult:
    scenario: str
    approach: str
    perturbed: bool
    model: str
    input_id: int
    expected_tools: set[str]
    predicted_tools: set[str]
    success: bool
    raw_output: str
    usage: Usage = field(default_factory=Usage)
    error: str | None = None


@dataclass
class ScenarioInput:
    id: int
    text: str
    expected_tools: set[str]


@dataclass
class Scenario:
    name: str
    tools: list[str]
    prompts: dict[str, dict[str, str]]
    inputs: list[ScenarioInput]
    structured_function_map: dict[str, str]
