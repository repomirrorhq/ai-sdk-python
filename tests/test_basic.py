"""Basic tests for AI SDK Python."""

import pytest

from ai_sdk import __version__
from ai_sdk.errors import AISDKError, InvalidArgumentError
from ai_sdk.utils import secure_json_parse


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_error_hierarchy():
    """Test error class hierarchy."""
    # Test basic error creation
    error = AISDKError("Test error")
    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.cause is None
    assert error.metadata == {}
    
    # Test error with metadata
    error = AISDKError("Test error", metadata={"key": "value"})
    assert error.metadata == {"key": "value"}
    
    # Test specific error type
    error = InvalidArgumentError("Invalid arg", argument="test", value=123)
    assert error.argument == "test"
    assert error.value == 123


def test_secure_json_parse():
    """Test secure JSON parsing."""
    # Test valid JSON
    result = secure_json_parse('{"key": "value"}')
    assert result == {"key": "value"}
    
    # Test with expected type
    result = secure_json_parse('{"key": "value"}', expected_type=dict)
    assert result == {"key": "value"}
    
    # Test invalid JSON
    with pytest.raises(Exception):
        secure_json_parse("invalid json")
    
    # Test wrong type
    with pytest.raises(Exception):
        secure_json_parse('["list"]', expected_type=dict)