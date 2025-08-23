"""Basic example of using AI SDK Python with OpenAI."""

import asyncio
import os
from ai_sdk import generate_text
from ai_sdk.providers.openai import OpenAIProvider


async def main():
    """Run a basic text generation example."""
    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Create provider and model
    provider = OpenAIProvider()
    model = provider.language_model("gpt-3.5-turbo")
    
    # Generate text
    print("Generating text...")
    result = await generate_text(
        model,
        prompt="Write a short poem about Python programming",
        max_tokens=100,
        temperature=0.7,
    )
    
    print(f"Generated text:\n{result.text}")
    print(f"Tokens used: {result.usage.total_tokens}")
    print(f"Finish reason: {result.finish_reason}")


if __name__ == "__main__":
    asyncio.run(main())