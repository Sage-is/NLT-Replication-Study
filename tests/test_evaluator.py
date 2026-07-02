"""Unit tests for the NLT evaluator module.

These exercise the current evaluator API: trials run through a ``SageClient``
(mocked here) and return ``TrialResult`` dataclasses. See ``src/nlt/core``.
"""

from unittest.mock import Mock

import pytest

from nlt.api.client import SageClient
from nlt.core import evaluator
from nlt.core.types import (
    ChatCompletionResponse,
    FunctionDefinition,
    Scenario,
    ScenarioInput,
    Tool,
    ToolCall,
    TrialResult,
    Usage,
)

# Tool names chosen so none is a substring of another — parse_nlt_output matches
# each tool by searching for its name in the output, so overlapping names would
# cross-match.
TOOLS = ["Recap", "Website", "Discounts"]


def make_scenario() -> Scenario:
    """Build a small but real Scenario matching the current dataclass shape."""
    return Scenario(
        name="test_scenario",
        tools=TOOLS,
        prompts={
            "nlt": {"non_perturbed": "NLT prompt", "perturbed": "NLT prompt (perturbed)"},
            "structured": {"non_perturbed": "Structured prompt", "perturbed": "Structured prompt (perturbed)"},
        },
        inputs=[
            ScenarioInput(id=1, text="Test input 1", expected_tools={"Recap", "Website"}),
            ScenarioInput(id=2, text="Test input 2", expected_tools={"Recap"}),
        ],
        structured_function_map={
            "check_recap": "Recap",
            "check_website": "Website",
            "check_discounts": "Discounts",
        },
        tool_schemas=[
            Tool(function=FunctionDefinition(name="check_recap", description="Recap tool")),
            Tool(function=FunctionDefinition(name="check_website", description="Website tool")),
            Tool(function=FunctionDefinition(name="check_discounts", description="Discounts tool")),
        ],
    )


def make_client(response: ChatCompletionResponse | None = None, error: Exception | None = None) -> Mock:
    """A mock SageClient whose chat_completion returns ``response`` or raises ``error``."""
    client = Mock(spec=SageClient)
    client.default_model = "test-model"
    if error is not None:
        client.chat_completion.side_effect = error
    else:
        client.chat_completion.return_value = response
    return client


@pytest.fixture
def scenario() -> Scenario:
    return make_scenario()


@pytest.fixture
def nlt_response() -> ChatCompletionResponse:
    return ChatCompletionResponse(
        content="Recap -- YES\nWebsite -- YES\nDiscounts -- NO",
        raw={},
        usage=Usage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
    )


@pytest.fixture
def structured_response() -> ChatCompletionResponse:
    return ChatCompletionResponse(
        content="",
        raw={},
        usage=Usage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        tool_calls=[
            ToolCall(id="1", type="function", function={"name": "check_recap"}),
            ToolCall(id="2", type="function", function={"name": "check_website"}),
        ],
    )


def test_run_single_trial_nlt(scenario, nlt_response):
    """An NLT trial parses the YES/NO grid into predicted tools."""
    client = make_client(response=nlt_response)
    result = evaluator.run_single_trial(
        client=client,
        scenario=scenario,
        approach="nlt",
        perturbed=False,
        input_text="Test input 1",
        expected_tools={"Recap", "Website"},
        model="test-model",
        delay_seconds=0.0,
    )

    assert isinstance(result, TrialResult)
    assert result.expected_tools == {"Recap", "Website"}
    assert result.predicted_tools == {"Recap", "Website"}
    assert result.success is True
    assert result.raw_output == "Recap -- YES\nWebsite -- YES\nDiscounts -- NO"
    assert result.usage.total_tokens == 150
    assert result.error is None
    # NLT must not send tool schemas to the API.
    assert client.chat_completion.call_args.kwargs["tools"] is None


def test_run_single_trial_structured(scenario, structured_response):
    """A structured trial maps OpenAI-style tool_calls to tool names."""
    client = make_client(response=structured_response)
    result = evaluator.run_single_trial(
        client=client,
        scenario=scenario,
        approach="structured",
        perturbed=False,
        input_text="Test input 1",
        expected_tools={"Recap", "Website"},
        model="test-model",
        delay_seconds=0.0,
    )

    assert result.predicted_tools == {"Recap", "Website"}
    assert result.success is True
    # Structured must pass the scenario's tool schemas to the API.
    assert client.chat_completion.call_args.kwargs["tools"] == scenario.tool_schemas


def test_run_single_trial_api_error(scenario):
    """API exceptions become an error TrialResult instead of propagating."""
    client = make_client(error=Exception("API Error"))
    result = evaluator.run_single_trial(
        client=client,
        scenario=scenario,
        approach="nlt",
        perturbed=False,
        input_text="Test input 1",
        expected_tools={"Recap", "Website"},
        model="test-model",
        delay_seconds=0.0,
    )

    assert result.error == "API Error"
    assert result.success is False
    assert result.predicted_tools == set()


def test_evaluate_basic(scenario, nlt_response):
    """evaluate runs inputs x replicates and assigns each trial its input_id."""
    client = make_client(response=nlt_response)
    results, aborted = evaluator.evaluate(
        client=client,
        scenario=scenario,
        approach="nlt",
        perturbed=False,
        replicates=2,
        model="test-model",
    )

    assert len(results) == 4  # 2 inputs x 2 replicates
    assert all(isinstance(r, TrialResult) for r in results)
    assert {r.input_id for r in results} == {1, 2}
    assert aborted is False


def test_evaluate_sample_limit(scenario, nlt_response):
    """sample_limit caps how many inputs are evaluated."""
    client = make_client(response=nlt_response)
    results, aborted = evaluator.evaluate(
        client=client,
        scenario=scenario,
        approach="nlt",
        perturbed=False,
        replicates=2,
        model="test-model",
        sample_limit=1,
    )

    assert len(results) == 2  # 1 input x 2 replicates
    assert all(r.input_id == 1 for r in results)
    assert aborted is False


def test_evaluate_perturbed(scenario, nlt_response):
    """Perturbed evaluation sends the perturbed system prompt to the API."""
    client = make_client(response=nlt_response)
    results, aborted = evaluator.evaluate(
        client=client,
        scenario=scenario,
        approach="nlt",
        perturbed=True,
        replicates=1,
        model="test-model",
    )

    assert len(results) == 2  # 2 inputs x 1 replicate
    assert aborted is False
    sent_messages = client.chat_completion.call_args.kwargs["messages"]
    assert any("perturbed" in m.content.lower() for m in sent_messages)


def test_evaluate_aborts_after_consecutive_errors(scenario):
    """evaluate stops early once max_consecutive_errors is reached."""
    client = make_client(error=Exception("boom"))
    results, aborted = evaluator.evaluate(
        client=client,
        scenario=scenario,
        approach="nlt",
        perturbed=False,
        replicates=5,
        model="test-model",
        max_consecutive_errors=3,
    )

    assert aborted is True
    assert all(r.error for r in results)
    assert len(results) == 3  # aborts at the 3rd consecutive error, not all 10


def test_summarize():
    """Test summarize function."""
    results = [
        TrialResult(
            scenario="test",
            approach="nlt",
            perturbed=False,
            model="test",
            input_id=1,
            expected_tools=set(),
            predicted_tools=set(),
            success=True,
            raw_output="",
            error=None,
        ),
        TrialResult(
            scenario="test",
            approach="nlt",
            perturbed=False,
            model="test",
            input_id=1,
            expected_tools=set(),
            predicted_tools=set(),
            success=True,
            raw_output="",
            error=None,
        ),
        TrialResult(
            scenario="test",
            approach="nlt",
            perturbed=False,
            model="test",
            input_id=2,
            expected_tools=set(),
            predicted_tools=set(),
            success=False,
            raw_output="",
            error=None,
        ),
        TrialResult(
            scenario="test",
            approach="nlt",
            perturbed=False,
            model="test",
            input_id=2,
            expected_tools=set(),
            predicted_tools=set(),
            success=True,
            raw_output="",
            error=None,
        ),
    ]

    summary = evaluator.summarize(results)

    assert summary["accuracy"] == 0.75  # 3/4 success
    assert summary["total"] == 4
    assert summary["errors"] == 0
    assert summary["valid_trials"] == 4
    assert summary["aborted"] is False


def test_summarize_with_errors():
    """Test summarize with API errors."""
    results = [
        TrialResult(
            scenario="test",
            approach="nlt",
            perturbed=False,
            model="test",
            input_id=1,
            expected_tools=set(),
            predicted_tools=set(),
            success=True,
            raw_output="",
            error=None,
        ),
        TrialResult(
            scenario="test",
            approach="nlt",
            perturbed=False,
            model="test",
            input_id=1,
            expected_tools=set(),
            predicted_tools=set(),
            success=False,
            raw_output="",
            error="API Error",
        ),
        TrialResult(
            scenario="test",
            approach="nlt",
            perturbed=False,
            model="test",
            input_id=2,
            expected_tools=set(),
            predicted_tools=set(),
            success=False,
            raw_output="",
            error="Timeout",
        ),
    ]

    summary = evaluator.summarize(results)

    assert summary["accuracy"] == 1.0  # 1/1 valid trial succeeded
    assert summary["total"] == 3
    assert summary["errors"] == 2
    assert summary["valid_trials"] == 1


def test_summarize_empty():
    """Test summarize with empty results."""
    summary = evaluator.summarize([])

    assert summary["accuracy"] is None  # No valid trials = N/A
    assert summary["variance"] is None
    assert summary["total"] == 0
    assert summary["errors"] == 0
    assert summary["valid_trials"] == 0


def test_summarize_all_errors():
    """Test summarize when all trials are errors."""
    results = [
        TrialResult(
            scenario="test",
            approach="nlt",
            perturbed=False,
            model="test",
            input_id=1,
            expected_tools=set(),
            predicted_tools=set(),
            success=False,
            raw_output="",
            error="API Error",
        ),
        TrialResult(
            scenario="test",
            approach="nlt",
            perturbed=False,
            model="test",
            input_id=2,
            expected_tools=set(),
            predicted_tools=set(),
            success=False,
            raw_output="",
            error="API Error",
        ),
    ]

    summary = evaluator.summarize(results)

    assert summary["accuracy"] is None  # N/A when all trials errored
    assert summary["variance"] is None
    assert summary["total"] == 2
    assert summary["errors"] == 2
    assert summary["valid_trials"] == 0
