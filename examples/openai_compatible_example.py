#!/usr/bin/env python3
"""
OpenAI-Compatible Provider Example

This example demonstrates how to use the OpenAI-Compatible provider with:
- Local model servers (Ollama, LMStudio, vLLM)
- Custom OpenAI-compatible APIs  
- Text generation and embedding
- Different authentication methods

Requirements:
- A running OpenAI-compatible server (Ollama, LMStudio, etc.)
- Or access to a third-party OpenAI-compatible API
"""

import asyncio
import os
from ai_sdk import generate_text, stream_text, embed
from ai_sdk.providers.openai_compatible import (
    create_openai_compatible,
    OpenAICompatibleProviderSettings
)


async def main():
    print("=== OpenAI-Compatible Provider Examples ===\n")
    
    # Example 1: Ollama local server
    print("1. Ollama Local Server Example")
    try:
        ollama = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="ollama",
                base_url="http://localhost:11434/v1",
                # No API key needed for local Ollama
            )
        )
        
        result = await generate_text(
            model=ollama.chat_model("llama3.2"),
            prompt="Explain what Ollama is in one sentence.",
            max_tokens=100
        )
        print(f"Ollama response: {result.text}\n")
        
    except Exception as e:
        print(f"Ollama error (server may not be running): {e}\n")
    
    # Example 2: LMStudio local server
    print("2. LMStudio Local Server Example")
    try:
        lmstudio = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="lmstudio", 
                base_url="http://localhost:1234/v1",
                # No API key needed for local LMStudio
            )
        )
        
        result = await generate_text(
            model=lmstudio.chat_model("local-model"),
            prompt="What are the benefits of running models locally?",
            max_tokens=150
        )
        print(f"LMStudio response: {result.text}\n")
        
    except Exception as e:
        print(f"LMStudio error (server may not be running): {e}\n")
    
    # Example 3: vLLM server
    print("3. vLLM Server Example")
    try:
        vllm = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="vllm",
                base_url="http://localhost:8000/v1",
                # vLLM typically doesn't require API keys for local deployment
            )
        )
        
        result = await generate_text(
            model=vllm.chat_model("meta-llama/Llama-2-7b-chat-hf"),
            prompt="Describe vLLM in technical terms.",
            max_tokens=120
        )
        print(f"vLLM response: {result.text}\n")
        
    except Exception as e:
        print(f"vLLM error (server may not be running): {e}\n")
    
    # Example 4: Custom API with authentication
    print("4. Custom OpenAI-Compatible API Example")
    try:
        custom_api = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="custom-api",
                base_url="https://api.example.com/v1",
                api_key=os.getenv("CUSTOM_API_KEY"),
                headers={
                    "X-Custom-Header": "example-value",
                    "User-Agent": "AI-SDK-Python/1.0"
                },
                query_params={
                    "version": "2024-01-01"
                }
            )
        )
        
        if os.getenv("CUSTOM_API_KEY"):
            result = await generate_text(
                model=custom_api.chat_model("custom-model"),
                prompt="Hello from a custom API!",
                max_tokens=80
            )
            print(f"Custom API response: {result.text}\n")
        else:
            print("Skipping custom API (no CUSTOM_API_KEY set)\n")
        
    except Exception as e:
        print(f"Custom API error: {e}\n")
    
    # Example 5: Text completion (legacy format)
    print("5. Text Completion Example (Legacy Format)")
    try:
        # Some providers support the legacy completions endpoint
        provider = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="completion-provider",
                base_url="http://localhost:11434/v1",
            )
        )
        
        completion_model = provider.completion_model("llama3.2")
        
        # Note: This may not work with all providers as many have deprecated completions
        result = await generate_text(
            model=completion_model,
            prompt="The future of AI is",
            max_tokens=60
        )
        print(f"Completion response: {result.text}\n")
        
    except Exception as e:
        print(f"Completion error (endpoint may not be supported): {e}\n")
    
    # Example 6: Embeddings with OpenAI-compatible API
    print("6. Text Embeddings Example")
    try:
        embedding_provider = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="embedding-provider",
                base_url="http://localhost:11434/v1",
            )
        )
        
        embeddings = await embed(
            model=embedding_provider.text_embedding_model("nomic-embed-text"),
            values=[
                "OpenAI-compatible APIs provide flexibility",
                "Local models offer privacy and control", 
                "Self-hosted solutions reduce costs"
            ]
        )
        print(f"Generated {len(embeddings.embeddings)} embeddings")
        print(f"First embedding dimensions: {len(embeddings.embeddings[0])}\n")
        
    except Exception as e:
        print(f"Embeddings error: {e}\n")
    
    # Example 7: Streaming text generation
    print("7. Streaming Text Generation Example")
    try:
        streaming_provider = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="streaming-provider",
                base_url="http://localhost:11434/v1",
            )
        )
        
        print("Streaming response from local model:")
        stream = await stream_text(
            model=streaming_provider.chat_model("llama3.2"),
            prompt="Write a short poem about local AI models:",
            max_tokens=200
        )
        
        async for chunk in stream:
            if chunk.type == "text-delta":
                print(chunk.text_delta, end="", flush=True)
        print("\n")
        
    except Exception as e:
        print(f"Streaming error: {e}\n")
    
    # Example 8: Provider with different model types
    print("8. Multi-Model Provider Example")
    try:
        multi_provider = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="multi-model",
                base_url="http://localhost:11434/v1",
                include_usage=True  # Include token usage in responses
            )
        )
        
        # Different model types for different tasks
        chat_result = await generate_text(
            model=multi_provider.chat_model("llama3.2"),
            prompt="What's 2+2?",
            max_tokens=20
        )
        print(f"Chat model result: {chat_result.text}")
        print(f"Usage: {chat_result.usage}")
        
    except Exception as e:
        print(f"Multi-model error: {e}")
    
    print("\n=== OpenAI-Compatible Provider Examples Complete ===")
    print("\nNotes:")
    print("- Make sure your local servers (Ollama, LMStudio, etc.) are running")
    print("- Adjust model names to match what's available on your server")
    print("- Use 'ollama list' to see available models in Ollama")
    print("- Check server logs for debugging connection issues")


if __name__ == "__main__":
    print("OpenAI-Compatible Provider supports:")
    print("🦙 Ollama - http://localhost:11434/v1")
    print("🎭 LMStudio - http://localhost:1234/v1") 
    print("⚡ vLLM - http://localhost:8000/v1")
    print("🔗 Any OpenAI-compatible API")
    print("")
    
    asyncio.run(main())