"""Unit tests for NLT evaluator module."""

import pytest
from unittest.mock import Mock, patch
from nlt.core import evaluator
from nlt.core.types import ChatCompletionResponse, Message, Usage


@pytest.fixture
def mock_scenario():
    """Create a mock scenario for testing."""
    return Mock(
        name="test_scenario",
        inputs=[
            {"id": 1, "text": "Test input 1", "expected_tools": {"Tool A", "Tool B"}},
            {"id": 2, "text": "Test input 2", "expected_tools": {"Tool A"}},
        ],
        system_prompt_nlt="NLT system prompt",
        system_prompt_structured="Structured system prompt",
        available_tools=["Tool A", "Tool B", "Tool C"],
        tool_schemas=[],
        function_name_map={},
    )


@pytest.fixture
def mock_response():
    """Create a mock API response."""
    return ChatCompletionResponse(
        id="test-123",
        object="chat.completion",
        created=1234567890,
        model="test-model",
        choices=[
            {
                "index": 0,
                "message": Message(
                    role="assistant",
                    content="Tool A -- YES\nTool B -- YES\nTool C -- NO",
                ),
                "finish_reason": "stop",
            }
        ],
        usage=Usage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
    )


def test_run_single_trial_nlt(mock_scenario, mock_response):
    """Test running a single NLT trial."""
    with patch("nlt.api.client.chat_completion", return_value=mock_response):
        result = evaluator.run_single_trial(
            input_data=mock_scenario.inputs[0],
            scenario=mock_scenario,
            approach="nlt",
            model="test-model",
            api_url="https://test.api",
            auth_token="test-token",
        )

    assert result["input_id"] == 1
    assert result["expected_tools"] == {"Tool A", "Tool B"}
    assert "predicted_tools" in result
    assert "success" in result
    assert result["raw_output"] == "Tool A -- YES\nTool B -- YES\nTool C -- NO"
    assert result["usage"]["total_tokens"] == 150


def test_run_single_trial_structured(mock_scenario):
    """Test running a single structured trial."""
    from nlt.core.types import ToolCall

    structured_response = ChatCompletionResponse(
        id="test-123",
        object="chat.completion",
        created=1234567890,
        model="test-model",
        choices=[
            {
                "index": 0,
                "message": Message(
                    role="assistant",
                    content="",
                    tool_calls=[
                        ToolCall(id="1", type="function", function={"name": "tool_a"}),
                        ToolCall(id="2", type="function", function={"name": "tool_b"}),
                    ],
                ),
                "finish_reason": "tool_calls",
            }
        ],
        usage=Usage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
    )

    mock_scenario.function_name_map = {"tool_a": "Tool A", "tool_b": "Tool B"}

    with patch("nlt.api.client.chat_completion", return_value=structured_response):
        result = evaluator.run_single_trial(
            input_data=mock_scenario.inputs[0],
            scenario=mock_scenario,
            approach="structured",
            model="test-model",
            api_url="https://test.api",
            auth_token="test-token",
        )

    assert result["input_id"] == 1
    assert result["expected_tools"] == {"Tool A", "Tool B"}
    assert "predicted_tools" in result
    assert "success" in result


def test_run_single_trial_api_error(mock_scenario):
    """Test handling of API errors."""
    with patch("nlt.api.client.chat_completion", side_effect=Exception("API Error")):
        result = evaluator.run_single_trial(
            input_data=mock_scenario.inputs[0],
            scenario=mock_scenario,
            approach="nlt",
            model="test-model",
            api_url="https://test.api",
            auth_token="test-token",
        )

    assert result["input_id"] == 1
    assert result["error"] == "API Error"
    assert result["success"] is False


def test_evaluate_basic(mock_scenario, mock_response):
    """Test basic evaluation with mocked API."""
    with patch("nlt.api.client.chat_completion", return_value=mock_response):
        results = evaluator.evaluate(
            scenario=mock_scenario,
            approach="nlt",
            model="test-model",
            replicates=2,
            api_url="https://test.api",
            auth_token="test-token",
        )

    # Should have 2 inputs × 2 replicates = 4 results
    assert len(results) == 4
    assert all("input_id" in r for r in results)
    assert all("success" in r for r in results)


def test_evaluate_sample_limit(mock_scenario, mock_response):
    """Test evaluation with sample limit."""
    with patch("nlt.api.client.chat_completion", return_value=mock_response):
        results = evaluator.evaluate(
            scenario=mock_scenario,
            approach="nlt",
            model="test-model",
            replicates=2,
            sample_limit=1,
            api_url="https://test.api",
            auth_token="test-token",
        )

    # Should have 1 input × 2 replicates = 2 results
    assert len(results) == 2


def test_summarize():
    """Test summarize function."""
    results = [
        {"input_id": 1, "success": True, "error": None},
        {"input_id": 1, "success": True, "error": None},
        {"input_id": 2, "success": False, "error": None},
        {"input_id": 2, "success": True, "error": None},
    ]

    summary = evaluator.summarize(results)

    assert summary["accuracy"] == 0.75  # 3/4 success
    assert summary["total"] == 4
    assert summary["errors"] == 0


def test_summarize_with_errors():
    """Test summarize with API errors."""
    results = [
        {"input_id": 1, "success": True, "error": None},
        {"input_id": 1, "success": False, "error": "API Error"},
        {"input_id": 2, "success": False, "error": "Timeout"},
    ]

    summary = evaluator.summarize(results)

    assert summary["accuracy"] == 1 / 3  # Only 1 success
    assert summary["total"] == 3
    assert summary["errors"] == 2


def test_summarize_empty():
    """Test summarize with empty results."""
    summary = evaluator.summarize([])

    assert summary["accuracy"] == 0.0
    assert summary["variance"] == 0.0
    assert summary["total"] == 0
    assert summary["errors"] == 0


def test_evaluate_perturbed(mock_scenario, mock_response):
    """Test evaluation with perturbed prompts."""
    with patch("nlt.api.client.chat_completion", return_value=mock_response):
        results = evaluator.evaluate(
            scenario=mock_scenario,
            approach="nlt",
            model="test-model",
            replicates=1,
            perturbed=True,
            api_url="https://test.api",
            auth_token="test-token",
        )

    assert len(results) == 2  # 2 inputs, 1 replicate each
    # Would verify perturbed prompts were used, but that requires inspecting the API call
