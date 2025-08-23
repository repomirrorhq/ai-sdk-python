#!/usr/bin/env python3
"""Comprehensive Groq AI provider usage examples.

This example demonstrates various capabilities of the Groq provider
including text generation, streaming, and working with different models.

Groq provides extremely fast inference for popular open-source models
including LLaMA, Mixtral, and Gemma families.

Setup:
    Set your Groq API key as an environment variable:
    export GROQ_API_KEY="your-groq-api-key"
    
    Or install the ai-sdk package:
    pip install ai-sdk
"""

import asyncio
import os
from ai_sdk import create_groq, generate_text, stream_text


async def example_1_basic_text_generation():
    """Example 1: Basic text generation with Groq."""
    print("\n=== Example 1: Basic Text Generation ===")
    
    # Create Groq provider
    groq = create_groq()
    
    # Generate text using LLaMA 3.1 8B (fastest model)
    result = await generate_text(
        model=groq.language_model("llama-3.1-8b-instant"),
        prompt="Explain the advantages of using Groq for AI inference in 2-3 sentences."
    )
    
    print(f"Generated text: {result.text}")
    print(f"Usage: {result.usage.total_tokens} tokens ({result.usage.prompt_tokens} prompt + {result.usage.completion_tokens} completion)")


async def example_2_streaming_text():
    """Example 2: Real-time streaming text generation."""
    print("\n=== Example 2: Streaming Text Generation ===")
    
    groq = create_groq()
    
    print("Streaming response: ", end="", flush=True)
    
    async for chunk in stream_text(
        model=groq.language_model("llama-3.3-70b-versatile"),
        prompt="Write a haiku about quantum computing.",
        max_tokens=100
    ):
        if chunk.text_delta:
            print(chunk.text_delta, end="", flush=True)
    
    print()  # New line after streaming


async def example_3_advanced_parameters():
    """Example 3: Using advanced generation parameters."""
    print("\n=== Example 3: Advanced Parameters ===")
    
    groq = create_groq()
    
    result = await generate_text(
        model=groq.language_model("mixtral-8x7b-32768"),
        prompt="Create a creative story opening about a time traveler.",
        max_tokens=150,
        temperature=0.8,  # More creative
        top_p=0.9,
        frequency_penalty=0.3,
        presence_penalty=0.2,
        stop_sequences=["The End", "END"]
    )
    
    print(f"Creative story: {result.text}")
    print(f"Finish reason: {result.finish_reason}")


async def example_4_conversation_context():
    """Example 4: Multi-turn conversation with context."""
    print("\n=== Example 4: Conversation Context ===")
    
    groq = create_groq()
    
    # Create conversation with system message and history
    from ai_sdk.providers.types import Message
    
    messages = [
        Message(role="system", content="You are a helpful AI assistant specialized in explaining complex topics simply."),
        Message(role="user", content="What is machine learning?"),
        Message(role="assistant", content="Machine learning is a subset of AI where computers learn patterns from data without explicit programming. Think of it like teaching a computer to recognize patterns the same way humans learn from experience."),
        Message(role="user", content="How does it relate to neural networks?")
    ]
    
    result = await generate_text(
        model=groq.language_model("llama-3.1-8b-instant"),
        messages=messages,
        max_tokens=200,
        temperature=0.7
    )
    
    print(f"AI Assistant: {result.text}")


async def example_5_model_comparison():
    """Example 5: Compare different Groq models."""
    print("\n=== Example 5: Model Comparison ===")
    
    groq = create_groq()
    
    prompt = "Explain photosynthesis in exactly one sentence."
    
    models_to_test = [
        "llama-3.1-8b-instant",      # Fastest
        "llama-3.3-70b-versatile",   # Most capable
        "gemma2-9b-it",              # Google's model
        "qwen-2.5-32b"               # Alibaba's model
    ]
    
    for model_id in models_to_test:
        try:
            result = await generate_text(
                model=groq.language_model(model_id),
                prompt=prompt,
                max_tokens=100,
                temperature=0.3
            )
            
            print(f"\n{model_id}:")
            print(f"Response: {result.text}")
            print(f"Tokens: {result.usage.total_tokens}")
            
        except Exception as e:
            print(f"\n{model_id}: Error - {e}")


async def example_6_error_handling():
    """Example 6: Comprehensive error handling."""
    print("\n=== Example 6: Error Handling ===")
    
    groq = create_groq()
    
    # Test various error conditions
    test_cases = [
        {
            "name": "Invalid model",
            "model": "non-existent-model",
            "prompt": "Test prompt"
        },
        {
            "name": "Too many tokens", 
            "model": "llama-3.1-8b-instant",
            "prompt": "Write a very long essay" * 1000,
            "max_tokens": 100000
        },
        {
            "name": "Empty prompt",
            "model": "llama-3.1-8b-instant", 
            "prompt": ""
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        try:
            result = await generate_text(
                model=groq.language_model(test['model']),
                prompt=test['prompt'],
                max_tokens=test.get('max_tokens', 50)
            )
            print(f"Success: {result.text[:100]}...")
        except Exception as e:
            print(f"Expected error: {type(e).__name__} - {e}")


async def example_7_high_speed_inference():
    """Example 7: Demonstrate Groq's high-speed inference."""
    print("\n=== Example 7: High-Speed Inference Benchmark ===")
    
    groq = create_groq()
    
    import time
    
    prompt = "List 10 interesting facts about space exploration."
    
    print("Testing inference speed with llama-3.1-8b-instant...")
    
    start_time = time.time()
    result = await generate_text(
        model=groq.language_model("llama-3.1-8b-instant"),
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    end_time = time.time()
    
    duration = end_time - start_time
    tokens_per_second = result.usage.completion_tokens / duration
    
    print(f"Generated {result.usage.completion_tokens} tokens in {duration:.2f} seconds")
    print(f"Speed: {tokens_per_second:.1f} tokens/second")
    print(f"\nGenerated content preview: {result.text[:200]}...")


async def example_8_streaming_with_usage():
    """Example 8: Streaming with token usage tracking."""
    print("\n=== Example 8: Streaming with Usage Tracking ===")
    
    groq = create_groq()
    
    print("Streaming with usage tracking: ", end="", flush=True)
    
    total_tokens = 0
    completion_tokens = 0
    
    async for chunk in stream_text(
        model=groq.language_model("llama-3.1-8b-instant"),
        prompt="Describe the future of renewable energy in 3 paragraphs.",
        max_tokens=200,
        temperature=0.6
    ):
        if chunk.text_delta:
            print(chunk.text_delta, end="", flush=True)
            
        if chunk.usage:
            total_tokens = chunk.usage.total_tokens
            completion_tokens = chunk.usage.completion_tokens
    
    print(f"\n\nFinal usage: {completion_tokens} completion tokens, {total_tokens} total tokens")


async def main():
    """Run all Groq examples."""
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Please set your GROQ_API_KEY environment variable")
        print("You can get a free API key at: https://console.groq.com/keys")
        print("\nExample:")
        print("export GROQ_API_KEY='your-groq-api-key-here'")
        return
    
    print("🚀 Groq AI Provider Examples")
    print("=" * 50)
    
    examples = [
        example_1_basic_text_generation,
        example_2_streaming_text,
        example_3_advanced_parameters,
        example_4_conversation_context,
        example_5_model_comparison,
        example_6_error_handling,
        example_7_high_speed_inference,
        example_8_streaming_with_usage
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            await example_func()
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Interrupted at example {i}")
            break
        except Exception as e:
            print(f"\n❌ Example {i} failed: {e}")
    
    print("\n✅ Groq examples completed!")
    print("\nGroq provides extremely fast inference speeds, making it ideal for:")
    print("• Real-time applications requiring low latency")
    print("• High-throughput batch processing")
    print("• Interactive AI assistants and chatbots")
    print("• Development and testing with quick feedback loops")


if __name__ == "__main__":
    asyncio.run(main())