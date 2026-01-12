from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    role: str
    content: str


@dataclass
class FunctionDefinition:
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_wire(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


@dataclass
class Tool:
    type: str = "function"
    function: FunctionDefinition | None = None

    def to_wire(self) -> dict[str, Any]:
        result = {"type": self.type}
        if self.function:
            result["function"] = self.function.to_wire()
        return result


@dataclass
class ToolCall:
    id: str
    type: str
    function: dict[str, Any]


@dataclass
class ChatCompletionRequest:
    model: str
    messages: list[Message]
    stream: bool = False
    tools: list[Tool] | None = None
    tool_choice: str | None = None

    def to_wire(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "stream": self.stream,
            "messages": [message.__dict__ for message in self.messages],
        }
        if self.tools:
            payload["tools"] = [tool.to_wire() for tool in self.tools]
        if self.tool_choice:
            payload["tool_choice"] = self.tool_choice
        return payload


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
    tool_calls: list[ToolCall] = field(default_factory=list)


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
    tool_schemas: list[Tool] = field(default_factory=list)
