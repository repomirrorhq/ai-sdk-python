#!/usr/bin/env python3
"""
Groq Service Tier Example

This example demonstrates how to use Groq's service tiers for different
request prioritization and throughput needs.

Service Tiers:
- 'on_demand': Default tier with consistent performance and fairness (default)
- 'flex': Higher throughput tier (10x rate limits) optimized for workloads that can handle occasional request failures
- 'auto': Uses on_demand rate limits first, then falls back to flex tier if exceeded

Requirements:
- Set GROQ_API_KEY environment variable
"""

import asyncio
import os
from ai_sdk import generate_text, stream_text
from ai_sdk.providers.groq import create_groq, GroqProviderOptions


async def main():
    print("=== Groq Service Tier Example ===\n")
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  GROQ_API_KEY environment variable not set")
        print("   Set it to your Groq API key")
        print("   Example: export GROQ_API_KEY=your_key_here\n")
        return
    
    # Create Groq provider
    groq = create_groq()
    
    # Example 1: Default on_demand service tier
    print("1. Default service tier (on_demand)")
    try:
        result = await generate_text(
            model=groq.language_model("llama-3.1-8b-instant"),
            prompt="What are the benefits of using different service tiers?",
            max_tokens=150
        )
        print(f"Generated: {result.text}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 2: Flex service tier for higher throughput
    print("2. Using flex service tier for higher throughput")
    try:
        result = await generate_text(
            model=groq.language_model("llama-3.1-8b-instant"),
            prompt="Explain the benefits of flex tier processing",
            max_tokens=150,
            provider_options={
                "service_tier": "flex"
            }
        )
        print(f"Generated: {result.text}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 3: Auto service tier (fallback behavior)
    print("3. Using auto service tier")
    try:
        result = await generate_text(
            model=groq.language_model("llama-3.1-8b-instant"),
            prompt="What happens with auto service tier configuration?",
            max_tokens=150,
            provider_options={
                "service_tier": "auto"
            }
        )
        print(f"Generated: {result.text}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 4: Streaming with flex tier
    print("4. Streaming with flex service tier")
    try:
        stream = await stream_text(
            model=groq.language_model("gemma2-9b-it"),
            prompt="List the advantages of high-throughput AI processing:",
            max_tokens=200,
            provider_options={
                "service_tier": "flex"
            }
        )
        
        print("Streaming response with flex tier:")
        async for chunk in stream:
            if chunk.type == "text-delta":
                print(chunk.text_delta, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"Error with streaming: {e}\n")
    
    # Example 5: Combining service tier with other provider options
    print("5. Service tier with other Groq-specific options")
    try:
        result = await generate_text(
            model=groq.language_model("llama-3.1-8b-instant"),
            prompt="Generate a structured response about AI processing tiers",
            max_tokens=150,
            provider_options={
                "service_tier": "flex",
                "user": "example-user-123",
                "structured_outputs": True
            },
            response_format={"type": "json"}
        )
        print(f"Generated JSON: {result.text}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    print("=== Service Tier Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())