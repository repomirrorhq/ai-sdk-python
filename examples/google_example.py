#!/usr/bin/env python3
"""
Google Generative AI provider example for ai-sdk-python.

This example demonstrates how to use Google's Gemini models with the AI SDK.
Set your GOOGLE_GENERATIVE_AI_API_KEY environment variable before running.
"""

import asyncio
import os
from ai_sdk import create_google, generate_text, stream_text


async def main():
    """Main example function demonstrating Google Generative AI integration."""
    # Check for API key
    api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    if not api_key:
        print("⚠️  Set GOOGLE_GENERATIVE_AI_API_KEY environment variable to run this example")
        return
    
    print("🤖 Google Generative AI Provider Example\n")
    
    # Create Google provider
    google = create_google(api_key=api_key)
    
    # Available models
    models_to_test = [
        "gemini-1.5-flash",      # Fast, efficient model
        "gemini-1.5-pro",       # High-quality model
        "gemini-2.0-flash",     # Latest fast model
    ]
    
    print("📋 Available Google models:")
    for model_id, description in google.supported_models.items():
        print(f"   • {model_id}: {description}")
    print()
    
    # Example 1: Basic text generation
    print("=" * 60)
    print("1. Basic Text Generation with Gemini 1.5 Flash")
    print("=" * 60)
    
    model = google.language_model("gemini-1.5-flash")
    
    result = await generate_text(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Explain quantum computing in simple terms."
            }
        ],
        max_tokens=150,
        temperature=0.7,
    )
    
    print(f"Generated text: {result.text}")
    print(f"Usage: {result.usage}")
    print(f"Finish reason: {result.finish_reason}")
    print()
    
    # Example 2: Streaming text generation
    print("=" * 60)
    print("2. Streaming Text Generation")
    print("=" * 60)
    
    print("Question: What are the main benefits of renewable energy?")
    print("Streaming response:")
    
    stream = stream_text(
        model=model,
        messages=[
            {
                "role": "user", 
                "content": "What are the main benefits of renewable energy? Please list 5 key advantages."
            }
        ],
        max_tokens=200,
        temperature=0.8,
    )
    
    async for chunk in stream:
        for part in chunk.stream_parts:
            if part.type == "text-delta":
                print(part.text_delta, end="", flush=True)
    print("\n")
    
    # Example 3: System instructions with Gemini
    print("=" * 60)
    print("3. System Instructions with Google")
    print("=" * 60)
    
    result = await generate_text(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful coding assistant. Always provide concise, practical examples."
            },
            {
                "role": "user", 
                "content": "How do I create a simple HTTP server in Python?"
            }
        ],
        max_tokens=200,
    )
    
    print(f"Response with system instruction: {result.text}")
    print()
    
    # Example 4: Multi-turn conversation
    print("=" * 60)
    print("4. Multi-turn Conversation")  
    print("=" * 60)
    
    conversation = [
        {"role": "user", "content": "What's the capital of France?"},
        {"role": "assistant", "content": "The capital of France is Paris."},
        {"role": "user", "content": "What's the population of that city?"},
    ]
    
    result = await generate_text(
        model=model,
        messages=conversation,
        max_tokens=100,
    )
    
    print("Conversation:")
    for msg in conversation[:-1]:  # Don't show the last user message twice
        print(f"  {msg['role']}: {msg['content']}")
    print(f"  user: {conversation[-1]['content']}")
    print(f"  assistant: {result.text}")
    print()
    
    # Example 5: Different models comparison
    print("=" * 60)
    print("5. Model Comparison")
    print("=" * 60)
    
    prompt = "Write a haiku about artificial intelligence."
    
    for model_id in ["gemini-1.5-flash", "gemini-1.5-pro"][:2]:  # Test first 2 models
        try:
            model = google.language_model(model_id)
            result = await generate_text(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.9,
            )
            
            print(f"{model_id}:")
            print(f"  {result.text}")
            print(f"  Tokens: {result.usage.total_tokens}")
            print()
            
        except Exception as e:
            print(f"  ❌ Error with {model_id}: {str(e)}")
            print()
    
    # Example 6: Advanced parameters
    print("=" * 60)  
    print("6. Advanced Generation Parameters")
    print("=" * 60)
    
    result = await generate_text(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Generate a creative story about a robot who loves to paint. Make it exactly 3 sentences."
            }
        ],
        max_tokens=100,
        temperature=0.9,       # High creativity
        top_p=0.9,            # Nucleus sampling 
        stop=["The End", "END"],  # Stop sequences
    )
    
    print(f"Creative story (temp=0.9): {result.text}")
    print(f"Usage: {result.usage}")
    print()
    
    print("✅ Google Generative AI provider example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())