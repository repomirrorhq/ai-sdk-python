"""Test reasoning functionality and utilities."""

import pytest
from unittest.mock import Mock

from ai_sdk.core.reasoning import (
    extract_reasoning_text,
    add_usage,
    has_reasoning_tokens,
    get_reasoning_token_ratio,
    ReasoningExtractor
)
from ai_sdk.providers.types import (
    Usage,
    TextContent,
    ReasoningContent,
    ProviderMetadata
)
from ai_sdk.providers.openai.reasoning_models import (
    is_reasoning_model,
    get_system_message_mode,
    filter_unsupported_params,
    process_reasoning_messages,
    REASONING_MODELS
)


class TestReasoningUtilities:
    """Test reasoning utility functions."""
    
    def test_extract_reasoning_text_with_reasoning_content(self):
        """Test extracting reasoning text from content list."""
        content = [
            TextContent(text="Regular text"),
            ReasoningContent(text="First reasoning step"),
            ReasoningContent(text="Second reasoning step"),
            TextContent(text="More regular text")
        ]
        
        reasoning_text = extract_reasoning_text(content)
        assert reasoning_text == "First reasoning step\nSecond reasoning step"
    
    def test_extract_reasoning_text_no_reasoning(self):
        """Test extracting reasoning text when none exists."""
        content = [
            TextContent(text="Regular text"),
            TextContent(text="More regular text")
        ]
        
        reasoning_text = extract_reasoning_text(content)
        assert reasoning_text is None
    
    def test_extract_reasoning_text_empty_list(self):
        """Test extracting reasoning text from empty list."""
        reasoning_text = extract_reasoning_text([])
        assert reasoning_text is None
    
    def test_add_usage_basic(self):
        """Test adding two usage objects."""
        usage1 = Usage(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            reasoning_tokens=50
        )
        usage2 = Usage(
            prompt_tokens=80,
            completion_tokens=150,
            total_tokens=230,
            reasoning_tokens=30
        )
        
        combined = add_usage(usage1, usage2)
        
        assert combined.prompt_tokens == 180
        assert combined.completion_tokens == 350
        assert combined.total_tokens == 530
        assert combined.reasoning_tokens == 80
    
    def test_add_usage_with_none_values(self):
        """Test adding usage objects with None values."""
        usage1 = Usage(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            reasoning_tokens=None
        )
        usage2 = Usage(
            prompt_tokens=80,
            completion_tokens=150,
            total_tokens=230,
            reasoning_tokens=50
        )
        
        combined = add_usage(usage1, usage2)
        
        assert combined.reasoning_tokens == 50
        assert combined.cached_input_tokens is None
    
    def test_has_reasoning_tokens_true(self):
        """Test has_reasoning_tokens with reasoning tokens."""
        usage = Usage(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            reasoning_tokens=50
        )
        
        assert has_reasoning_tokens(usage) is True
    
    def test_has_reasoning_tokens_false(self):
        """Test has_reasoning_tokens without reasoning tokens."""
        usage = Usage(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            reasoning_tokens=None
        )
        
        assert has_reasoning_tokens(usage) is False
    
    def test_get_reasoning_token_ratio(self):
        """Test calculating reasoning token ratio."""
        usage = Usage(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            reasoning_tokens=60
        )
        
        ratio = get_reasoning_token_ratio(usage)
        assert ratio == 0.2  # 60/300 = 0.2
    
    def test_get_reasoning_token_ratio_none(self):
        """Test reasoning token ratio with no reasoning tokens."""
        usage = Usage(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            reasoning_tokens=None
        )
        
        ratio = get_reasoning_token_ratio(usage)
        assert ratio is None


class TestReasoningExtractor:
    """Test ReasoningExtractor utility class."""
    
    def test_add_reasoning(self):
        """Test adding reasoning content."""
        extractor = ReasoningExtractor()
        
        reasoning = extractor.add_reasoning("Test reasoning", None)
        
        assert isinstance(reasoning, ReasoningContent)
        assert reasoning.text == "Test reasoning"
        assert len(extractor.reasoning_parts) == 1
    
    def test_get_combined_reasoning(self):
        """Test getting combined reasoning text."""
        extractor = ReasoningExtractor()
        
        extractor.add_reasoning("First step")
        extractor.add_reasoning("Second step")
        extractor.add_reasoning("Third step")
        
        combined = extractor.get_combined_reasoning()
        assert combined == "First step\nSecond step\nThird step"
    
    def test_clear(self):
        """Test clearing reasoning content."""
        extractor = ReasoningExtractor()
        
        extractor.add_reasoning("Test reasoning")
        assert len(extractor.reasoning_parts) == 1
        
        extractor.clear()
        assert len(extractor.reasoning_parts) == 0


class TestOpenAIReasoningModels:
    """Test OpenAI reasoning model utilities."""
    
    def test_is_reasoning_model_true(self):
        """Test identifying reasoning models."""
        assert is_reasoning_model("o1-mini") is True
        assert is_reasoning_model("o1-preview") is True
        assert is_reasoning_model("o1-2024-12-17") is True
    
    def test_is_reasoning_model_false(self):
        """Test identifying non-reasoning models."""
        assert is_reasoning_model("gpt-4") is False
        assert is_reasoning_model("gpt-3.5-turbo") is False
        assert is_reasoning_model("random-model") is False
    
    def test_get_system_message_mode_remove(self):
        """Test system message mode for models that remove system messages."""
        assert get_system_message_mode("o1-mini") == "remove"
        assert get_system_message_mode("o1-preview") == "remove"
    
    def test_get_system_message_mode_developer(self):
        """Test system message mode for models that convert to developer."""
        assert get_system_message_mode("o1-2024-12-17") == "developer"
    
    def test_get_system_message_mode_default(self):
        """Test system message mode for non-reasoning models."""
        assert get_system_message_mode("gpt-4") == "system"
    
    def test_filter_unsupported_params(self):
        """Test filtering unsupported parameters for reasoning models."""
        params = {
            "model": "o1-mini",
            "messages": [],
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1000,
            "stream": False
        }
        
        filtered, removed = filter_unsupported_params("o1-mini", params)
        
        assert "temperature" not in filtered
        assert "top_p" not in filtered
        assert "max_completion_tokens" in filtered
        assert "max_tokens" not in filtered
        assert filtered["max_completion_tokens"] == 1000
        assert "temperature" in removed
        assert "top_p" in removed
    
    def test_filter_unsupported_params_non_reasoning(self):
        """Test that non-reasoning models don't get filtered."""
        params = {
            "model": "gpt-4",
            "messages": [],
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1000
        }
        
        filtered, removed = filter_unsupported_params("gpt-4", params)
        
        assert filtered == params
        assert removed == []
    
    def test_process_reasoning_messages_remove(self):
        """Test message processing for models that remove system messages."""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        processed = process_reasoning_messages("o1-mini", messages)
        
        # System message should be removed
        assert len(processed) == 2
        assert processed[0]["role"] == "user"
        assert processed[1]["role"] == "assistant"
    
    def test_process_reasoning_messages_developer(self):
        """Test message processing for models that convert system to developer."""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        
        processed = process_reasoning_messages("o1-2024-12-17", messages)
        
        # System message should become developer message
        assert len(processed) == 2
        assert processed[0]["role"] == "developer"
        assert processed[0]["content"] == "You are helpful"
        assert processed[1]["role"] == "user"
    
    def test_reasoning_models_constant(self):
        """Test that REASONING_MODELS constant contains expected models."""
        assert "o1-mini" in REASONING_MODELS
        assert "o1-preview" in REASONING_MODELS
        assert "o1-2024-12-17" in REASONING_MODELS
        assert "gpt-4" not in REASONING_MODELS


@pytest.mark.asyncio
async def test_usage_integration():
    """Integration test for usage objects with reasoning tokens."""
    # Test the Usage model with reasoning tokens
    usage = Usage(
        prompt_tokens=100,
        completion_tokens=200,
        total_tokens=300,
        reasoning_tokens=50,
        cached_input_tokens=25
    )
    
    # Test serialization/deserialization works
    usage_dict = usage.dict()
    assert usage_dict["reasoning_tokens"] == 50
    assert usage_dict["cached_input_tokens"] == 25
    
    # Test reconstruction
    new_usage = Usage(**usage_dict)
    assert new_usage.reasoning_tokens == 50
    assert new_usage.cached_input_tokens == 25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])