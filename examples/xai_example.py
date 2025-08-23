"""
xAI Provider Example - Grok Models with Advanced Features

This example demonstrates the xAI provider capabilities including:
- Text generation with Grok models
- Advanced reasoning with transparent thinking
- Search-augmented generation with citations
- Tool calling and multimodal capabilities
"""

import asyncio
import os
from typing import Any, Dict

from ai_sdk import generate_text, stream_text
from ai_sdk.providers.xai import XAIProvider
from ai_sdk.tools import tool


# Initialize xAI provider
xai = XAIProvider(api_key=os.getenv("XAI_API_KEY"))


@tool
def get_weather(location: str) -> str:
    """Get current weather for a location."""
    return f"The weather in {location} is sunny and 72°F"


@tool 
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Search results for '{query}': Latest information available"


async def basic_text_generation():
    """Basic text generation with Grok-4."""
    print("\n=== Basic Text Generation ===")
    
    response = await generate_text(
        model=xai.grok_4(),
        messages=[
            {"role": "user", "content": "Explain quantum computing in simple terms"}
        ],
        max_tokens=200,
        temperature=0.7,
    )
    
    print(f"Response: {response.text}")
    print(f"Finish reason: {response.finish_reason}")
    print(f"Token usage: {response.usage}")


async def reasoning_with_grok_mini():
    """Advanced reasoning with Grok-3-Mini showing transparent thinking."""
    print("\n=== Advanced Reasoning with Grok-3-Mini ===")
    
    response = await generate_text(
        model=xai.grok_3_mini(),
        messages=[
            {
                "role": "user", 
                "content": "Solve this step by step: If a train travels 60 mph for 2.5 hours, then 80 mph for 1.5 hours, what's the total distance?"
            }
        ],
        max_tokens=300,
        provider_options={
            "reasoning_effort": "high"  # Enable high reasoning effort
        }
    )
    
    print(f"Response: {response.text}")
    
    # Show reasoning content if available
    for content in response.content:
        if hasattr(content, 'type') and content.type == 'reasoning':
            print(f"\nReasoning process: {content.text}")
    
    print(f"Usage: {response.usage}")


async def search_augmented_generation():
    """Search-augmented generation with citations."""
    print("\n=== Search-Augmented Generation ===")
    
    response = await generate_text(
        model=xai.grok_3(),
        messages=[
            {
                "role": "user",
                "content": "What are the latest developments in artificial intelligence in 2025?"
            }
        ],
        max_tokens=400,
        provider_options={
            "search_parameters": {
                "mode": "on",  # Force search
                "return_citations": True,
                "from_date": "2025-01-01",
                "max_search_results": 10,
                "sources": [
                    {
                        "type": "web",
                        "country": "US",
                        "safe_search": True
                    },
                    {
                        "type": "news",
                        "country": "US", 
                        "safe_search": True
                    }
                ]
            }
        }
    )
    
    print(f"Response: {response.text}")
    
    # Show citations
    citations = []
    for content in response.content:
        if hasattr(content, 'source_type') and content.source_type == 'url':
            citations.append(content.url)
    
    if citations:
        print("\nCitations:")
        for i, url in enumerate(citations, 1):
            print(f"{i}. {url}")


async def tool_calling_example():
    """Tool calling with Grok models."""
    print("\n=== Tool Calling ===")
    
    response = await generate_text(
        model=xai.grok_4(),
        messages=[
            {
                "role": "user",
                "content": "What's the weather like in San Francisco? Also search for recent AI news."
            }
        ],
        tools=[get_weather, search_web],
        tool_choice="auto",
        max_tokens=300,
    )
    
    print(f"Response: {response.text}")
    
    # Show tool calls
    for content in response.content:
        if hasattr(content, 'tool_name'):
            print(f"Tool called: {content.tool_name}")
            print(f"Input: {content.input}")


async def streaming_example():
    """Streaming text generation with real-time output."""
    print("\n=== Streaming Generation ===")
    
    print("Streaming response: ", end="", flush=True)
    
    async for chunk in stream_text(
        model=xai.grok_3_fast(),
        messages=[
            {
                "role": "user",
                "content": "Write a short poem about artificial intelligence and the future"
            }
        ],
        max_tokens=200,
        temperature=0.8,
    ):
        if chunk.type == "text-delta":
            print(chunk.delta, end="", flush=True)
        elif chunk.type == "finish":
            print(f"\n\nFinish reason: {chunk.finish_reason}")
            print(f"Token usage: {chunk.usage}")


async def multimodal_example():
    """Multimodal example with Grok-2-Vision (if image provided)."""
    print("\n=== Multimodal Vision Example ===")
    
    # Note: This would require an actual image file
    # For demonstration, we'll show the structure
    try:
        response = await generate_text(
            model=xai.grok_2_vision(),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail"},
                        # {"type": "file", "data": open("image.jpg", "rb").read(), "media_type": "image/jpeg"}
                    ]
                }
            ],
            max_tokens=300,
        )
        
        print(f"Vision response: {response.text}")
        
    except Exception as e:
        print(f"Vision example requires an actual image file: {e}")


async def json_mode_example():
    """JSON mode for structured output."""
    print("\n=== JSON Mode Example ===")
    
    response = await generate_text(
        model=xai.grok_4(),
        messages=[
            {
                "role": "user",
                "content": "Analyze the pros and cons of electric vehicles. Return as JSON with 'pros' and 'cons' arrays."
            }
        ],
        response_format={
            "type": "json",
            "schema": {
                "type": "object",
                "properties": {
                    "pros": {"type": "array", "items": {"type": "string"}},
                    "cons": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["pros", "cons"]
            }
        },
        max_tokens=300,
    )
    
    print(f"JSON Response: {response.text}")


async def model_comparison():
    """Compare different Grok model capabilities."""
    print("\n=== Model Comparison ===")
    
    prompt = "Explain the concept of entropy in thermodynamics"
    models = [
        ("Grok-4", xai.grok_4()),
        ("Grok-3", xai.grok_3()),  
        ("Grok-3-Fast", xai.grok_3_fast()),
        ("Grok-3-Mini", xai.grok_3_mini()),
    ]
    
    for model_name, model in models:
        print(f"\n--- {model_name} ---")
        try:
            response = await generate_text(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7,
            )
            
            print(f"Response: {response.text[:200]}...")
            print(f"Tokens: {response.usage.get('total_tokens', 'N/A')}")
            
        except Exception as e:
            print(f"Error with {model_name}: {e}")


async def main():
    """Run all examples."""
    print("🚀 xAI Provider Examples - Grok Models with Advanced Features")
    print("=" * 60)
    
    try:
        await basic_text_generation()
        await reasoning_with_grok_mini()
        await search_augmented_generation()
        await tool_calling_example()
        await streaming_example()
        await multimodal_example()
        await json_mode_example()
        await model_comparison()
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you have set your XAI_API_KEY environment variable")
    
    print("\n✅ xAI examples completed!")


if __name__ == "__main__":
    asyncio.run(main())