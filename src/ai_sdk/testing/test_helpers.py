"""Test helpers and utilities for AI SDK testing."""

import uuid
from typing import Any, Dict, List, Optional, Union
from ..providers.types import Message, Content


def mock_id() -> str:
    """Generate a mock ID for testing.
    
    Returns:
        A predictable mock ID string
    """
    return f"mock-{uuid.uuid4().hex[:8]}"


def create_test_messages(
    user_message: str = "Test message",
    assistant_message: Optional[str] = "Test response",
    system_message: Optional[str] = None,
) -> List[Message]:
    """Create test messages for testing AI interactions.
    
    Args:
        user_message: User message content
        assistant_message: Assistant response (optional)
        system_message: System message (optional)
        
    Returns:
        List of test messages
    """
    messages = []
    
    if system_message:
        messages.append({
            "role": "system",
            "content": system_message
        })
    
    messages.append({
        "role": "user", 
        "content": user_message
    })
    
    if assistant_message:
        messages.append({
            "role": "assistant",
            "content": assistant_message
        })
    
    return messages


def create_test_content(
    text: Optional[str] = None,
    image_url: Optional[str] = None,
    image_data: Optional[bytes] = None,
) -> List[Content]:
    """Create test content for multimodal messages.
    
    Args:
        text: Text content
        image_url: Image URL
        image_data: Image data
        
    Returns:
        List of content items
    """
    content = []
    
    if text:
        content.append({
            "type": "text",
            "text": text
        })
    
    if image_url:
        content.append({
            "type": "image",
            "image": {"url": image_url}
        })
    
    if image_data:
        import base64
        content.append({
            "type": "image", 
            "image": {
                "data": base64.b64encode(image_data).decode(),
                "mime_type": "image/png"
            }
        })
    
    return content


def assert_tool_calls(
    result: Any,
    expected_tool_names: List[str],
    expected_count: Optional[int] = None,
):
    """Assert that a result contains expected tool calls.
    
    Args:
        result: Generation result to check
        expected_tool_names: List of expected tool names
        expected_count: Expected number of tool calls
    """
    assert hasattr(result, 'tool_calls'), "Result should have tool_calls attribute"
    
    tool_calls = result.tool_calls
    actual_tool_names = [call.tool_name for call in tool_calls]
    
    if expected_count is not None:
        assert len(tool_calls) == expected_count, f"Expected {expected_count} tool calls, got {len(tool_calls)}"
    
    for expected_name in expected_tool_names:
        assert expected_name in actual_tool_names, f"Expected tool '{expected_name}' not found in {actual_tool_names}"


def assert_generation_result(
    result: Any,
    expected_text: Optional[str] = None,
    expected_finish_reason: Optional[str] = None,
    should_have_usage: bool = True,
    should_have_tool_calls: bool = False,
):
    """Assert properties of a generation result.
    
    Args:
        result: Generation result to check
        expected_text: Expected text content
        expected_finish_reason: Expected finish reason
        should_have_usage: Whether result should have usage info
        should_have_tool_calls: Whether result should have tool calls
    """
    if expected_text is not None:
        assert hasattr(result, 'text'), "Result should have text attribute"
        assert result.text == expected_text, f"Expected text '{expected_text}', got '{result.text}'"
    
    if expected_finish_reason is not None:
        assert hasattr(result, 'finish_reason'), "Result should have finish_reason attribute"
        assert result.finish_reason == expected_finish_reason, f"Expected finish_reason '{expected_finish_reason}', got '{result.finish_reason}'"
    
    if should_have_usage:
        assert hasattr(result, 'usage'), "Result should have usage attribute"
        assert result.usage is not None, "Usage should not be None"
    
    if should_have_tool_calls:
        assert hasattr(result, 'tool_calls'), "Result should have tool_calls attribute"
        assert len(result.tool_calls) > 0, "Should have at least one tool call"
    else:
        if hasattr(result, 'tool_calls'):
            assert len(result.tool_calls) == 0, "Should not have any tool calls"


class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def create_chat_messages(count: int = 3) -> List[Message]:
        """Create a conversation with multiple messages."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]
        
        for i in range(count):
            messages.append({
                "role": "user",
                "content": f"User message {i + 1}"
            })
            messages.append({
                "role": "assistant", 
                "content": f"Assistant response {i + 1}"
            })
        
        return messages
    
    @staticmethod
    def create_multimodal_message(
        text: str = "Analyze this image",
        image_count: int = 1
    ) -> Message:
        """Create a multimodal message with text and images."""
        content = [{"type": "text", "text": text}]
        
        for i in range(image_count):
            content.append({
                "type": "image",
                "image": {"url": f"https://example.com/image{i + 1}.jpg"}
            })
        
        return {
            "role": "user",
            "content": content
        }
    
    @staticmethod
    def create_tool_call_message(
        tool_name: str = "test_tool",
        tool_args: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Create a message with tool calls."""
        return {
            "role": "assistant",
            "content": "",
            "tool_calls": [{
                "id": mock_id(),
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": tool_args or {"param": "value"}
                }
            }]
        }


class AssertionHelpers:
    """Additional assertion helpers for testing."""
    
    @staticmethod
    def assert_valid_uuid(value: str):
        """Assert that a string is a valid UUID."""
        try:
            uuid.UUID(value)
        except ValueError:
            raise AssertionError(f"'{value}' is not a valid UUID")
    
    @staticmethod
    def assert_positive_number(value: Union[int, float], name: str = "value"):
        """Assert that a number is positive."""
        assert isinstance(value, (int, float)), f"{name} should be a number"
        assert value > 0, f"{name} should be positive, got {value}"
    
    @staticmethod
    def assert_non_empty_string(value: str, name: str = "value"):
        """Assert that a string is not empty."""
        assert isinstance(value, str), f"{name} should be a string"
        assert len(value) > 0, f"{name} should not be empty"
    
    @staticmethod
    def assert_dict_contains_keys(d: dict, keys: List[str]):
        """Assert that a dictionary contains all specified keys."""
        for key in keys:
            assert key in d, f"Dictionary missing key '{key}'. Available keys: {list(d.keys())}"
    
    @staticmethod
    def assert_list_length(lst: list, expected_length: int, name: str = "list"):
        """Assert that a list has expected length."""
        actual_length = len(lst)
        assert actual_length == expected_length, f"{name} should have length {expected_length}, got {actual_length}"


# Convenience exports
assert_valid_uuid = AssertionHelpers.assert_valid_uuid
assert_positive_number = AssertionHelpers.assert_positive_number
assert_non_empty_string = AssertionHelpers.assert_non_empty_string
assert_dict_contains_keys = AssertionHelpers.assert_dict_contains_keys
assert_list_length = AssertionHelpers.assert_list_length