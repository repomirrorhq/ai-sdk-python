"""Tests for the AI SDK middleware system."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from ai_sdk.middleware import (
    wrap_language_model,
    logging_middleware,
    caching_middleware,
    default_settings_middleware,
    telemetry_middleware,
)
from ai_sdk.middleware.base import SimpleMiddleware
from ai_sdk.middleware.types import GenerateTextParams, GenerateTextResult
from ai_sdk.providers.base import LanguageModel
from ai_sdk.providers.types import Usage, FinishReason


class MockLanguageModel:
    """Mock language model for testing."""
    
    def __init__(self, provider="test", model_id="test-model"):
        self.provider = provider
        self.model_id = model_id
    
    async def generate_text(self, params: dict) -> GenerateTextResult:
        """Mock generate text implementation."""
        return GenerateTextResult(
            text="Mock response",
            usage=Usage(prompt_tokens=10, completion_tokens=15, total_tokens=25),
            finish_reason=FinishReason.STOP,
            response_id="test-123",
        )
    
    async def stream_text(self, params: dict):
        """Mock stream text implementation."""
        # Simple async generator for testing
        async def mock_stream():
            yield {"type": "text-delta", "text_delta": "Mock "}
            yield {"type": "text-delta", "text_delta": "streaming "}
            yield {"type": "text-delta", "text_delta": "response"}
        
        return mock_stream()


@pytest.fixture
def mock_model():
    """Fixture providing a mock language model."""
    return MockLanguageModel()


@pytest.mark.asyncio
async def test_wrap_language_model_basic(mock_model):
    """Test basic language model wrapping."""
    wrapped = wrap_language_model(model=mock_model, middleware=[])
    
    # Should maintain the same interface
    assert wrapped.provider == "test"
    assert wrapped.model_id == "test-model"
    
    # Should work without middleware
    result = await wrapped.generate_text({"messages": [{"role": "user", "content": "test"}]})
    assert result.text == "Mock response"


@pytest.mark.asyncio
async def test_transform_params_middleware(mock_model):
    """Test parameter transformation middleware."""
    
    async def transform_params(*, params, type, model):
        # Add a system message
        messages = list(params.get("messages", []))
        messages.insert(0, {"role": "system", "content": "You are helpful."})
        return {**params, "messages": messages}
    
    middleware = SimpleMiddleware()
    middleware.transformParams = transform_params
    
    wrapped = wrap_language_model(model=mock_model, middleware=[middleware])
    
    # Mock the underlying generate_text to capture params
    original_generate = mock_model.generate_text
    captured_params = None
    
    async def capture_generate(params):
        nonlocal captured_params
        captured_params = params
        return await original_generate(params)
    
    mock_model.generate_text = capture_generate
    
    # Make request
    await wrapped.generate_text({"messages": [{"role": "user", "content": "Hello"}]})
    
    # Should have added system message
    assert len(captured_params["messages"]) == 2
    assert captured_params["messages"][0]["role"] == "system"
    assert captured_params["messages"][0]["content"] == "You are helpful."


@pytest.mark.asyncio
async def test_wrap_generate_middleware(mock_model):
    """Test generate method wrapping middleware."""
    
    call_count = 0
    
    async def wrap_generate(*, do_generate, params, model):
        nonlocal call_count
        call_count += 1
        
        # Call the original and modify response
        result = await do_generate()
        return GenerateTextResult(
            text=f"Modified: {result.text}",
            usage=result.usage,
            finish_reason=result.finish_reason,
            response_id=result.response_id,
        )
    
    middleware = SimpleMiddleware()
    middleware.wrapGenerate = wrap_generate
    
    wrapped = wrap_language_model(model=mock_model, middleware=[middleware])
    
    result = await wrapped.generate_text({"messages": [{"role": "user", "content": "test"}]})
    
    assert call_count == 1
    assert result.text == "Modified: Mock response"


@pytest.mark.asyncio
async def test_middleware_composition(mock_model):
    """Test composing multiple middleware."""
    
    transform_called = False
    wrap_called = False
    
    async def transform_params(*, params, type, model):
        nonlocal transform_called
        transform_called = True
        return {**params, "temperature": 0.5}
    
    async def wrap_generate(*, do_generate, params, model):
        nonlocal wrap_called
        wrap_called = True
        result = await do_generate()
        return result
    
    middleware1 = SimpleMiddleware()
    middleware1.transformParams = transform_params
    
    middleware2 = SimpleMiddleware()
    middleware2.wrapGenerate = wrap_generate
    
    wrapped = wrap_language_model(model=mock_model, middleware=[middleware1, middleware2])
    
    await wrapped.generate_text({"messages": [{"role": "user", "content": "test"}]})
    
    assert transform_called
    assert wrap_called


@pytest.mark.asyncio
async def test_logging_middleware(mock_model, caplog):
    """Test logging middleware functionality."""
    middleware = logging_middleware(level="INFO")
    wrapped = wrap_language_model(model=mock_model, middleware=[middleware])
    
    await wrapped.generate_text({"messages": [{"role": "user", "content": "test"}]})
    
    # Should have logged the request and response
    assert any("Generate request" in record.message for record in caplog.records)


@pytest.mark.asyncio
async def test_caching_middleware(mock_model):
    """Test caching middleware functionality."""
    cache_store = {}
    middleware = caching_middleware(ttl=60, cache_store=cache_store)
    wrapped = wrap_language_model(model=mock_model, middleware=[middleware])
    
    params = {"messages": [{"role": "user", "content": "test"}]}
    
    # First call should execute
    result1 = await wrapped.generate_text(params)
    assert len(cache_store) == 1
    
    # Second call should hit cache
    result2 = await wrapped.generate_text(params)
    assert result1.text == result2.text
    assert len(cache_store) == 1  # Should still be 1 item


@pytest.mark.asyncio
async def test_default_settings_middleware(mock_model):
    """Test default settings middleware."""
    middleware = default_settings_middleware(
        default_temperature=0.7,
        default_max_tokens=100,
        default_system_message="You are helpful.",
    )
    
    wrapped = wrap_language_model(model=mock_model, middleware=[middleware])
    
    # Mock to capture transformed params
    captured_params = None
    original_generate = mock_model.generate_text
    
    async def capture_generate(params):
        nonlocal captured_params
        captured_params = params
        return await original_generate(params)
    
    mock_model.generate_text = capture_generate
    
    # Make request without specifying defaults
    await wrapped.generate_text({"messages": [{"role": "user", "content": "Hello"}]})
    
    # Should have applied defaults
    assert captured_params["temperature"] == 0.7
    assert captured_params["max_tokens"] == 100
    assert captured_params["messages"][0]["role"] == "system"
    assert captured_params["messages"][0]["content"] == "You are helpful."


@pytest.mark.asyncio
async def test_telemetry_middleware(mock_model):
    """Test telemetry middleware functionality."""
    telemetry_data = []
    
    async def callback(data):
        telemetry_data.append(data)
    
    middleware = telemetry_middleware(callback=callback)
    wrapped = wrap_language_model(model=mock_model, middleware=[middleware])
    
    await wrapped.generate_text({"messages": [{"role": "user", "content": "test"}]})
    
    assert len(telemetry_data) == 1
    data = telemetry_data[0]
    assert data["provider"] == "test"
    assert data["model"] == "test-model"
    assert data["operation"] == "generate"
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_middleware_error_handling(mock_model):
    """Test middleware error handling."""
    
    async def failing_wrap_generate(*, do_generate, params, model):
        raise ValueError("Test error")
    
    middleware = SimpleMiddleware()
    middleware.wrapGenerate = failing_wrap_generate
    
    wrapped = wrap_language_model(model=mock_model, middleware=[middleware])
    
    with pytest.raises(ValueError, match="Test error"):
        await wrapped.generate_text({"messages": [{"role": "user", "content": "test"}]})


@pytest.mark.asyncio
async def test_provider_and_model_id_override(mock_model):
    """Test overriding provider and model ID."""
    wrapped = wrap_language_model(
        model=mock_model, 
        middleware=[],
        provider_id="custom-provider",
        model_id="custom-model",
    )
    
    assert wrapped.provider == "custom-provider"
    assert wrapped.model_id == "custom-model"


def test_middleware_factory_resolution():
    """Test that middleware functions are properly resolved."""
    
    def middleware_factory():
        middleware = SimpleMiddleware()
        middleware.transformParams = lambda **kwargs: kwargs["params"]
        return middleware
    
    mock_model = MockLanguageModel()
    
    # Should accept both middleware instances and factory functions
    wrapped = wrap_language_model(
        model=mock_model,
        middleware=[middleware_factory]  # Factory function
    )
    
    assert wrapped is not None