"""
Comprehensive DeepInfra Provider Example for AI SDK Python.

This example demonstrates the key features of the DeepInfra provider:
1. Text generation with 50+ open-source models (Llama, Qwen, Mistral, etc.)
2. Streaming text generation with cost-effective models
3. Tool calling with advanced models
4. Text embeddings with BGE, E5, and Sentence Transformers
5. Image generation with FLUX and Stable Diffusion models
6. Vision capabilities with Llama 3.2 Vision models
7. Code generation with specialized code models
8. Batch processing and cost optimization
9. Error handling and best practices

Prerequisites:
- Install ai-sdk-python: pip install ai-sdk-python[deepinfra]
- Set DEEPINFRA_API_KEY environment variable or pass api_key parameter
"""

import asyncio
import json
import os
from typing import Any, Dict, List

from ai_sdk import generate_text, stream_text, embed, embed_many, generate_image
from ai_sdk.providers.deepinfra import (
    DeepInfraProvider,
    create_deepinfra_provider,
    DeepInfraChatModelId,
    DeepInfraEmbeddingModelId,
    DeepInfraImageModelId,
    DeepInfraProviderSettings
)
from ai_sdk.core.types import ChatPrompt, UserMessage, SystemMessage, ToolMessage
from ai_sdk.tools.core import create_tool


async def basic_text_generation():
    """Demonstrate basic text generation with various DeepInfra models."""
    print("=== Basic Text Generation ===")
    
    # Create provider (uses DEEPINFRA_API_KEY from environment)
    provider = DeepInfraProvider()
    
    # Try different model families
    models_to_try = [
        ("meta-llama/Meta-Llama-3.1-70B-Instruct", "Llama 3.1 70B"),
        ("Qwen/Qwen2.5-72B-Instruct", "Qwen 2.5 72B"),
        ("meta-llama/Llama-3.3-70B-Instruct-Turbo", "Llama 3.3 70B Turbo"),
    ]
    
    prompt = "Explain quantum computing in simple terms, focusing on practical applications."
    
    for model_id, model_name in models_to_try:
        print(f"\n--- {model_name} ---")
        try:
            model = provider.language_model(model_id)
            result = await generate_text(
                model=model,
                prompt=prompt,
                max_output_tokens=200,
                temperature=0.7
            )
            
            print(f"Generated text: {result.text[:200]}...")
            print(f"Usage: {result.usage}")
            print(f"Finish reason: {result.finish_reason}")
            
            if result.provider_metadata and "deepinfra" in result.provider_metadata:
                deepinfra_meta = result.provider_metadata["deepinfra"]
                print(f"Model: {deepinfra_meta.get('model')}")
                print(f"DeepInfra finish reason: {deepinfra_meta.get('finish_reason')}")
                
        except Exception as e:
            print(f"Error with {model_name}: {e}")
            continue


async def streaming_generation():
    """Demonstrate streaming text generation with cost-effective models."""
    print("\n=== Streaming Text Generation ===")
    
    provider = DeepInfraProvider()
    # Use a cost-effective model for streaming
    model = provider.language_model("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
    
    print("Streaming response: ", end="", flush=True)
    
    async for part in stream_text(
        model=model,
        prompt="Write a short story about a robot discovering emotions.",
        max_output_tokens=300,
        temperature=0.8
    ):
        if hasattr(part, 'delta') and part.delta:
            print(part.delta, end="", flush=True)
        elif hasattr(part, 'finish_reason'):
            print(f"\n\nStream finished: {part.finish_reason}")
            if part.usage:
                print(f"Usage: {part.usage}")
            if part.provider_metadata:
                deepinfra_meta = part.provider_metadata.get("deepinfra", {})
                print(f"Model used: {deepinfra_meta.get('model')}")


async def tool_calling_example():
    """Demonstrate tool calling with advanced DeepInfra models."""
    print("\n=== Tool Calling Example ===")
    
    # Define tools
    calculator_tool = create_tool(
        name="calculator",
        description="Perform mathematical calculations",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    )
    
    weather_tool = create_tool(
        name="get_weather",
        description="Get current weather for a location",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name or location"
                },
                "units": {
                    "type": "string", 
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature units"
                }
            },
            "required": ["location"]
        }
    )
    
    provider = DeepInfraProvider()
    model = provider.language_model("meta-llama/Meta-Llama-3.1-70B-Instruct")
    
    result = await generate_text(
        model=model,
        prompt="What's the weather in London and what's 25 * 47 * 12?",
        tools=[calculator_tool, weather_tool],
        max_output_tokens=300
    )
    
    print(f"Response: {result.text}")
    
    if result.tool_calls:
        print(f"Tool calls made: {len(result.tool_calls)}")
        for i, tool_call in enumerate(result.tool_calls):
            print(f"  {i+1}. {tool_call['name']}: {tool_call['arguments']}")


async def vision_model_example():
    """Demonstrate vision capabilities with Llama 3.2 Vision models."""
    print("\n=== Vision Model Example ===")
    
    provider = DeepInfraProvider()
    model = provider.language_model("meta-llama/Llama-3.2-11B-Vision-Instruct")
    
    # Note: In a real implementation, you would pass image data
    # This example shows the text-only interaction pattern
    
    prompt = ChatPrompt(messages=[
        SystemMessage(
            content="You are a helpful assistant that can analyze images and answer questions about them."
        ),
        UserMessage(
            content="If I were to show you an image of a sunset over mountains, what details would you look for to describe it effectively?"
        )
    ])
    
    result = await generate_text(
        model=model,
        prompt=prompt,
        max_output_tokens=300,
        temperature=0.7
    )
    
    print(f"Vision model response: {result.text}")
    
    if result.provider_metadata:
        deepinfra_meta = result.provider_metadata.get("deepinfra", {})
        print(f"Vision model used: {deepinfra_meta.get('model')}")


async def code_generation_example():
    """Demonstrate code generation with specialized code models."""
    print("\n=== Code Generation Example ===")
    
    provider = DeepInfraProvider()
    # Use a specialized code model
    model = provider.language_model("codellama/CodeLlama-70b-Instruct-hf")
    
    code_prompt = """
    Write a Python function that implements a binary search algorithm.
    Include proper error handling and documentation.
    """
    
    result = await generate_text(
        model=model,
        prompt=code_prompt,
        max_output_tokens=500,
        temperature=0.2  # Lower temperature for code generation
    )
    
    print(f"Generated code:\n{result.text}")
    
    # Try with Qwen Coder
    print("\n--- Qwen Coder Model ---")
    qwen_model = provider.language_model("Qwen/Qwen2.5-Coder-32B-Instruct")
    
    qwen_result = await generate_text(
        model=qwen_model,
        prompt="Write a JavaScript async function that fetches data from an API with proper error handling.",
        max_output_tokens=300,
        temperature=0.2
    )
    
    print(f"Qwen Coder result:\n{qwen_result.text}")


async def embedding_examples():
    """Demonstrate text embeddings with various DeepInfra embedding models."""
    print("\n=== Text Embeddings ===")
    
    provider = DeepInfraProvider()
    
    # Try different embedding models
    embedding_models = [
        ("BAAI/bge-large-en-v1.5", "BGE Large (Best Quality)"),
        ("intfloat/multilingual-e5-large", "E5 Large (Multilingual)"),
        ("sentence-transformers/all-mpnet-base-v2", "All-MPNet (Fast)")
    ]
    
    texts = [
        "Machine learning is a subset of artificial intelligence",
        "Deep learning uses neural networks with multiple layers",
        "Natural language processing helps computers understand text"
    ]
    
    for model_id, model_name in embedding_models:
        print(f"\n--- {model_name} ---")
        try:
            embedding_model = provider.embedding_model(model_id)
            
            result = await embed(
                model=embedding_model,
                values=texts
            )
            
            print(f"Generated {len(result.embeddings)} embeddings")
            print(f"Embedding dimensions: {len(result.embeddings[0]) if result.embeddings else 0}")
            print(f"Usage: {result.usage}")
            
            if result.provider_metadata:
                deepinfra_meta = result.provider_metadata.get("deepinfra", {})
                print(f"Model: {deepinfra_meta.get('model')}")
                
        except Exception as e:
            print(f"Error with {model_name}: {e}")
            continue


async def batch_embedding_example():
    """Demonstrate batch embedding processing."""
    print("\n=== Batch Embeddings ===")
    
    provider = DeepInfraProvider()
    embedding_model = provider.embedding_model("BAAI/bge-base-en-v1.5")
    
    # Create a large set of texts for batch processing
    large_texts = [
        f"This is document number {i} about artificial intelligence and machine learning." 
        for i in range(150)
    ]  # More than batch size to test batching
    
    result = await embed_many(
        model=embedding_model,
        values=large_texts
    )
    
    print(f"Batch embedding results:")
    print(f"Generated {len(result.embeddings)} embeddings")
    print(f"Usage: {result.usage}")
    
    if result.provider_metadata:
        deepinfra_meta = result.provider_metadata.get("deepinfra", {})
        print(f"Batch count: {deepinfra_meta.get('batch_count')}")
        print(f"Total texts: {deepinfra_meta.get('total_texts')}")


async def similarity_search_example():
    """Demonstrate semantic similarity search using DeepInfra embeddings."""
    print("\n=== Semantic Similarity Search ===")
    
    provider = DeepInfraProvider()
    embedding_model = provider.embedding_model("BAAI/bge-large-en-v1.5")
    
    # Knowledge base
    documents = [
        "Python is a high-level programming language",
        "Machine learning algorithms can recognize patterns in data",
        "The weather today is sunny and warm", 
        "Neural networks are inspired by biological neurons",
        "JavaScript is used for web development",
        "Deep learning is a subset of machine learning",
        "The stock market fluctuated today",
        "Natural language processing helps computers understand text",
        "FLUX models generate high-quality images from text prompts",
        "DeepInfra provides cost-effective access to AI models"
    ]
    
    # Get embeddings for documents
    doc_embeddings_result = await embed(
        model=embedding_model,
        values=documents
    )
    
    # Query
    query = "Tell me about artificial intelligence and programming"
    query_embedding_result = await embed(
        model=embedding_model,
        values=[query]
    )
    
    # Calculate similarities (simple dot product)
    import numpy as np
    
    doc_embeddings = np.array(doc_embeddings_result.embeddings)
    query_embedding = np.array(query_embedding_result.embeddings[0])
    
    similarities = np.dot(doc_embeddings, query_embedding)
    
    # Sort by similarity
    sorted_indices = np.argsort(similarities)[::-1]
    
    print(f"Query: '{query}'")
    print("Most similar documents:")
    for i, idx in enumerate(sorted_indices[:5]):
        print(f"  {i+1}. (score: {similarities[idx]:.4f}) {documents[idx]}")


async def image_generation_example():
    """Demonstrate image generation with DeepInfra image models."""
    print("\n=== Image Generation ===")
    
    provider = DeepInfraProvider()
    
    # Try different image models
    image_models = [
        ("black-forest-labs/FLUX-1-schnell", "FLUX Schnell (Fast)"),
        ("stabilityai/sd3.5", "Stable Diffusion 3.5")
    ]
    
    prompts = [
        "A futuristic cityscape at sunset with flying cars",
        "A serene mountain lake with reflection of snow-capped peaks"
    ]
    
    for model_id, model_name in image_models:
        print(f"\n--- {model_name} ---")
        try:
            image_model = provider.image_model(model_id)
            
            result = await generate_image(
                model=image_model,
                prompt=prompts[0],  # Use first prompt
                n=1,
                width=1024,
                height=1024
            )
            
            print(f"Generated {len(result.images)} image(s)")
            if result.images:
                print(f"Image format: {result.images[0].format}")
                if result.images[0].data:
                    print(f"Image size: {len(result.images[0].data)} bytes")
                else:
                    print(f"Image URL: {result.images[0].url}")
            
            if result.provider_metadata:
                deepinfra_meta = result.provider_metadata.get("deepinfra", {})
                print(f"Model: {deepinfra_meta.get('model')}")
                print(f"Created: {deepinfra_meta.get('created')}")
                
        except Exception as e:
            print(f"Error with {model_name}: {e}")
            continue


async def cost_optimization_example():
    """Demonstrate cost optimization strategies with DeepInfra."""
    print("\n=== Cost Optimization ===")
    
    provider = DeepInfraProvider()
    
    # Compare different models for cost vs quality
    model_comparison = [
        ("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "Small & Fast"),
        ("meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", "Large & High Quality"),
        ("meta-llama/Llama-3.3-70B-Instruct-Turbo", "Latest & Balanced")
    ]
    
    prompt = "Summarize the benefits of renewable energy in 2 sentences."
    
    for model_id, description in model_comparison:
        print(f"\n--- {description} ({model_id.split('/')[-1]}) ---")
        try:
            model = provider.language_model(model_id)
            
            result = await generate_text(
                model=model,
                prompt=prompt,
                max_output_tokens=100,
                temperature=0.7
            )
            
            print(f"Response: {result.text}")
            print(f"Tokens used: {result.usage.total_tokens if result.usage else 'Unknown'}")
            
        except Exception as e:
            print(f"Error with {description}: {e}")
            continue


async def error_handling_example():
    """Demonstrate error handling and best practices."""
    print("\n=== Error Handling ===")
    
    try:
        # Invalid API key example
        provider = create_deepinfra_provider(api_key="invalid-key")
        model = provider.language_model("meta-llama/Meta-Llama-3.1-8B-Instruct")
        
        result = await generate_text(
            model=model,
            prompt="This will fail",
            max_output_tokens=50
        )
        
    except Exception as e:
        print(f"Expected error with invalid API key: {type(e).__name__}: {e}")
    
    try:
        # Invalid model example
        provider = DeepInfraProvider()
        model = provider.language_model("non-existent/model")
        
        result = await generate_text(
            model=model,
            prompt="This might fail",
            max_output_tokens=50
        )
        
    except Exception as e:
        print(f"Possible error with invalid model: {type(e).__name__}: {e}")


async def provider_info_example():
    """Show provider capabilities and model information."""
    print("\n=== Provider Information ===")
    
    provider = DeepInfraProvider()
    
    # Get provider info
    provider_info = provider.get_provider_info()
    print(f"Provider: {provider_info['name']}")
    print(f"Description: {provider_info['description']}")
    print(f"Capabilities: {', '.join(provider_info['capabilities'])}")
    print(f"API Compatibility: {provider_info['api_compatibility']}")
    print(f"Cost Tier: {provider_info['cost_tier']}")
    
    # Get available models
    models = provider.get_available_models()
    
    print(f"\nLanguage Models (showing top 10):")
    for i, (model_id, info) in enumerate(list(models["language_models"].items())[:10]):
        print(f"  {i+1}. {model_id}")
        print(f"     Family: {info.get('family', 'Unknown')}")
        print(f"     Context: {info.get('context_length', 'Unknown')} tokens")
        print(f"     Tools: {info.get('supports_tools', False)}")
    
    print(f"\nEmbedding Models (showing top 5):")
    for i, (model_id, info) in enumerate(list(models["embedding_models"].items())[:5]):
        print(f"  {i+1}. {model_id}")
        print(f"     Dimensions: {info.get('dimensions', 'Unknown')}")
        print(f"     Languages: {', '.join(info.get('languages', []))}")
    
    print(f"\nImage Models:")
    for i, (model_id, info) in enumerate(models["image_models"].items()):
        print(f"  {i+1}. {model_id}")
        print(f"     Quality: {info.get('quality', 'Unknown')}")
        print(f"     Max Resolution: {info.get('max_resolution', 'Unknown')}")


async def main():
    """Run all examples."""
    print("DeepInfra Provider Examples for AI SDK Python")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("DEEPINFRA_API_KEY")
    if not api_key:
        print("WARNING: DEEPINFRA_API_KEY not found. Some examples may fail.")
        print("Set your API key: export DEEPINFRA_API_KEY='your-api-key'")
        print("Get your API key from: https://deepinfra.com/")
        print()
    
    try:
        await basic_text_generation()
        await streaming_generation()
        await tool_calling_example()
        await vision_model_example()
        await code_generation_example()
        await embedding_examples()
        await batch_embedding_example()
        await similarity_search_example()
        await image_generation_example()
        await cost_optimization_example()
        await error_handling_example()
        await provider_info_example()
        
        print("\n" + "=" * 60)
        print("All DeepInfra examples completed successfully!")
        print("✨ DeepInfra provides cost-effective access to 50+ open-source models!")
        
    except Exception as e:
        print(f"\nExample failed: {type(e).__name__}: {e}")
        print("Check your API key and internet connection.")


if __name__ == "__main__":
    asyncio.run(main())