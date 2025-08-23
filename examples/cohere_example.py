"""
Comprehensive Cohere Provider Example for AI SDK Python.

This example demonstrates the key features of the Cohere provider:
1. Text generation with Command models
2. Streaming text generation
3. Tool calling and function execution
4. Document-aware chat with citations
5. Text embeddings with various input types
6. Batch embedding processing
7. JSON mode for structured outputs
8. Error handling and best practices

Prerequisites:
- Install ai-sdk-python: pip install ai-sdk-python[cohere]
- Set COHERE_API_KEY environment variable or pass api_key parameter
"""

import asyncio
import json
import os
from typing import Any, Dict, List

from ai_sdk import generate_text, stream_text, embed, embed_many
from ai_sdk.providers.cohere import (
    CohereProvider,
    create_cohere_provider,
    CohereChatModelId,
    CohereEmbeddingModelId,
    CohereProviderSettings
)
from ai_sdk.core.types import ChatPrompt, UserMessage, SystemMessage, ToolMessage
from ai_sdk.tools.core import create_tool


async def basic_text_generation():
    """Demonstrate basic text generation with Cohere Command models."""
    print("=== Basic Text Generation ===")
    
    # Create provider (uses COHERE_API_KEY from environment)
    provider = CohereProvider()
    model = provider.language_model("command-r-plus")
    
    # Simple text generation
    result = await generate_text(
        model=model,
        prompt="Write a brief explanation of quantum computing in simple terms.",
        max_output_tokens=200,
        temperature=0.7
    )
    
    print(f"Generated text: {result.text}")
    print(f"Usage: {result.usage}")
    print(f"Finish reason: {result.finish_reason}")
    
    if result.provider_metadata and "cohere" in result.provider_metadata:
        cohere_meta = result.provider_metadata["cohere"]
        print(f"Cohere finish reason: {cohere_meta.get('finish_reason')}")


async def streaming_generation():
    """Demonstrate streaming text generation."""
    print("\n=== Streaming Text Generation ===")
    
    provider = CohereProvider()
    model = provider.language_model("command-r")
    
    print("Streaming response: ", end="", flush=True)
    
    async for part in stream_text(
        model=model,
        prompt="Tell me about the history of artificial intelligence.",
        max_output_tokens=300,
        temperature=0.6
    ):
        if hasattr(part, 'delta') and part.delta:
            print(part.delta, end="", flush=True)
        elif hasattr(part, 'finish_reason'):
            print(f"\n\nStream finished: {part.finish_reason}")
            if part.usage:
                print(f"Usage: {part.usage}")


async def tool_calling_example():
    """Demonstrate tool calling with Cohere models."""
    print("\n=== Tool Calling Example ===")
    
    # Define tools
    get_weather_tool = create_tool(
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
    
    provider = CohereProvider()
    model = provider.language_model("command-r-plus")
    
    result = await generate_text(
        model=model,
        prompt="What's the weather in Paris and what's 25 * 47?",
        tools=[get_weather_tool, calculator_tool],
        max_output_tokens=300
    )
    
    print(f"Response: {result.text}")
    
    if result.tool_calls:
        print(f"Tool calls made: {len(result.tool_calls)}")
        for i, tool_call in enumerate(result.tool_calls):
            print(f"  {i+1}. {tool_call['name']}: {tool_call['arguments']}")


async def document_aware_chat():
    """Demonstrate document-aware chat with citations."""
    print("\n=== Document-Aware Chat ===")
    
    provider = CohereProvider()
    model = provider.language_model("command-r-plus")
    
    # Create a chat prompt with context documents
    prompt = ChatPrompt(messages=[
        SystemMessage(
            content="You are a helpful assistant that answers questions based on provided documents. Always cite your sources."
        ),
        UserMessage(
            content="What are the main benefits of renewable energy according to the documents?"
        )
    ])
    
    # Note: In a real implementation, you would pass documents through the prompt
    # or use Cohere's document feature directly through provider-specific options
    
    result = await generate_text(
        model=model,
        prompt=prompt,
        max_output_tokens=400,
        temperature=0.3
    )
    
    print(f"Response: {result.text}")
    
    if result.provider_metadata and "cohere" in result.provider_metadata:
        cohere_meta = result.provider_metadata["cohere"]
        
        if cohere_meta.get("citations"):
            print("Citations found:")
            for citation in cohere_meta["citations"]:
                print(f"  - Text: '{citation.get('text')}' (chars {citation.get('start')}-{citation.get('end')})")
        
        if cohere_meta.get("documents"):
            print(f"Documents used: {len(cohere_meta['documents'])}")


async def json_mode_example():
    """Demonstrate JSON mode for structured outputs."""
    print("\n=== JSON Mode Example ===")
    
    provider = CohereProvider()
    model = provider.language_model("command-r-plus")
    
    # Define JSON schema
    schema = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "Brief summary of the analysis"
            },
            "sentiment": {
                "type": "string",
                "enum": ["positive", "negative", "neutral"],
                "description": "Overall sentiment"
            },
            "key_points": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key points from the text"
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Confidence score of the analysis"
            }
        },
        "required": ["summary", "sentiment", "key_points", "confidence"]
    }
    
    result = await generate_text(
        model=model,
        prompt="""
        Analyze this customer review:
        "I absolutely love this product! The quality is amazing and it arrived faster than expected. 
        The customer service was also very helpful when I had questions. Highly recommend!"
        """,
        response_format={
            "type": "json",
            "schema": schema
        },
        max_output_tokens=300
    )
    
    print(f"JSON Response: {result.text}")
    
    try:
        parsed_json = json.loads(result.text)
        print(f"Parsed JSON:")
        print(f"  Summary: {parsed_json.get('summary')}")
        print(f"  Sentiment: {parsed_json.get('sentiment')}")
        print(f"  Key points: {parsed_json.get('key_points')}")
        print(f"  Confidence: {parsed_json.get('confidence')}")
    except json.JSONDecodeError:
        print("Failed to parse JSON response")


async def embedding_examples():
    """Demonstrate text embeddings with Cohere models."""
    print("\n=== Text Embeddings ===")
    
    provider = CohereProvider()
    embedding_model = provider.embedding_model("embed-english-v3.0")
    
    # Single embedding
    texts = ["Hello world", "How are you today?", "Machine learning is fascinating"]
    
    result = await embed(
        model=embedding_model,
        values=texts
    )
    
    print(f"Generated {len(result.embeddings)} embeddings")
    print(f"Embedding dimensions: {len(result.embeddings[0]) if result.embeddings else 0}")
    print(f"Usage: {result.usage}")
    
    # Batch embeddings with many texts
    large_texts = [f"This is text number {i}" for i in range(150)]  # More than batch size
    
    batch_result = await embed_many(
        model=embedding_model,
        values=large_texts
    )
    
    print(f"\nBatch embedding results:")
    print(f"Generated {len(batch_result.embeddings)} embeddings")
    print(f"Usage: {batch_result.usage}")
    
    if batch_result.provider_metadata and "cohere" in batch_result.provider_metadata:
        cohere_meta = batch_result.provider_metadata["cohere"]
        print(f"Batch count: {cohere_meta.get('batch_count')}")


async def similarity_search_example():
    """Demonstrate semantic similarity search using embeddings."""
    print("\n=== Semantic Similarity Search ===")
    
    provider = CohereProvider()
    embedding_model = provider.embedding_model("embed-english-v3.0")
    
    # Knowledge base
    documents = [
        "Python is a high-level programming language",
        "Machine learning algorithms can recognize patterns in data",
        "The weather today is sunny and warm", 
        "Neural networks are inspired by biological neurons",
        "JavaScript is used for web development",
        "Deep learning is a subset of machine learning",
        "The stock market fluctuated today",
        "Natural language processing helps computers understand text"
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
    for i, idx in enumerate(sorted_indices[:3]):
        print(f"  {i+1}. (score: {similarities[idx]:.4f}) {documents[idx]}")


async def error_handling_example():
    """Demonstrate error handling and best practices."""
    print("\n=== Error Handling ===")
    
    try:
        # Invalid API key example
        provider = create_cohere_provider(api_key="invalid-key")
        model = provider.language_model("command-r")
        
        result = await generate_text(
            model=model,
            prompt="This will fail",
            max_output_tokens=50
        )
        
    except Exception as e:
        print(f"Expected error with invalid API key: {type(e).__name__}: {e}")
    
    try:
        # Invalid model example
        provider = CohereProvider()
        model = provider.language_model("non-existent-model")
        
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
    
    provider = CohereProvider()
    
    # Get provider info
    provider_info = provider.get_provider_info()
    print(f"Provider: {provider_info['name']}")
    print(f"Description: {provider_info['description']}")
    print(f"Capabilities: {', '.join(provider_info['capabilities'])}")
    
    # Get available models
    models = provider.get_available_models()
    
    print(f"\nAvailable Language Models:")
    for model_id, info in models["language_models"].items():
        print(f"  {model_id}: {info['description']}")
        print(f"    Context: {info.get('context_length', 'Unknown')} tokens")
        print(f"    Tools: {info.get('supports_tools', False)}")
    
    print(f"\nAvailable Embedding Models:")
    for model_id, info in models["embedding_models"].items():
        print(f"  {model_id}: {info['description']}")
        print(f"    Dimensions: {info.get('dimensions', 'Unknown')}")
        print(f"    Languages: {', '.join(info.get('languages', []))}")


async def main():
    """Run all examples."""
    print("Cohere Provider Examples for AI SDK Python")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        print("WARNING: COHERE_API_KEY not found. Some examples may fail.")
        print("Set your API key: export COHERE_API_KEY='your-api-key'")
        print()
    
    try:
        await basic_text_generation()
        await streaming_generation()
        await tool_calling_example()
        await document_aware_chat()
        await json_mode_example()
        await embedding_examples()
        await similarity_search_example()
        await error_handling_example()
        await provider_info_example()
        
        print("\n" + "=" * 50)
        print("All Cohere examples completed successfully!")
        
    except Exception as e:
        print(f"\nExample failed: {type(e).__name__}: {e}")
        print("Check your API key and internet connection.")


if __name__ == "__main__":
    asyncio.run(main())