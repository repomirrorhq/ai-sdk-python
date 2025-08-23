"""
Example usage of Groq provider with AI SDK Python.

This example demonstrates how to use Groq's high-speed inference platform
for text generation and streaming.
"""

import asyncio
import os
from ai_sdk import create_groq
from ai_sdk.core import generate_text, stream_text


async def main():
    """Main example function."""
    
    # Create Groq provider
    # You can set GROQ_API_KEY environment variable or pass api_key directly
    groq = create_groq(
        # api_key="your-groq-api-key-here"  # Optional if GROQ_API_KEY is set
    )
    
    print("🚀 Groq AI SDK Python Example")
    print("=" * 50)
    
    # Example 1: Basic text generation
    print("\n1. Basic Text Generation")
    print("-" * 25)
    
    try:
        result = await generate_text(
            model=groq("llama-3.1-8b-instant"),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What makes Groq's LPU technology special?"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        print(f"Response: {result.content}")
        print(f"Usage: {result.usage}")
        print(f"Finish reason: {result.finish_reason}")
        
    except Exception as e:
        print(f"Error in basic generation: {e}")
    
    print("\n✅ Groq example completed!")


if __name__ == "__main__":
    # Check if API key is available
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  Warning: GROQ_API_KEY environment variable not set.")
        print("   Set it with: export GROQ_API_KEY='your-api-key'")
        print("   Or pass api_key directly to create_groq()")
        print()
    
    # Run the examples
    asyncio.run(main())
