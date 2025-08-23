"""Testing utilities for AI SDK Python.

This module provides mock providers, test helpers, and utilities for testing
AI SDK applications and the SDK itself.

Key features:
- Mock providers for all model types (Language, Embedding, Image, Speech, Transcription)
- Stream simulation utilities
- Test data generators
- Response builders
- Assertion helpers
"""

from .mock_providers import (
    MockLanguageModel,
    MockEmbeddingModel,
    MockImageModel,
    MockSpeechModel,
    MockTranscriptionModel,
    MockProvider,
)
from .stream_utils import (
    simulate_readable_stream,
    convert_array_to_async_iterable,
    convert_async_iterable_to_array,
)
from .test_helpers import (
    mock_id,
    create_test_messages,
    create_test_content,
    assert_tool_calls,
    assert_generation_result,
)
from .response_builders import (
    build_text_response,
    build_object_response,
    build_tool_call_response,
    build_error_response,
)

__all__ = [
    # Mock Providers
    "MockLanguageModel",
    "MockEmbeddingModel",
    "MockImageModel",
    "MockSpeechModel",
    "MockTranscriptionModel",
    "MockProvider",
    # Stream Utilities
    "simulate_readable_stream",
    "convert_array_to_async_iterable",
    "convert_async_iterable_to_array",
    # Test Helpers
    "mock_id",
    "create_test_messages",
    "create_test_content",
    "assert_tool_calls",
    "assert_generation_result",
    # Response Builders
    "build_text_response",
    "build_object_response", 
    "build_tool_call_response",
    "build_error_response",
]