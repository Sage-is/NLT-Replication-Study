"""Unit tests for NLT parser module."""

from nlt.core import parser


def test_parse_nlt_output_all_yes():
    """Test parsing when all tools are marked YES."""
    output = """
Thinking: All tools are relevant
Website information -- YES
Past Purchases -- YES
Talk to a Human -- YES
Assessment finished.
"""
    tools = ["Website information", "Past Purchases", "Talk to a Human"]
    result = parser.parse_nlt_output(output, tools)

    assert result == {
        "Website information": True,
        "Past Purchases": True,
        "Talk to a Human": True,
    }


def test_parse_nlt_output_all_no():
    """Test parsing when all tools are marked NO."""
    output = """
Thinking: No tools needed
Website information -- NO
Past Purchases -- NO
Talk to a Human -- NO
Assessment finished.
"""
    tools = ["Website information", "Past Purchases", "Talk to a Human"]
    result = parser.parse_nlt_output(output, tools)

    assert result == {
        "Website information": False,
        "Past Purchases": False,
        "Talk to a Human": False,
    }


def test_parse_nlt_output_mixed():
    """Test parsing with mixed YES/NO responses."""
    output = """
Thinking: Some tools relevant
Website information -- YES
Past Purchases -- NO
Talk to a Human -- YES
Assessment finished.
"""
    tools = ["Website information", "Past Purchases", "Talk to a Human"]
    result = parser.parse_nlt_output(output, tools)

    assert result == {
        "Website information": True,
        "Past Purchases": False,
        "Talk to a Human": True,
    }


def test_parse_nlt_output_case_insensitive():
    """Test that YES/NO matching is case-insensitive."""
    output = """
Thinking: Testing case sensitivity
Website information -- yes
Past Purchases -- No
Talk to a Human -- YES
Assessment finished.
"""
    tools = ["Website information", "Past Purchases", "Talk to a Human"]
    result = parser.parse_nlt_output(output, tools)

    assert result == {
        "Website information": True,
        "Past Purchases": False,
        "Talk to a Human": True,
    }


def test_parse_nlt_output_missing_tool():
    """Test that missing tools default to False."""
    output = """
Thinking: Only some tools mentioned
Website information -- YES
Talk to a Human -- NO
Assessment finished.
"""
    tools = ["Website information", "Past Purchases", "Talk to a Human"]
    result = parser.parse_nlt_output(output, tools)

    assert result == {
        "Website information": True,
        "Past Purchases": False,  # Missing, should default to False
        "Talk to a Human": False,
    }


def test_parse_nlt_output_extra_text():
    """Test parsing with extra commentary in output."""
    output = """
Let me analyze this request.

Thinking: The user is asking about website and purchases
Website information -- YES (they mentioned the website)
Past Purchases -- YES (asking about previous orders)
Talk to a Human -- NO (no request to speak with agent)

Assessment finished.

I hope that helps!
"""
    tools = ["Website information", "Past Purchases", "Talk to a Human"]
    result = parser.parse_nlt_output(output, tools)

    assert result == {
        "Website information": True,
        "Past Purchases": True,
        "Talk to a Human": False,
    }


def test_parse_tool_calls_basic():
    """Test tool_calls parsing."""
    from nlt.core.types import ToolCall

    tool_calls = [
        ToolCall(id="1", type="function", function={"name": "check_website_information"}),
        ToolCall(id="2", type="function", function={"name": "check_past_purchases"}),
    ]
    function_map = {
        "check_website_information": "Website information",
        "check_past_purchases": "Past Purchases",
        "check_talk_to_a_human": "Talk to a Human",
    }
    result = parser.parse_tool_calls(tool_calls, function_map)

    assert result == {"Website information", "Past Purchases"}


def test_parse_tool_calls_none():
    """Test tool_calls parsing when no tools are called."""
    from nlt.core.types import ToolCall

    tool_calls = []
    function_map = {
        "check_website_information": "Website information",
        "check_past_purchases": "Past Purchases",
    }
    result = parser.parse_tool_calls(tool_calls, function_map)

    assert result == set()


def test_parse_tool_calls_unknown_function():
    """Test that unknown function names are ignored."""
    from nlt.core.types import ToolCall

    tool_calls = [
        ToolCall(id="1", type="function", function={"name": "check_website_information"}),
        ToolCall(id="2", type="function", function={"name": "unknown_function"}),
    ]
    function_map = {
        "check_website_information": "Website information",
        "check_past_purchases": "Past Purchases",
    }
    result = parser.parse_tool_calls(tool_calls, function_map)

    assert result == {"Website information"}


def test_exact_match_success():
    """Test exact match when sets are equal."""
    expected = {"Website information", "Past Purchases"}
    predicted = {"Website information", "Past Purchases"}
    assert parser.exact_match(expected, predicted) is True


def test_exact_match_failure_extra():
    """Test exact match fails when predicted has extra tools."""
    expected = {"Website information"}
    predicted = {"Website information", "Past Purchases"}
    assert parser.exact_match(expected, predicted) is False


def test_exact_match_failure_missing():
    """Test exact match fails when predicted is missing tools."""
    expected = {"Website information", "Past Purchases"}
    predicted = {"Website information"}
    assert parser.exact_match(expected, predicted) is False


def test_accuracy_and_variance_all_success():
    """Test accuracy/variance calculation with all successes."""
    results = [True, True, True, True, True]
    stats = parser.accuracy_and_variance(results)

    assert stats["accuracy"] == 1.0
    assert stats["variance"] == 0.0


def test_accuracy_and_variance_all_failure():
    """Test accuracy/variance calculation with all failures."""
    results = [False, False, False, False, False]
    stats = parser.accuracy_and_variance(results)

    assert stats["accuracy"] == 0.0
    assert stats["variance"] == 0.0


def test_accuracy_and_variance_mixed():
    """Test accuracy/variance calculation with mixed results."""
    results = [True, True, False, False]
    stats = parser.accuracy_and_variance(results)

    assert stats["accuracy"] == 0.5
    assert stats["variance"] == 0.25


def test_accuracy_and_variance_empty():
    """Test accuracy/variance with empty input."""
    results = []
    stats = parser.accuracy_and_variance(results)

    assert stats["accuracy"] == 0.0
    assert stats["variance"] == 0.0
