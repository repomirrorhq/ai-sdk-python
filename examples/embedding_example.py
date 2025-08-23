"""Example demonstrating embedding functionality with AI SDK Python."""

import asyncio
import os

from ai_sdk import embed, embed_many, cosine_similarity
from ai_sdk.providers.openai import OpenAIProvider


async def main():
    """Demonstrate embedding functionality."""
    
    # Initialize the OpenAI provider
    # Note: Set OPENAI_API_KEY environment variable
    openai = OpenAIProvider()
    
    print("🔮 AI SDK Python - Embedding Example")
    print("=" * 50)
    
    # Example 1: Single embedding
    print("\n1. Single Embedding Example")
    print("-" * 30)
    
    embedding_model = openai.embedding_model("text-embedding-3-small")
    
    text = "The quick brown fox jumps over the lazy dog."
    result = await embed(
        model=embedding_model,
        value=text,
    )
    
    print(f"Text: {text}")
    print(f"Embedding dimensions: {len(result.embedding)}")
    print(f"First 5 dimensions: {result.embedding[:5]}")
    print(f"Tokens used: {result.usage.tokens}")
    
    # Example 2: Multiple embeddings (batch processing)
    print("\n2. Multiple Embeddings Example")
    print("-" * 35)
    
    texts = [
        "I love machine learning and artificial intelligence",
        "Python is a great programming language for data science",
        "The weather today is sunny and warm", 
        "Natural language processing is fascinating",
        "I enjoy hiking in the mountains",
    ]
    
    results = await embed_many(
        model=embedding_model,
        values=texts,
    )
    
    print(f"Embedded {len(texts)} texts")
    print(f"Total tokens used: {results.usage.tokens}")
    
    for i, (text, embedding) in enumerate(zip(results.values, results.embeddings)):
        print(f"{i+1}. '{text}' -> {len(embedding)} dimensions")
    
    # Example 3: Semantic similarity
    print("\n3. Semantic Similarity Example")
    print("-" * 35)
    
    # Compare embeddings to find similar texts
    similarities = []
    
    for i in range(len(results.embeddings)):
        for j in range(i + 1, len(results.embeddings)):
            similarity = cosine_similarity(results.embeddings[i], results.embeddings[j])
            similarities.append((i, j, similarity, texts[i], texts[j]))
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[2], reverse=True)
    
    print("Most similar text pairs:")
    for i, j, sim, text1, text2 in similarities[:3]:
        print(f"Similarity: {sim:.3f}")
        print(f"  Text 1: '{text1}'")
        print(f"  Text 2: '{text2}'")
        print()
    
    # Example 4: Using different embedding models
    print("\n4. Different Embedding Models Example")
    print("-" * 40)
    
    models = [
        ("text-embedding-3-small", "Small model (fast, lower cost)"),
        ("text-embedding-3-large", "Large model (more accurate, higher cost)"),
        ("text-embedding-ada-002", "Legacy model (older, still good)"),
    ]
    
    sample_text = "Artificial intelligence is transforming the world."
    
    for model_id, description in models:
        try:
            model = openai.embedding_model(model_id)
            result = await embed(model=model, value=sample_text)
            
            print(f"Model: {model_id}")
            print(f"Description: {description}")
            print(f"Embedding dimensions: {len(result.embedding)}")
            print(f"Tokens used: {result.usage.tokens}")
            print()
        except Exception as e:
            print(f"Model {model_id} failed: {e}")
            print()
    
    # Example 5: Custom dimensions (text-embedding-3 models only)
    print("\n5. Custom Dimensions Example")
    print("-" * 35)
    
    try:
        # Create embedding model with custom dimensions
        custom_model = openai.embedding_model("text-embedding-3-small").with_dimensions(512)
        
        result = await embed(
            model=custom_model,
            value="This embedding will have exactly 512 dimensions.",
        )
        
        print(f"Custom embedding dimensions: {len(result.embedding)}")
        print(f"Tokens used: {result.usage.tokens}")
        
    except Exception as e:
        print(f"Custom dimensions failed: {e}")
    
    # Example 6: Large batch processing
    print("\n6. Large Batch Processing Example")
    print("-" * 40)
    
    # Create a large list of texts
    large_batch = [
        f"This is text number {i} for batch processing demonstration."
        for i in range(50)  # 50 texts
    ]
    
    print(f"Processing {len(large_batch)} texts...")
    
    # This will automatically handle batching and parallel processing
    large_results = await embed_many(
        model=embedding_model,
        values=large_batch,
        max_parallel_calls=3,  # Limit parallel calls
    )
    
    print(f"Successfully embedded {len(large_results.embeddings)} texts")
    print(f"Total tokens used: {large_results.usage.tokens}")
    print(f"Average tokens per text: {large_results.usage.tokens / len(large_batch):.1f}")
    
    print("\n✨ Embedding examples completed!")


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: Please set the OPENAI_API_KEY environment variable")
        print("   You can get an API key from: https://platform.openai.com/api-keys")
        exit(1)
    
    asyncio.run(main())