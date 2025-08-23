"""Basic test to validate middleware system functionality."""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_sdk.middleware import (
    wrap_language_model,
    logging_middleware,
    caching_middleware,
    default_settings_middleware,
)
from ai_sdk.middleware.base import SimpleMiddleware
from ai_sdk.middleware.types import GenerateTextResult
from ai_sdk.providers.types import Usage, FinishReason


class MockLanguageModel:
    """Mock language model for testing."""
    
    def __init__(self, provider="test", model_id="test-model"):
        self.provider = provider
        self.model_id = model_id
        self.call_count = 0
    
    async def generate_text(self, params: dict) -> GenerateTextResult:
        """Mock generate text implementation."""
        self.call_count += 1
        print(f"Mock model called with: {params}")
        return GenerateTextResult(
            text=f"Mock response #{self.call_count}",
            usage=Usage(prompt_tokens=10, completion_tokens=15, total_tokens=25),
            finish_reason=FinishReason.STOP,
            response_id=f"test-{self.call_count}",
        )


async def test_basic_wrapping():
    """Test basic middleware wrapping functionality."""
    print("🧪 Testing basic middleware wrapping...")
    
    mock_model = MockLanguageModel()
    wrapped = wrap_language_model(model=mock_model, middleware=[])
    
    # Test basic properties
    assert wrapped.provider == "test"
    assert wrapped.model_id == "test-model"
    print("✅ Provider and model ID preserved")
    
    # Test generation
    result = await wrapped.generate_text({"messages": [{"role": "user", "content": "test"}]})
    assert result.text == "Mock response #1"
    print("✅ Basic generation works")


async def test_parameter_transformation():
    """Test parameter transformation middleware."""
    print("\n🧪 Testing parameter transformation...")
    
    mock_model = MockLanguageModel()
    
    # Create middleware that adds system message
    async def transform_params(*, params, type, model):
        messages = list(params.get("messages", []))
        messages.insert(0, {"role": "system", "content": "You are helpful."})
        return {**params, "messages": messages, "temperature": 0.7}
    
    middleware = SimpleMiddleware()
    middleware.transformParams = transform_params
    
    wrapped = wrap_language_model(model=mock_model, middleware=[middleware])
    
    # Capture params by overriding the mock
    captured_params = None
    original_generate = mock_model.generate_text
    
    async def capture_generate(params):
        nonlocal captured_params
        captured_params = params
        return await original_generate(params)
    
    mock_model.generate_text = capture_generate
    
    # Make request
    await wrapped.generate_text({"messages": [{"role": "user", "content": "Hello"}]})
    
    # Verify transformation
    assert len(captured_params["messages"]) == 2
    assert captured_params["messages"][0]["role"] == "system"
    assert captured_params["temperature"] == 0.7
    print("✅ Parameter transformation works")


async def test_response_wrapping():
    """Test response wrapping middleware."""
    print("\n🧪 Testing response wrapping...")
    
    mock_model = MockLanguageModel()
    
    # Create middleware that modifies response
    async def wrap_generate(*, do_generate, params, model):
        result = await do_generate()
        return GenerateTextResult(
            text=f"WRAPPED: {result.text}",
            usage=result.usage,
            finish_reason=result.finish_reason,
            response_id=result.response_id,
        )
    
    middleware = SimpleMiddleware()
    middleware.wrapGenerate = wrap_generate
    
    wrapped = wrap_language_model(model=mock_model, middleware=[middleware])
    
    result = await wrapped.generate_text({"messages": [{"role": "user", "content": "test"}]})
    assert result.text.startswith("WRAPPED: Mock response")
    print("✅ Response wrapping works")


async def test_middleware_composition():
    """Test composing multiple middleware."""
    print("\n🧪 Testing middleware composition...")
    
    mock_model = MockLanguageModel()
    
    # First middleware adds system message
    async def transform1(*, params, type, model):
        messages = list(params.get("messages", []))
        messages.insert(0, {"role": "system", "content": "System 1"})
        return {**params, "messages": messages}
    
    # Second middleware adds another system message
    async def transform2(*, params, type, model):
        messages = list(params.get("messages", []))
        messages.insert(0, {"role": "system", "content": "System 2"})
        return {**params, "messages": messages}
    
    # Third middleware wraps response
    async def wrap_response(*, do_generate, params, model):
        result = await do_generate()
        return GenerateTextResult(
            text=f"[FINAL: {result.text}]",
            usage=result.usage,
            finish_reason=result.finish_reason,
            response_id=result.response_id,
        )
    
    middleware1 = SimpleMiddleware()
    middleware1.transformParams = transform1
    
    middleware2 = SimpleMiddleware()
    middleware2.transformParams = transform2
    
    middleware3 = SimpleMiddleware()
    middleware3.wrapGenerate = wrap_response
    
    wrapped = wrap_language_model(
        model=mock_model, 
        middleware=[middleware1, middleware2, middleware3]
    )
    
    # Capture final params
    captured_params = None
    original_generate = mock_model.generate_text
    
    async def capture_generate(params):
        nonlocal captured_params
        captured_params = params
        return await original_generate(params)
    
    mock_model.generate_text = capture_generate
    
    result = await wrapped.generate_text({"messages": [{"role": "user", "content": "Hello"}]})
    
    # Should have both system messages (applied in order)
    assert len(captured_params["messages"]) == 3
    assert captured_params["messages"][0]["content"] == "System 1"  # First middleware
    assert captured_params["messages"][1]["content"] == "System 2"  # Second middleware
    assert captured_params["messages"][2]["content"] == "Hello"     # Original user message
    
    # Response should be wrapped
    assert result.text.startswith("[FINAL: Mock response")
    
    print("✅ Middleware composition works correctly")


async def test_built_in_middleware():
    """Test built-in middleware functions."""
    print("\n🧪 Testing built-in middleware...")
    
    mock_model = MockLanguageModel()
    
    # Test default settings middleware
    default_middleware = default_settings_middleware(
        default_temperature=0.5,
        default_system_message="You are a test assistant."
    )
    
    wrapped = wrap_language_model(model=mock_model, middleware=[default_middleware])
    
    # Capture params
    captured_params = None
    original_generate = mock_model.generate_text
    
    async def capture_generate(params):
        nonlocal captured_params
        captured_params = params
        return await original_generate(params)
    
    mock_model.generate_text = capture_generate
    
    await wrapped.generate_text({"messages": [{"role": "user", "content": "Hello"}]})
    
    # Should have applied defaults
    assert captured_params["temperature"] == 0.5
    assert captured_params["messages"][0]["role"] == "system"
    assert captured_params["messages"][0]["content"] == "You are a test assistant."
    
    print("✅ Built-in default settings middleware works")


async def test_caching_middleware():
    """Test caching middleware."""
    print("\n🧪 Testing caching middleware...")
    
    mock_model = MockLanguageModel()
    
    # Create caching middleware with custom cache
    cache_store = {}
    cache_middleware = caching_middleware(ttl=60, cache_store=cache_store)
    
    wrapped = wrap_language_model(model=mock_model, middleware=[cache_middleware])
    
    params = {"messages": [{"role": "user", "content": "What is 2+2?"}]}
    
    # First call - should execute and cache
    result1 = await wrapped.generate_text(params)
    assert mock_model.call_count == 1
    assert len(cache_store) == 1
    print("✅ First call cached")
    
    # Second call - should hit cache
    result2 = await wrapped.generate_text(params)
    assert mock_model.call_count == 1  # Should not have called model again
    assert result1.text == result2.text
    print("✅ Second call hit cache")
    
    # Different params - should execute again
    different_params = {"messages": [{"role": "user", "content": "What is 3+3?"}]}
    result3 = await wrapped.generate_text(different_params)
    assert mock_model.call_count == 2
    print("✅ Different params bypass cache correctly")


async def main():
    """Run all tests."""
    print("🚀 Running AI SDK Middleware System Tests")
    print("=" * 50)
    
    try:
        await test_basic_wrapping()
        await test_parameter_transformation()
        await test_response_wrapping()
        await test_middleware_composition()
        await test_built_in_middleware()
        await test_caching_middleware()
        
        print("\n🎉 All tests passed successfully!")
        print("✅ Middleware system is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)