"""Mistral AI provider example for AI SDK Python.

This example demonstrates how to use Mistral AI models with the AI SDK Python,
showcasing various model families and capabilities.

Requirements:
- pip install 'ai-sdk'
- Set MISTRAL_API_KEY environment variable
"""

import asyncio
import os
from ai_sdk import generate_text, stream_text
from ai_sdk.providers.mistral import create_mistral, MistralProviderSettings


async def basic_mistral_example():
    """Basic text generation with Mistral Large."""
    
    print("🚀 Basic Mistral Example")
    print("=" * 50)
    
    mistral = create_mistral()
    model = await mistral.language_model("mistral-large-latest")
    
    try:
        result = await generate_text(
            model=model,
            prompt="Explain quantum computing in simple terms.",
            max_tokens=150
        )
        
        print(f"Model: mistral-large-latest")
        print(f"Response: {result['content']}")
        print(f"Tokens used: {result.get('usage', {})}")
        
    except Exception as e:
        print(f"Error: {e}")


async def small_models_example():
    """Example with efficient small models."""
    
    print("\n⚡ Small Models Example")
    print("=" * 50)
    
    mistral = create_mistral()
    
    small_models = [
        ("ministral-3b-latest", "Ministral 3B"),
        ("ministral-8b-latest", "Ministral 8B"),
        ("mistral-small-latest", "Mistral Small"),
    ]
    
    prompt = "Write a one-sentence summary of machine learning."
    
    for model_id, model_name in small_models:
        try:
            print(f"\n{model_name} ({model_id}):")
            
            model = await mistral.language_model(model_id)
            result = await generate_text(
                model=model,
                prompt=prompt,
                max_tokens=50,
                temperature=0.3
            )
            
            print(f"Response: {result['content']}")
            print(f"Tokens: {result.get('usage', {}).get('total_tokens', 'N/A')}")
            
        except Exception as e:
            print(f"Error with {model_name}: {e}")


async def reasoning_models_example():
    """Example with Magistral reasoning models."""
    
    print("\n🧠 Reasoning Models Example")
    print("=" * 50)
    
    mistral = create_mistral()
    
    reasoning_models = [
        "magistral-small-2507",
        "magistral-medium-2507",
    ]
    
    complex_prompt = """
    Solve this step by step:
    If a train travels 120 km in 2 hours, and then travels another 180 km in 3 hours,
    what is the average speed for the entire journey?
    """
    
    for model_id in reasoning_models:
        try:
            print(f"\nModel: {model_id}")
            
            model = await mistral.language_model(model_id)
            result = await generate_text(
                model=model,
                prompt=complex_prompt,
                max_tokens=200,
                temperature=0.1
            )
            
            print(f"Response: {result['content']}")
            
        except Exception as e:
            print(f"Error with {model_id}: {e}")


async def streaming_example():
    """Example of streaming responses."""
    
    print("\n🌊 Streaming Example")
    print("=" * 50)
    
    mistral = create_mistral()
    model = await mistral.language_model("mistral-large-latest")
    
    try:
        print("Streaming response:")
        stream = await stream_text(
            model=model,
            prompt="Write a creative short story about a robot chef.",
            max_tokens=300,
            temperature=0.8
        )
        
        async for chunk in stream:
            if chunk.get("type") == "content_delta":
                print(chunk["delta"]["text"], end="", flush=True)
            elif chunk.get("type") == "done":
                print(f"\n\nFinished. Usage: {chunk.get('usage', {})}")
                
    except Exception as e:
        print(f"Error: {e}")


async def tool_calling_example():
    """Example of tool calling with Mistral."""
    
    print("\n🔧 Tool Calling Example")
    print("=" * 50)
    
    mistral = create_mistral()
    model = await mistral.language_model("mistral-large-latest")
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate_area",
                "description": "Calculate the area of a rectangle",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "length": {
                            "type": "number",
                            "description": "The length of the rectangle"
                        },
                        "width": {
                            "type": "number", 
                            "description": "The width of the rectangle"
                        }
                    },
                    "required": ["length", "width"]
                }
            }
        }
    ]
    
    try:
        result = await generate_text(
            model=model,
            prompt="Calculate the area of a rectangle that is 5 meters long and 3 meters wide.",
            tools=tools,
            max_tokens=200
        )
        
        print(f"Response: {result['content']}")
        if result.get('tool_calls'):
            print(f"Tool calls: {result['tool_calls']}")
            
    except Exception as e:
        print(f"Error: {e}")


async def custom_settings_example():
    """Example with custom provider settings."""
    
    print("\n⚙️  Custom Settings Example")
    print("=" * 50)
    
    # Custom settings with safety prompt
    settings = MistralProviderSettings(
        api_key=os.getenv("MISTRAL_API_KEY"),
        timeout=30,
        headers={"User-Agent": "ai-sdk-python-example"}
    )
    
    mistral = create_mistral(settings)
    model = await mistral.language_model("mistral-large-latest")
    
    try:
        result = await generate_text(
            model=model,
            prompt="Tell me about artificial intelligence.",
            max_tokens=100,
            temperature=0.7,
            provider_options={
                "safe_prompt": True  # Enable safety prompt
            }
        )
        
        print(f"Response with safety prompt: {result['content']}")
        
    except Exception as e:
        print(f"Error: {e}")


async def open_source_models_example():
    """Example with open source Mistral models."""
    
    print("\n🌐 Open Source Models Example")
    print("=" * 50)
    
    mistral = create_mistral()
    
    open_models = [
        ("open-mistral-7b", "Mistral 7B"),
        ("open-mixtral-8x7b", "Mixtral 8x7B"),
        ("open-mixtral-8x22b", "Mixtral 8x22B"),
    ]
    
    prompt = "What are the advantages of open source AI models?"
    
    for model_id, model_name in open_models:
        try:
            print(f"\n{model_name} ({model_id}):")
            
            model = await mistral.language_model(model_id)
            result = await generate_text(
                model=model,
                prompt=prompt,
                max_tokens=100,
                temperature=0.5
            )
            
            print(f"Response: {result['content'][:200]}...")  # Truncate for display
            
        except Exception as e:
            print(f"Error with {model_name}: {e}")


async def main():
    """Run all Mistral examples."""
    print("🏗️  Mistral AI Provider Examples")
    print("=" * 50)
    print("Testing Mistral AI integration with AI SDK Python")
    print()
    
    # Check if API key is available
    if not os.getenv("MISTRAL_API_KEY"):
        print("⚠️  No Mistral API key found!")
        print("Please set the MISTRAL_API_KEY environment variable.")
        print("Get your API key from: https://console.mistral.ai/")
        return
    
    try:
        await basic_mistral_example()
        await small_models_example() 
        await reasoning_models_example()
        await streaming_example()
        await tool_calling_example()
        await custom_settings_example()
        await open_source_models_example()
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
    
    print("\n🎉 Mistral examples completed!")


if __name__ == "__main__":
    asyncio.run(main())