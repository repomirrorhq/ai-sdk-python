#!/usr/bin/env python3
"""Comprehensive Together AI provider usage examples.

This example demonstrates various capabilities of the Together AI provider
including text generation, streaming, embeddings, and working with different
open-source models.

Together AI provides access to 100+ open-source models with competitive pricing
and supports models from Meta, Mistral, Google, and other leading AI research organizations.

Setup:
    Set your Together AI API key as an environment variable:
    export TOGETHER_API_KEY="your-together-api-key"
    
    Or install the ai-sdk package:
    pip install ai-sdk
"""

import asyncio
import os
from ai_sdk import create_together, generate_text, stream_text
from ai_sdk.core.embed import embed, embed_many


async def example_1_basic_text_generation():
    """Example 1: Basic text generation with Together AI."""
    print("\n=== Example 1: Basic Text Generation ===")
    
    # Create Together AI provider
    together = create_together()
    
    # Generate text using LLaMA 3.1 8B (fast and efficient)
    result = await generate_text(
        model=together.language_model("meta-llama/Llama-3.1-8B-Instruct-Turbo"),
        prompt="Explain the advantages of open-source AI models in 2-3 sentences."
    )
    
    print(f"Generated text: {result.text}")
    print(f"Usage: {result.usage.total_tokens} tokens ({result.usage.prompt_tokens} prompt + {result.usage.completion_tokens} completion)")


async def example_2_streaming_text():
    """Example 2: Real-time streaming text generation."""
    print("\n=== Example 2: Streaming Text Generation ===")
    
    together = create_together()
    
    print("Streaming response: ", end="", flush=True)
    
    async for chunk in stream_text(
        model=together.language_model("meta-llama/Llama-3.3-70B-Instruct-Turbo"),
        prompt="Write a creative story about AI and humans working together.",
        max_tokens=200,
        temperature=0.8
    ):
        if chunk.text_delta:
            print(chunk.text_delta, end="", flush=True)
    
    print()  # New line after streaming


async def example_3_model_comparison():
    """Example 3: Compare different open-source models."""
    print("\n=== Example 3: Model Comparison ===")
    
    together = create_together()
    
    prompt = "What is quantum computing? Explain in exactly one paragraph."
    
    models_to_test = [
        "meta-llama/Llama-3.1-8B-Instruct-Turbo",  # Meta LLaMA fast
        "meta-llama/Llama-3.3-70B-Instruct-Turbo", # Meta LLaMA large
        "mistralai/Mixtral-8x7B-Instruct-v0.1",     # Mistral Mixtral
        "google/gemma-2-9b-it",                      # Google Gemma
        "Qwen/Qwen2.5-7B-Instruct"                  # Alibaba Qwen
    ]
    
    for model_id in models_to_test:
        try:
            result = await generate_text(
                model=together.language_model(model_id),
                prompt=prompt,
                max_tokens=150,
                temperature=0.3
            )
            
            print(f"\n{model_id.split('/')[-1]}:")
            print(f"Response: {result.text}")
            print(f"Tokens: {result.usage.total_tokens}")
            
        except Exception as e:
            print(f"\n{model_id}: Error - {e}")


async def example_4_advanced_parameters():
    """Example 4: Using advanced generation parameters."""
    print("\n=== Example 4: Advanced Parameters ===")
    
    together = create_together()
    
    result = await generate_text(
        model=together.language_model("mistralai/Mixtral-8x7B-Instruct-v0.1"),
        prompt="Create a technical explanation of neural networks.",
        max_tokens=300,
        temperature=0.7,
        top_p=0.9,
        top_k=50,
        frequency_penalty=0.1,
        presence_penalty=0.1,
        stop_sequences=["END", "CONCLUSION"],
        seed=42  # For reproducible results
    )
    
    print(f"Technical explanation: {result.text}")
    print(f"Finish reason: {result.finish_reason}")


async def example_5_conversation_context():
    """Example 5: Multi-turn conversation with context."""
    print("\n=== Example 5: Conversation Context ===")
    
    together = create_together()
    
    # Create conversation with system message and history
    from ai_sdk.providers.types import Message
    
    messages = [
        Message(role="system", content="You are a helpful AI assistant specialized in explaining technology concepts clearly and concisely."),
        Message(role="user", content="What is machine learning?"),
        Message(role="assistant", content="Machine learning is a branch of AI where computers learn to make predictions or decisions by finding patterns in data, rather than being explicitly programmed for each task."),
        Message(role="user", content="How does it differ from traditional programming?")
    ]
    
    result = await generate_text(
        model=together.language_model("meta-llama/Llama-3.1-70B-Instruct-Turbo"),
        messages=messages,
        max_tokens=200,
        temperature=0.6
    )
    
    print(f"AI Assistant: {result.text}")


async def example_6_embeddings():
    """Example 6: Generate embeddings with Together AI."""
    print("\n=== Example 6: Embeddings Generation ===")
    
    together = create_together()
    
    # Single text embedding
    print("Generating single embedding...")
    embedding_result = await embed(
        model=together.embedding_model("BAAI/bge-large-en-v1.5"),
        value="Together AI provides access to many open-source models."
    )
    
    print(f"Embedding dimensions: {len(embedding_result.embedding)}")
    print(f"First 5 values: {embedding_result.embedding[:5]}")
    print(f"Usage: {embedding_result.usage.total_tokens} tokens")
    
    # Multiple text embeddings
    print("\nGenerating multiple embeddings...")
    texts = [
        "Open-source AI models democratize access to advanced AI capabilities.",
        "Together AI hosts models from leading research organizations.",
        "Cost-effective inference makes AI accessible to more developers.",
        "Community-driven development accelerates AI innovation."
    ]
    
    embeddings_result = await embed_many(
        model=together.embedding_model("BAAI/bge-large-en-v1.5"),
        values=texts
    )
    
    print(f"Generated {len(embeddings_result.embeddings)} embeddings")
    print(f"Total usage: {embeddings_result.usage.total_tokens} tokens")
    
    # Calculate semantic similarity
    from ai_sdk.core.embed import cosine_similarity
    
    similarity = cosine_similarity(
        embeddings_result.embeddings[0], 
        embeddings_result.embeddings[1]
    )
    print(f"Similarity between first two texts: {similarity:.3f}")


async def example_7_together_specific_models():
    """Example 7: Together AI-specific models and features."""
    print("\n=== Example 7: Together AI-Specific Models ===")
    
    together = create_together()
    
    # Test DeepSeek reasoning model
    print("Testing DeepSeek reasoning model...")
    try:
        result = await generate_text(
            model=together.language_model("deepseek-ai/deepseek-r1-distill-llama-70b"),
            prompt="Solve this step by step: If a train travels 120 km in 2 hours, what's its average speed?",
            max_tokens=200,
            temperature=0.1
        )
        print(f"DeepSeek response: {result.text}")
    except Exception as e:
        print(f"DeepSeek model error: {e}")
    
    # Test Databricks DBRX model
    print("\nTesting Databricks DBRX model...")
    try:
        result = await generate_text(
            model=together.language_model("databricks/dbrx-instruct"),
            prompt="Explain the concept of attention mechanisms in transformers.",
            max_tokens=150,
            temperature=0.5
        )
        print(f"DBRX response: {result.text}")
    except Exception as e:
        print(f"DBRX model error: {e}")


async def example_8_cost_optimization():
    """Example 8: Cost optimization strategies."""
    print("\n=== Example 8: Cost Optimization Strategies ===")
    
    together = create_together()
    
    prompt = "List 5 benefits of renewable energy."
    
    # Compare cost-effective smaller models vs larger models
    cost_models = [
        ("meta-llama/Llama-3.1-8B-Instruct-Turbo", "Small/Fast"),
        ("meta-llama/Llama-3.1-70B-Instruct-Turbo", "Large/Capable"),
        ("mistralai/Mistral-7B-Instruct-v0.3", "Efficient/Specialized")
    ]
    
    for model_id, description in cost_models:
        try:
            result = await generate_text(
                model=together.language_model(model_id),
                prompt=prompt,
                max_tokens=100,
                temperature=0.3
            )
            
            print(f"\n{description} ({model_id.split('/')[-1]}):")
            print(f"Tokens used: {result.usage.total_tokens}")
            print(f"Response quality: {len(result.text.split())} words")
            print(f"Preview: {result.text[:100]}...")
            
        except Exception as e:
            print(f"Error with {model_id}: {e}")


async def example_9_error_handling():
    """Example 9: Comprehensive error handling."""
    print("\n=== Example 9: Error Handling ===")
    
    together = create_together()
    
    # Test various error conditions
    test_cases = [
        {
            "name": "Invalid model",
            "model": "non-existent/model",
            "prompt": "Test prompt"
        },
        {
            "name": "Empty prompt",
            "model": "meta-llama/Llama-3.1-8B-Instruct-Turbo",
            "prompt": ""
        },
        {
            "name": "Extremely long prompt",
            "model": "meta-llama/Llama-3.1-8B-Instruct-Turbo",
            "prompt": "Test " * 10000  # Very long prompt
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        try:
            result = await generate_text(
                model=together.language_model(test['model']),
                prompt=test['prompt'],
                max_tokens=50
            )
            print(f"Success: {result.text[:50]}...")
        except Exception as e:
            print(f"Expected error: {type(e).__name__} - {e}")


async def example_10_streaming_with_embeddings():
    """Example 10: Combining streaming generation with embeddings."""
    print("\n=== Example 10: Streaming + Embeddings ===")
    
    together = create_together()
    
    print("Generating story with streaming...")
    story_parts = []
    
    async for chunk in stream_text(
        model=together.language_model("meta-llama/Llama-3.1-8B-Instruct-Turbo"),
        prompt="Write a short story about the future of AI in 100 words.",
        max_tokens=120,
        temperature=0.7
    ):
        if chunk.text_delta:
            print(chunk.text_delta, end="", flush=True)
            story_parts.append(chunk.text_delta)
    
    full_story = "".join(story_parts)
    print("\n")
    
    # Now generate embedding for the complete story
    print("Generating embedding for the story...")
    embedding_result = await embed(
        model=together.embedding_model("togethercomputer/m2-bert-80M-8k-retrieval"),
        value=full_story
    )
    
    print(f"Story embedding generated: {len(embedding_result.embedding)} dimensions")
    print(f"Embedding tokens used: {embedding_result.usage.total_tokens}")


async def main():
    """Run all Together AI examples."""
    
    # Check for API key
    if not os.getenv("TOGETHER_API_KEY"):
        print("❌ Please set your TOGETHER_API_KEY environment variable")
        print("You can get a free API key at: https://api.together.xyz/")
        print("\nExample:")
        print("export TOGETHER_API_KEY='your-together-api-key-here'")
        return
    
    print("🤝 Together AI Provider Examples")
    print("=" * 50)
    
    examples = [
        example_1_basic_text_generation,
        example_2_streaming_text,
        example_3_model_comparison,
        example_4_advanced_parameters,
        example_5_conversation_context,
        example_6_embeddings,
        example_7_together_specific_models,
        example_8_cost_optimization,
        example_9_error_handling,
        example_10_streaming_with_embeddings
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            await example_func()
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Interrupted at example {i}")
            break
        except Exception as e:
            print(f"\n❌ Example {i} failed: {e}")
    
    print("\n✅ Together AI examples completed!")
    print("\nTogether AI benefits:")
    print("• Access to 100+ open-source models from leading organizations")
    print("• Competitive pricing for both inference and embeddings")
    print("• High-quality models including LLaMA, Mixtral, Gemma, and more")
    print("• Support for both fast/cost-effective and large/capable models")
    print("• Community-driven development and transparent model hosting")
    print("• Great for research, development, and production workloads")


if __name__ == "__main__":
    asyncio.run(main())