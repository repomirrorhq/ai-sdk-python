"""Tests for the Agent system."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from ai_sdk import Agent, AgentSettings, tool
from ai_sdk.providers.base import LanguageModel
from ai_sdk.providers.types import Message, FinishReason, Usage
from ai_sdk.core.generate_text import GenerateTextResult


class MockLanguageModel:
    """Mock language model for testing."""

    def __init__(self):
        self.provider_id = "test"
        self.model_id = "test-model"


@pytest.fixture
def mock_model():
    """Mock language model fixture."""
    return MockLanguageModel()


@pytest.fixture
def sample_tool():
    """Sample tool for testing."""
    @tool("calculator", "Perform arithmetic calculations")
    def calculator(expression: str) -> str:
        """Simple calculator tool."""
        try:
            result = eval(expression)  # In real use, use a safe evaluator
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    return calculator


def test_agent_initialization(mock_model):
    """Test agent initialization."""
    agent = Agent(
        model=mock_model,
        system="You are a helpful assistant.",
        temperature=0.7,
        max_tokens=100
    )

    assert agent.settings.model == mock_model
    assert agent.settings.system == "You are a helpful assistant."
    assert agent.settings.temperature == 0.7
    assert agent.settings.max_tokens == 100
    assert agent.settings.tools is None


def test_agent_with_tools(mock_model, sample_tool):
    """Test agent initialization with tools."""
    agent = Agent(
        model=mock_model,
        tools={"calculator": sample_tool},
        system="You are a math assistant."
    )

    assert agent.settings.model == mock_model
    assert agent.settings.tools is not None
    assert "calculator" in agent.settings.tools
    assert agent.get_tool("calculator") == sample_tool


def test_agent_tool_management(mock_model, sample_tool):
    """Test agent tool management methods."""
    agent = Agent(model=mock_model)

    # Initially no tools
    assert agent.list_tools() == []
    assert agent.get_tool("calculator") is None

    # Add tool
    agent.add_tool("calculator", sample_tool)
    assert agent.list_tools() == ["calculator"]
    assert agent.get_tool("calculator") == sample_tool

    # Remove tool
    agent.remove_tool("calculator")
    assert agent.list_tools() == []
    assert agent.get_tool("calculator") is None


def test_agent_settings_update(mock_model):
    """Test agent settings updates."""
    agent = Agent(model=mock_model, temperature=0.5)

    assert agent.settings.temperature == 0.5

    # Update settings
    agent.update_settings(temperature=0.8, max_tokens=200)
    assert agent.settings.temperature == 0.8
    assert agent.settings.max_tokens == 200

    # Test invalid setting
    with pytest.raises(ValueError, match="Unknown setting"):
        agent.update_settings(invalid_setting="value")


@pytest.mark.asyncio
async def test_agent_generate_basic(mock_model, monkeypatch):
    """Test basic agent generation."""
    # Mock the generate_text function
    mock_result = GenerateTextResult(
        text="Hello! How can I help you?",
        finish_reason=FinishReason.STOP,
        usage=Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        messages=[
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hello! How can I help you?")
        ]
    )

    mock_generate_text = AsyncMock(return_value=mock_result)
    monkeypatch.setattr("ai_sdk.agent.agent.generate_text", mock_generate_text)

    agent = Agent(
        model=mock_model,
        system="You are helpful.",
        temperature=0.7
    )

    result = await agent.generate("Hello")

    assert result == mock_result
    mock_generate_text.assert_called_once()

    # Verify the call arguments
    call_args = mock_generate_text.call_args[1]
    assert call_args["model"] == mock_model
    assert call_args["system"] == "You are helpful."
    assert call_args["prompt"] == "Hello"
    assert call_args["temperature"] == 0.7


@pytest.mark.asyncio
async def test_agent_generate_with_messages(mock_model, monkeypatch):
    """Test agent generation with messages."""
    mock_result = GenerateTextResult(
        text="I understand.",
        finish_reason=FinishReason.STOP,
        usage=Usage(prompt_tokens=15, completion_tokens=3, total_tokens=18),
        messages=[
            Message(role="system", content="You are helpful."),
            Message(role="user", content="Please help me"),
            Message(role="assistant", content="I understand.")
        ]
    )

    mock_generate_text = AsyncMock(return_value=mock_result)
    monkeypatch.setattr("ai_sdk.agent.agent.generate_text", mock_generate_text)

    agent = Agent(
        model=mock_model,
        system="You are helpful."
    )

    messages = [Message(role="user", content="Please help me")]
    result = await agent.generate(messages=messages)

    assert result == mock_result
    mock_generate_text.assert_called_once()

    # Verify the call arguments
    call_args = mock_generate_text.call_args[1]
    assert call_args["model"] == mock_model
    assert len(call_args["messages"]) == 2  # System message + user message
    assert call_args["messages"][0].role == "system"
    assert call_args["messages"][1].role == "user"


def test_agent_stream_method_exists(mock_model):
    """Test that the stream method exists and is callable."""
    agent = Agent(model=mock_model)

    # The stream method should exist
    assert hasattr(agent, 'stream')
    assert callable(agent.stream)

    # We can't easily test the actual streaming without complex mocking,
    # but we can ensure the method signature is correct
    import inspect
    sig = inspect.signature(agent.stream)
    expected_params = ['prompt', 'messages', 'provider_metadata', 'provider_options', 'kwargs']

    # Check that key parameters exist
    assert 'prompt' in sig.parameters
    assert 'messages' in sig.parameters


def test_agent_generate_requires_input(mock_model):
    """Test that generate requires either prompt or messages."""
    agent = Agent(model=mock_model)

    # Should raise error when no input provided
    with pytest.raises(ValueError, match="Either 'prompt' or 'messages' must be provided"):
        # We can't actually await this in a non-async test, but the validation
        # happens before the async part, so we test this by creating the
        # generation options and checking the validation
        agent.stream()  # This should raise the error synchronously
