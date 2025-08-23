"""Integration tests for OpenAI provider."""

import pytest

from ai_sdk.providers.openai import OpenAIProvider
from ai_sdk.core.generate_text import generate_text


@pytest.mark.skip("Requires OpenAI API key")
async def test_openai_generate_text():
    """Test basic text generation with OpenAI."""
    provider = OpenAIProvider()
    model = provider.language_model("gpt-3.5-turbo")
    
    result = await generate_text(
        model,
        prompt="Hello, how are you?",
        max_tokens=50,
    )
    
    assert result.text
    assert result.usage.total_tokens > 0
    assert result.finish_reason
    assert len(result.content) > 0


def test_openai_provider_creation():
    """Test OpenAI provider creation without API key."""
    # This should work without API key for testing
    try:
        provider = OpenAIProvider(api_key="test-key")
        assert provider.name == "openai"
        assert provider.api_key == "test-key"
        
        model = provider.language_model("gpt-4")
        assert model.model_id == "gpt-4"
        assert model.provider_name == "openai"
    except Exception as e:
        pytest.fail(f"Provider creation failed: {e}")


def test_openai_provider_requires_api_key():
    """Test that OpenAI provider requires API key."""
    import os
    
    # Temporarily remove API key from environment
    old_key = os.environ.get("OPENAI_API_KEY")
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    try:
        with pytest.raises(ValueError, match="OpenAI API key not found"):
            OpenAIProvider()
    finally:
        # Restore API key
        if old_key:
            os.environ["OPENAI_API_KEY"] = old_key