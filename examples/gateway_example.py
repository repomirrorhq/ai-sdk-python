#!/usr/bin/env python3
"""
Gateway Provider Example

This example demonstrates how to use the Gateway provider for:
- Model routing and load balancing
- Getting available models and metadata  
- Text generation with language models
- Text embedding generation
- Streaming text generation

Requirements:
- Set AI_GATEWAY_API_KEY environment variable with your Gateway API key
- Or deploy to Vercel with OIDC authentication
"""

import asyncio
import os
from ai_sdk import generate_text, stream_text, embed
from ai_sdk.providers.gateway import (
    GatewayProvider, 
    create_gateway_provider,
    gateway,
    GatewayProviderSettings
)


async def main():
    print("=== Vercel AI Gateway Provider Example ===\n")
    
    # Example 1: Using the default gateway provider
    print("1. Using default gateway provider")
    try:
        result = await generate_text(
            model=gateway.language_model("gpt-4-turbo"),
            prompt="What are the benefits of using AI Gateway for production deployments?"
        )
        print(f"Generated: {result.text}\n")
    except Exception as e:
        print(f"Error with default provider: {e}\n")
    
    # Example 2: Creating a custom Gateway provider with settings
    print("2. Custom Gateway provider with settings")
    try:
        custom_gateway = create_gateway_provider(
            GatewayProviderSettings(
                base_url="https://ai-gateway.vercel.sh/v1/ai",
                headers={"x-custom-header": "example"},
                metadata_cache_refresh_millis=60000  # 1 minute cache
            )
        )
        
        result = await generate_text(
            model=custom_gateway.language_model("claude-3-sonnet-20240229"),
            prompt="Explain model routing in AI Gateway",
            max_tokens=200
        )
        print(f"Generated: {result.text}\n")
    except Exception as e:
        print(f"Error with custom provider: {e}\n")
    
    # Example 3: Get available models
    print("3. Fetching available models from Gateway")
    try:
        metadata = await gateway.get_available_models()
        print(f"Available models: {len(metadata.models)}")
        
        # Show first few models
        for model in metadata.models[:5]:
            print(f"  - {model.id}: {model.name}")
            if model.description:
                print(f"    Description: {model.description}")
            if model.pricing:
                print(f"    Pricing: Input: {model.pricing.input}, Output: {model.pricing.output}")
        print()
    except Exception as e:
        print(f"Error fetching models: {e}\n")
    
    # Example 4: Text embeddings
    print("4. Text embeddings with Gateway")
    try:
        embeddings = await embed(
            model=gateway.text_embedding_model("text-embedding-ada-002"),
            values=[
                "AI Gateway provides model routing and load balancing",
                "It offers caching and analytics for production AI applications",
                "Gateway supports multiple AI providers seamlessly"
            ]
        )
        print(f"Generated {len(embeddings.embeddings)} embeddings")
        print(f"First embedding dimensions: {len(embeddings.embeddings[0])}\n")
    except Exception as e:
        print(f"Error with embeddings: {e}\n")
    
    # Example 5: Streaming text generation
    print("5. Streaming text generation")
    try:
        stream = await stream_text(
            model=gateway.language_model("gpt-3.5-turbo"),
            prompt="List the top 5 advantages of using AI Gateway in bullet points:",
            max_tokens=300
        )
        
        print("Streaming response:")
        async for chunk in stream:
            if chunk.type == "text-delta":
                print(chunk.text_delta, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"Error with streaming: {e}\n")
    
    # Example 6: Tool calling through Gateway
    print("6. Tool calling through Gateway (if supported)")
    try:
        from ai_sdk.tools import tool
        
        @tool("get_weather", "Get weather information for a city")
        def get_weather(city: str) -> str:
            """Get weather for a city (mock implementation)"""
            return f"The weather in {city} is sunny with 22°C"
        
        result = await generate_text(
            model=gateway.language_model("gpt-4-turbo"),
            prompt="What's the weather like in San Francisco?",
            tools=[get_weather],
            max_tokens=100
        )
        
        print(f"Tool result: {result.text}")
        if result.tool_calls:
            print(f"Tool calls made: {len(result.tool_calls)}")
    except ImportError:
        print("Tools not available in this SDK version")
    except Exception as e:
        print(f"Error with tools: {e}")
    
    print("\n=== Gateway Example Complete ===")


if __name__ == "__main__":
    # Check for API key
    api_key = os.getenv("AI_GATEWAY_API_KEY")
    if not api_key:
        print("⚠️  AI_GATEWAY_API_KEY environment variable not set")
        print("   Set it to your Gateway API key or deploy to Vercel with OIDC")
        print("   Example: export AI_GATEWAY_API_KEY=your_key_here\n")
    
    asyncio.run(main())