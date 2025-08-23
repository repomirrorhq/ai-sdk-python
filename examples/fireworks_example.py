#!/usr/bin/env python3
"""
Fireworks Provider Example for AI SDK Python.

This example demonstrates how to use Fireworks AI's high-performance model 
hosting platform with a wide variety of optimized open-source models.

Features demonstrated:
- High-performance inference with optimized models
- Wide model selection (Llama, Mixtral, Qwen, DeepSeek, etc.)
- Chat models with streaming and tool calling
- Embedding models for semantic search
- Multimodal vision capabilities
- Performance optimization strategies
- Model recommendations for different use cases

Before running:
1. Install dependencies: pip install ai-sdk[fireworks] # (when available)
2. Set your API key: export FIREWORKS_API_KEY="your-api-key"
3. Get API key from: https://fireworks.ai/

Note: Fireworks specializes in high-performance hosting of open-source models
with optimized inference infrastructure and competitive pricing.
"""

import asyncio
import time
import json
from typing import List, Dict, Any

# AI SDK imports
from ai_sdk import (
    generate_text,
    stream_text, 
    generate_object,
    embed,
    embed_many,
    create_fireworks,
    tool,
    Agent
)
from ai_sdk.providers.fireworks.types import FIREWORKS_MODEL_INFO


# Example tools for demonstration
@tool
async def get_model_performance_info(model_id: str):
    """Get performance information for a specific Fireworks model."""
    model_info = FIREWORKS_MODEL_INFO.get(model_id, {})
    return {
        "model_id": model_id,
        "description": model_info.get("description", "Unknown model"),
        "context_length": model_info.get("context_length", "Unknown"),
        "optimization": model_info.get("provider_optimization", "fireworks_hosted"),
        "use_cases": model_info.get("use_cases", [])
    }

@tool 
async def compare_embedding_similarity(text1: str, text2: str):
    """Compare similarity between two texts using embeddings."""
    # This would use the embedding model in a real implementation
    return {
        "text1": text1[:50] + "..." if len(text1) > 50 else text1,
        "text2": text2[:50] + "..." if len(text2) > 50 else text2,
        "similarity_score": 0.85,  # Mock score
        "relationship": "highly similar"
    }


async def main():
    """Demonstrate Fireworks provider capabilities."""
    
    print("🔥 Fireworks AI Provider Demo - High-Performance Model Hosting")
    print("=" * 70)
    
    # Initialize Fireworks provider
    fireworks = create_fireworks()
    
    # Display provider information
    provider_info = fireworks.get_provider_info()
    print(f"\n📋 Provider Info:")
    print(f"   Name: {provider_info['name']}")
    print(f"   Description: {provider_info['description']}")
    print(f"   Infrastructure: {provider_info['infrastructure']['optimization']}")
    print(f"   Model Families: {', '.join(provider_info['model_families'])}")
    
    # Display available models overview
    models = fireworks.get_available_models()
    print(f"\n🚀 Available Models Overview:")
    print(f"   Total models: {models['total_models']}")
    print(f"   Language models: {len(models['language_models'])}")
    print(f"   Embedding models: {len(models['embedding_models'])}")
    
    # Show model categories
    print(f"\n📊 Model Categories:")
    for category, model_list in models["model_categories"].items():
        print(f"   • {category.replace('_', ' ').title()}: {len(model_list)} models")
    
    print("\n" + "=" * 70)
    
    # Example 1: High-Performance Text Generation
    print("\n1️⃣  High-Performance Text Generation")
    print("-" * 35)
    
    # Use Llama 3.3 70B for high-quality generation
    model = fireworks.language_model("accounts/fireworks/models/llama-v3p3-70b-instruct")
    
    start_time = time.time()
    
    result = await generate_text(
        model=model,
        prompt="Explain the advantages of using optimized open-source models on dedicated inference infrastructure:",
        max_tokens=200,
        temperature=0.7
    )
    
    response_time = (time.time() - start_time) * 1000
    
    print(f"✅ Response: {result.text}")
    print(f"⚡ Response time: {response_time:.0f}ms")
    print(f"📊 Tokens: {result.usage.totalTokens}")
    print(f"🔥 Model: {result.providerMetadata['fireworks']['model'] if result.providerMetadata else 'N/A'}")
    
    print("\n" + "-" * 70)
    
    # Example 2: Efficient Small Model for Fast Responses
    print("\n2️⃣  Efficient Small Model (Cost-Effective)")
    print("-" * 35)
    
    efficient_model = fireworks.language_model("accounts/fireworks/models/llama-v3p2-3b-instruct")
    
    print("Streaming response from efficient 3B model:")
    stream_start = time.time()
    
    async for chunk in stream_text(
        model=efficient_model,
        prompt="List 3 benefits of using smaller, efficient language models:",
        max_tokens=150
    ):
        if chunk.type == "text-delta":
            print(chunk.textDelta, end="", flush=True)
        elif chunk.type == "finish":
            stream_time = (time.time() - stream_start) * 1000
            print(f"\n\n⚡ Fast streaming completed in: {stream_time:.0f}ms")
            print(f"📊 Total tokens: {chunk.usage.totalTokens}")
            print(f"💰 Cost-effective model with good performance")
    
    print("\n" + "-" * 70)
    
    # Example 3: Specialized Coding Model
    print("\n3️⃣  Specialized Coding Model")
    print("-" * 35)
    
    coding_model = fireworks.language_model("accounts/fireworks/models/qwen2p5-coder-32b-instruct")
    
    coding_result = await generate_text(
        model=coding_model,
        prompt="""Write a Python function that efficiently calculates the Fibonacci sequence using memoization:
        
        Requirements:
        - Use a decorator for memoization
        - Include type hints
        - Add docstring
        - Handle edge cases""",
        max_tokens=300
    )
    
    print(f"✅ Code generated by specialized coding model:")
    print(f"{coding_result.text}")
    print(f"🧠 Model optimized for: {FIREWORKS_MODEL_INFO.get('accounts/fireworks/models/qwen2p5-coder-32b-instruct', {}).get('use_cases', ['coding'])}")
    
    print("\n" + "-" * 70)
    
    # Example 4: Tool Calling with Advanced Reasoning
    print("\n4️⃣  Tool Calling with Advanced Reasoning Model")
    print("-" * 35)
    
    reasoning_model = fireworks.language_model("accounts/fireworks/models/deepseek-v3")
    
    # Create agent with tools
    agent = Agent(
        model=reasoning_model,
        tools=[get_model_performance_info, compare_embedding_similarity]
    )
    
    agent_result = await agent.generate_text(
        "Get performance info for the DeepSeek V3 model, then compare the similarity between 'machine learning' and 'artificial intelligence'."
    )
    
    print(f"✅ Agent response: {agent_result.text}")
    print(f"🔧 Tool calls executed: {len(agent_result.toolCalls) if agent_result.toolCalls else 0}")
    print(f"🧠 Advanced reasoning model used for complex multi-step tasks")
    
    print("\n" + "-" * 70)
    
    # Example 5: Text Embeddings
    print("\n5️⃣  High-Quality Text Embeddings")
    print("-" * 35)
    
    embedding_model = fireworks.embedding_model("nomic-ai/nomic-embed-text-v1.5")
    
    # Single embedding
    single_result = await embed(
        model=embedding_model,
        input_text="Fireworks AI provides optimized inference for open-source models"
    )
    
    print(f"✅ Single embedding generated:")
    print(f"   Dimensions: {len(single_result.embedding)}")
    print(f"   Tokens used: {single_result.usage.tokens}")
    
    # Batch embeddings
    texts_to_embed = [
        "High-performance model hosting",
        "Open-source language models", 
        "Optimized inference infrastructure",
        "Cost-effective AI solutions"
    ]
    
    batch_result = await embed_many(
        model=embedding_model,
        input_texts=texts_to_embed
    )
    
    print(f"\n✅ Batch embeddings generated:")
    print(f"   Number of embeddings: {len(batch_result.embeddings)}")
    print(f"   Dimensions per embedding: {len(batch_result.embeddings[0])}")
    print(f"   Total tokens used: {batch_result.usage.tokens}")
    
    print("\n" + "-" * 70)
    
    # Example 6: Structured Output Generation
    print("\n6️⃣  Structured Output with JSON Mode")
    print("-" * 35)
    
    from pydantic import BaseModel
    from typing import List
    
    class ModelComparison(BaseModel):
        model_name: str
        strengths: List[str]
        ideal_use_cases: List[str] 
        performance_tier: str
        cost_efficiency: str
    
    json_result = await generate_object(
        model=model,
        schema=ModelComparison,
        prompt="Create a comparison analysis for the Mixtral 8x7B model, focusing on its mixture of experts architecture."
    )
    
    print(f"✅ Structured analysis generated:")
    print(json.dumps(json_result.object.model_dump(), indent=2))
    
    print("\n" + "-" * 70)
    
    # Example 7: Model Recommendations
    print("\n7️⃣  Model Recommendations by Use Case")
    print("-" * 35)
    
    use_cases = ["general_chat", "coding", "analysis", "cost_effective", "embeddings"]
    
    for use_case in use_cases:
        recommendation = fireworks.get_model_recommendations(use_case)
        print(f"\n🎯 {use_case.replace('_', ' ').title()}:")
        print(f"   Primary: {recommendation['primary'].split('/')[-1]}")
        print(f"   Reason: {recommendation['reasoning']}")
        if recommendation.get('alternatives'):
            alt_names = [alt.split('/')[-1] for alt in recommendation['alternatives'][:2]]
            print(f"   Alternatives: {', '.join(alt_names)}")
    
    print("\n" + "-" * 70)
    
    # Example 8: Performance Optimization
    print("\n8️⃣  Performance Optimization Strategies")
    print("-" * 35)
    
    optimization_types = ["speed", "quality", "cost", "balanced"]
    
    for opt_type in optimization_types:
        opts = fireworks.create_performance_options(
            optimize_for=opt_type,
            max_tokens=100
        )
        print(f"\n⚡ {opt_type.title()} optimization:")
        print(f"   Settings: {opts}")
        
        # Test with efficient model for speed demo
        if opt_type == "speed":
            speed_start = time.time()
            speed_result = await generate_text(
                model=efficient_model,
                prompt="Quick fact about Fireworks AI:",
                **opts
            )
            speed_time = (time.time() - speed_start) * 1000
            print(f"   Result: {speed_result.text[:100]}...")
            print(f"   Time: {speed_time:.0f}ms")
    
    print("\n" + "=" * 70)
    
    # Performance and Cost Analysis
    print("\n💡 Fireworks AI Advantages:")
    print("""
    🏭 Infrastructure Excellence:
    • High-performance GPU clusters optimized for inference
    • Auto-scaling infrastructure for consistent availability
    • Multi-region deployment for global low latency
    • Enterprise-grade reliability and uptime
    
    🤖 Model Diversity:
    • 10+ high-quality open-source model families
    • Specialized models for coding, reasoning, vision
    • Latest versions of popular models (Llama, Mixtral, Qwen)
    • Both large frontier models and efficient small models
    
    ⚡ Performance Optimizations:
    • Optimized model serving infrastructure
    • Fast inference with competitive response times  
    • Efficient batching and caching strategies
    • Streaming support for real-time applications
    
    💰 Cost Effectiveness:
    • Competitive pricing across all model sizes
    • Efficient small models for cost-sensitive use cases
    • Pay-per-use pricing model
    • No infrastructure management overhead
    
    🔧 Developer Experience:
    • OpenAI-compatible API for easy integration
    • Comprehensive model information and recommendations
    • Tool calling and JSON mode support
    • Multimodal capabilities for vision tasks
    """)
    
    print("\n🎉 Demo completed! Fireworks AI provides high-performance hosting")
    print("    for a wide variety of optimized open-source models.")


if __name__ == "__main__":
    asyncio.run(main())