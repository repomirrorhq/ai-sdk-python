"""Comprehensive example demonstrating the AI SDK middleware system.

This example showcases various middleware capabilities including:
- Request/response logging
- Response caching for performance
- Default settings application
- Usage telemetry and monitoring
- Custom middleware creation
- Middleware composition and chaining

Run with: python examples/middleware_example.py
"""

import asyncio
import logging
import os
import time
from typing import Dict, Any

# Configure logging to see middleware output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from ai_sdk import (
    create_openai,
    wrap_language_model,
    logging_middleware,
    caching_middleware,
    default_settings_middleware,
    telemetry_middleware,
)
from ai_sdk.middleware import SimpleMiddleware


async def telemetry_callback(data: Dict[str, Any]):
    """Custom telemetry callback for monitoring."""
    print(f"📊 TELEMETRY: {data['operation']} to {data['model']} - Status: {data['status']}")
    if 'duration_ms' in data:
        print(f"   ⏱️  Duration: {data['duration_ms']}ms")
    if 'total_tokens' in data:
        print(f"   🔢 Tokens: {data['total_tokens']} total ({data['input_tokens']} in, {data['output_tokens']} out)")


def create_custom_safety_middleware():
    """Create a custom middleware that filters unsafe content."""
    
    # Simple word filter for demonstration
    UNSAFE_WORDS = ["bomb", "weapon", "violence", "harm"]
    
    async def transform_params(*, params, type, model):
        """Add safety system message and check user input."""
        messages = list(params.get("messages", []))
        
        # Check for unsafe content in user messages
        for message in messages:
            if message.get("role") == "user":
                content = message.get("content", "").lower()
                if any(word in content for word in UNSAFE_WORDS):
                    print(f"⚠️  SAFETY: Potentially unsafe content detected, adding extra safety instructions")
                    break
        
        # Add safety system message
        safety_message = {
            "role": "system",
            "content": "You are a helpful, harmless, and honest assistant. Never provide information that could be used to cause harm."
        }
        
        # Insert after any existing system message or at the beginning
        if messages and messages[0].get("role") == "system":
            messages.insert(1, safety_message)
        else:
            messages.insert(0, safety_message)
        
        return {**params, "messages": messages}
    
    async def wrap_generate(*, do_generate, params, model):
        """Filter response content for safety."""
        result = await do_generate()
        
        # Simple content filtering
        filtered_text = result.text
        for word in UNSAFE_WORDS:
            if word in filtered_text.lower():
                filtered_text = filtered_text.replace(word, "[FILTERED]")
                print(f"⚠️  SAFETY: Filtered potentially unsafe content from response")
        
        # Return result with filtered text
        return type(result)(
            text=filtered_text,
            usage=result.usage,
            finish_reason=result.finish_reason,
            response_id=result.response_id,
        )
    
    middleware = SimpleMiddleware()
    middleware.transformParams = transform_params
    middleware.wrapGenerate = wrap_generate
    return middleware


async def demonstrate_basic_middleware():
    """Demonstrate basic middleware functionality."""
    print("🔧 DEMONSTRATION: Basic Middleware Functionality")
    print("=" * 60)
    
    # Create OpenAI model
    openai = create_openai(api_key=os.getenv("OPENAI_API_KEY"))
    base_model = openai.chat("gpt-3.5-turbo")
    
    # Wrap with logging middleware
    logged_model = wrap_language_model(
        model=base_model,
        middleware=logging_middleware(
            level="INFO",
            include_params=True,
            include_response=True,
            include_timing=True,
        )
    )
    
    print("📝 Making request with logging middleware:")
    result = await logged_model.generate_text({
        "messages": [{"role": "user", "content": "What is 2+2?"}]
    })
    
    print(f"✅ Response: {result.text}")
    print()


async def demonstrate_caching():
    """Demonstrate response caching middleware."""
    print("💾 DEMONSTRATION: Response Caching")
    print("=" * 60)
    
    openai = create_openai(api_key=os.getenv("OPENAI_API_KEY"))
    base_model = openai.chat("gpt-3.5-turbo")
    
    # Wrap with caching middleware
    cached_model = wrap_language_model(
        model=base_model,
        middleware=caching_middleware(ttl=60)  # 1 minute cache
    )
    
    query = {"messages": [{"role": "user", "content": "What is the capital of France?"}]}
    
    print("🔄 First request (should miss cache):")
    start_time = time.time()
    result1 = await cached_model.generate_text(query)
    duration1 = time.time() - start_time
    print(f"✅ Response: {result1.text}")
    print(f"⏱️  Duration: {duration1:.2f}s")
    
    print("\n🔄 Second request (should hit cache):")
    start_time = time.time()
    result2 = await cached_model.generate_text(query)
    duration2 = time.time() - start_time
    print(f"✅ Response: {result2.text}")
    print(f"⏱️  Duration: {duration2:.2f}s")
    print(f"🚀 Cache speedup: {duration1/duration2:.1f}x faster!")
    print()


async def demonstrate_default_settings():
    """Demonstrate default settings middleware."""
    print("⚙️  DEMONSTRATION: Default Settings")
    print("=" * 60)
    
    openai = create_openai(api_key=os.getenv("OPENAI_API_KEY"))
    base_model = openai.chat("gpt-3.5-turbo")
    
    # Wrap with default settings
    configured_model = wrap_language_model(
        model=base_model,
        middleware=default_settings_middleware(
            default_temperature=0.1,  # More deterministic responses
            default_max_tokens=50,    # Shorter responses
            default_system_message="You are a concise assistant. Keep responses brief.",
        )
    )
    
    print("📋 Making request without specifying temperature, max_tokens, or system message:")
    result = await configured_model.generate_text({
        "messages": [{"role": "user", "content": "Explain artificial intelligence"}]
    })
    
    print(f"✅ Response (should be brief due to defaults): {result.text}")
    print()


async def demonstrate_telemetry():
    """Demonstrate telemetry middleware."""
    print("📊 DEMONSTRATION: Telemetry and Monitoring")
    print("=" * 60)
    
    openai = create_openai(api_key=os.getenv("OPENAI_API_KEY"))
    base_model = openai.chat("gpt-3.5-turbo")
    
    # Wrap with telemetry middleware
    monitored_model = wrap_language_model(
        model=base_model,
        middleware=telemetry_middleware(
            track_requests=True,
            track_tokens=True,
            track_timing=True,
            callback=telemetry_callback,
        )
    )
    
    print("📈 Making request with telemetry tracking:")
    result = await monitored_model.generate_text({
        "messages": [{"role": "user", "content": "Write a haiku about programming"}]
    })
    
    print(f"✅ Response: {result.text}")
    print()


async def demonstrate_custom_middleware():
    """Demonstrate custom safety middleware."""
    print("🛡️  DEMONSTRATION: Custom Safety Middleware")
    print("=" * 60)
    
    openai = create_openai(api_key=os.getenv("OPENAI_API_KEY"))
    base_model = openai.chat("gpt-3.5-turbo")
    
    # Wrap with custom safety middleware
    safe_model = wrap_language_model(
        model=base_model,
        middleware=create_custom_safety_middleware()
    )
    
    print("🔒 Making safe request:")
    result1 = await safe_model.generate_text({
        "messages": [{"role": "user", "content": "How do I bake a cake?"}]
    })
    print(f"✅ Safe response: {result1.text[:100]}...")
    
    print("\n⚠️  Making potentially unsafe request:")
    result2 = await safe_model.generate_text({
        "messages": [{"role": "user", "content": "Tell me about weapons in history"}]
    })
    print(f"🛡️  Filtered response: {result2.text[:100]}...")
    print()


async def demonstrate_middleware_composition():
    """Demonstrate composing multiple middleware together."""
    print("🔗 DEMONSTRATION: Middleware Composition")
    print("=" * 60)
    
    openai = create_openai(api_key=os.getenv("OPENAI_API_KEY"))
    base_model = openai.chat("gpt-3.5-turbo")
    
    # Compose multiple middleware
    enhanced_model = wrap_language_model(
        model=base_model,
        middleware=[
            # Applied in order for parameter transformation
            default_settings_middleware(
                default_temperature=0.7,
                default_system_message="You are a creative writing assistant.",
            ),
            create_custom_safety_middleware(),
            # Applied in reverse order for method wrapping
            logging_middleware(level="INFO", include_timing=True),
            caching_middleware(ttl=30),
            telemetry_middleware(callback=telemetry_callback),
        ]
    )
    
    print("🎯 Making request with full middleware stack:")
    result = await enhanced_model.generate_text({
        "messages": [{"role": "user", "content": "Write a short story about a robot"}]
    })
    
    print(f"✅ Enhanced response: {result.text[:200]}...")
    
    print("\n🔄 Making same request again (should hit cache):")
    result2 = await enhanced_model.generate_text({
        "messages": [{"role": "user", "content": "Write a short story about a robot"}]
    })
    print("✅ Second request completed (check logs for cache hit)")
    print()


async def demonstrate_streaming_middleware():
    """Demonstrate middleware with streaming operations."""
    print("🌊 DEMONSTRATION: Streaming with Middleware")
    print("=" * 60)
    
    openai = create_openai(api_key=os.getenv("OPENAI_API_KEY"))
    base_model = openai.chat("gpt-3.5-turbo")
    
    # Wrap with logging and telemetry for streaming
    streaming_model = wrap_language_model(
        model=base_model,
        middleware=[
            logging_middleware(level="INFO"),
            telemetry_middleware(callback=telemetry_callback),
        ]
    )
    
    print("📡 Starting streaming request with middleware:")
    stream = await streaming_model.stream_text({
        "messages": [{"role": "user", "content": "Count from 1 to 5 slowly"}]
    })
    
    print("🔄 Streaming response:")
    async for chunk in stream:
        if chunk.type == "text-delta":
            print(chunk.text_delta, end="", flush=True)
    
    print("\n✅ Streaming completed")
    print()


async def main():
    """Run all middleware demonstrations."""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY=your_api_key_here")
        return
    
    print("🚀 AI SDK Middleware System Demonstration")
    print("=" * 60)
    print("This example showcases the production-ready middleware system")
    print("for the AI SDK, enabling caching, logging, telemetry, and more!")
    print()
    
    try:
        await demonstrate_basic_middleware()
        await demonstrate_caching()
        await demonstrate_default_settings()
        await demonstrate_telemetry()
        await demonstrate_custom_middleware()
        await demonstrate_middleware_composition()
        await demonstrate_streaming_middleware()
        
        print("🎉 All middleware demonstrations completed successfully!")
        print()
        print("💡 Key Features Demonstrated:")
        print("   • Request/response logging with timing")
        print("   • Intelligent response caching")
        print("   • Default parameter application")
        print("   • Usage telemetry and monitoring")
        print("   • Custom safety middleware")
        print("   • Middleware composition and chaining")
        print("   • Streaming support")
        print()
        print("🏭 Production Benefits:")
        print("   • Cost optimization through caching")
        print("   • Comprehensive observability")
        print("   • Safety guardrails and filtering")
        print("   • Consistent defaults across applications")
        print("   • Modular and reusable components")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())