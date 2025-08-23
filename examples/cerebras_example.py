#!/usr/bin/env python3
"""
Cerebras Provider Example for AI SDK Python.

This example demonstrates how to use Cerebras' ultra-fast inference 
with their specialized Wafer-Scale Engine hardware for dramatically
faster response times compared to traditional GPUs.

Features demonstrated:
- Ultra-fast text generation (10x+ faster than traditional GPUs)
- Streaming responses for real-time interaction
- Tool calling capabilities
- JSON mode for structured outputs
- Speed optimization techniques
- Model comparison and benchmarking

Before running:
1. Install dependencies: pip install ai-sdk[cerebras] # (when available)
2. Set your API key: export CEREBRAS_API_KEY="your-api-key"
3. Get API key from: https://inference.cerebras.ai/

Note: Cerebras specializes in ultra-fast inference, making it ideal for
real-time applications, interactive chat, and scenarios where latency matters.
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
    create_cerebras,
    tool,
    Agent
)
from ai_sdk.providers.cerebras.types import CEREBRAS_MODEL_INFO


# Example tools for demonstration
@tool
async def get_system_performance():
    """Get current system performance metrics."""
    return {
        "cpu_usage": "25%",
        "memory_usage": "60%", 
        "network_latency": "12ms",
        "timestamp": time.time()
    }

@tool 
async def calculate_speed_improvement(base_time: float, cerebras_time: float):
    """Calculate speed improvement factor."""
    if cerebras_time <= 0:
        return {"error": "Invalid cerebras_time"}
    
    improvement = base_time / cerebras_time
    return {
        "base_time": base_time,
        "cerebras_time": cerebras_time, 
        "speed_improvement": f"{improvement:.1f}x faster",
        "time_saved": base_time - cerebras_time,
        "efficiency_gain": f"{((improvement - 1) * 100):.1f}% faster"
    }


async def main():
    """Demonstrate Cerebras provider capabilities."""
    
    print("🧠 Cerebras AI Provider Demo - Ultra-Fast Inference")
    print("=" * 60)
    
    # Initialize Cerebras provider
    cerebras = create_cerebras()
    
    # Display provider information
    provider_info = cerebras.get_provider_info()
    print(f"\n📋 Provider Info:")
    print(f"   Name: {provider_info['name']}")
    print(f"   Description: {provider_info['description']}")
    print(f"   Hardware: {provider_info['hardware']['type']}")
    print(f"   Speed Advantage: {provider_info['hardware']['speed_improvement']}")
    
    # Display available models
    models = cerebras.get_available_models()
    print(f"\n🚀 Available Models:")
    for model_id, info in models["language_models"].items():
        print(f"   • {model_id}")
        print(f"     - {info['description']}")
        print(f"     - Speed: {info['inference_speed']}")
        print(f"     - Parameters: {info['parameters']}")
        print(f"     - Context: {info['context_length']:,} tokens")
    
    print("\n" + "=" * 60)
    
    # Example 1: Ultra-Fast Text Generation
    print("\n1️⃣  Ultra-Fast Text Generation")
    print("-" * 30)
    
    model = cerebras.language_model("llama3.1-8b")
    
    # Measure response time
    start_time = time.time()
    
    result = await generate_text(
        model=model,
        prompt="Explain the advantages of specialized AI hardware like Cerebras WSE in one paragraph:",
        max_tokens=150,
        temperature=0.7
    )
    
    response_time = (time.time() - start_time) * 1000  # Convert to ms
    
    print(f"✅ Response: {result.text}")
    print(f"⚡ Response time: {response_time:.0f}ms")
    print(f"📊 Tokens: {result.usage.totalTokens}")
    
    # Compare with typical GPU speeds
    speed_comparison = cerebras.get_speed_comparison("llama3.1-8b")
    print(f"🏆 Speed advantage: {speed_comparison['speedup']}")
    
    print("\n" + "-" * 60)
    
    # Example 2: Streaming for Real-Time Interaction
    print("\n2️⃣  Real-Time Streaming (Ultra-Low Latency)")
    print("-" * 30)
    
    print("Streaming response:")
    stream_start = time.time()
    
    async for chunk in stream_text(
        model=model,
        prompt="List 5 benefits of ultra-fast AI inference:",
        max_tokens=200
    ):
        if chunk.type == "text-delta":
            print(chunk.textDelta, end="", flush=True)
        elif chunk.type == "finish":
            stream_time = (time.time() - stream_start) * 1000
            print(f"\n\n⚡ Streaming completed in: {stream_time:.0f}ms")
            print(f"📊 Total tokens: {chunk.usage.totalTokens}")
            
            # Extract Cerebras-specific metadata
            if chunk.providerMetadata and "cerebras" in chunk.providerMetadata:
                cerebras_meta = chunk.providerMetadata["cerebras"]
                print(f"🔧 Hardware: {cerebras_meta.get('hardware', 'cerebras_wse')}")
                print(f"⚡ Speed: {cerebras_meta.get('inference_speed', 'ultra_fast')}")
    
    print("\n" + "-" * 60)
    
    # Example 3: Tool Calling with Ultra-Fast Response
    print("\n3️⃣  Tool Calling with Ultra-Fast Response")
    print("-" * 30)
    
    # Create agent with tools
    agent = Agent(
        model=model,
        tools=[get_system_performance, calculate_speed_improvement]
    )
    
    tool_start = time.time()
    
    agent_result = await agent.generate_text(
        "Check the system performance, then calculate how much faster a 50ms Cerebras response would be compared to a typical 500ms GPU response."
    )
    
    tool_time = (time.time() - tool_start) * 1000
    
    print(f"✅ Agent response: {agent_result.text}")
    print(f"⚡ Total time (including tools): {tool_time:.0f}ms")
    print(f"🔧 Tool calls executed: {len(agent_result.toolCalls) if agent_result.toolCalls else 0}")
    
    print("\n" + "-" * 60)
    
    # Example 4: JSON Mode for Structured Output
    print("\n4️⃣  JSON Mode for Structured Output")
    print("-" * 30)
    
    from pydantic import BaseModel
    from typing import List
    
    class SpeedBenchmark(BaseModel):
        model_name: str
        avg_response_time_ms: float
        tokens_per_second: float
        use_cases: List[str]
        hardware_advantage: str
    
    json_start = time.time()
    
    benchmark_result = await generate_object(
        model=model,
        schema=SpeedBenchmark,
        prompt="Create a performance benchmark for the llama3.1-8b model on Cerebras hardware, focusing on its speed advantages."
    )
    
    json_time = (time.time() - json_start) * 1000
    
    print(f"✅ Structured output generated:")
    print(json.dumps(benchmark_result.object.model_dump(), indent=2))
    print(f"⚡ JSON generation time: {json_time:.0f}ms")
    
    print("\n" + "-" * 60)
    
    # Example 5: Speed-Optimized Configuration
    print("\n5️⃣  Speed-Optimized Configuration")
    print("-" * 30)
    
    # Create speed-optimized options
    speed_opts = cerebras.create_speed_optimized_options(
        prioritize_latency=True,
        max_tokens=100,
        temperature=0.5
    )
    
    print(f"Speed-optimized settings: {speed_opts}")
    
    optimized_start = time.time()
    
    optimized_result = await generate_text(
        model=model,
        prompt="Explain Cerebras' Wafer-Scale Engine in 50 words:",
        **speed_opts
    )
    
    optimized_time = (time.time() - optimized_start) * 1000
    
    print(f"✅ Optimized response: {optimized_result.text}")
    print(f"⚡ Optimized response time: {optimized_time:.0f}ms")
    
    print("\n" + "-" * 60)
    
    # Example 6: Model Comparison
    print("\n6️⃣  Model Size Comparison")
    print("-" * 30)
    
    models_to_compare = ["llama3.1-8b", "llama3.1-70b", "llama-3.3-70b"]
    
    for model_id in models_to_compare:
        model_info = CEREBRAS_MODEL_INFO.get(model_id, {})
        speed_comp = cerebras.get_speed_comparison(model_id)
        
        print(f"\n🧠 {model_id}:")
        print(f"   Parameters: {model_info.get('parameters', 'N/A')}")
        print(f"   Speed: {speed_comp.get('speedup', 'N/A')}")
        print(f"   Best for: {', '.join(model_info.get('use_cases', [])[:3])}")
        print(f"   Hardware advantage: {speed_comp.get('hardware_advantage', 'WSE acceleration')}")
    
    print("\n" + "=" * 60)
    
    # Performance Tips
    print("\n💡 Cerebras Performance Tips:")
    print("""
    1. Use llama3.1-8b for maximum speed (10x faster than GPUs)
    2. Enable streaming for perceived ultra-low latency
    3. Keep max_tokens reasonable for faster responses
    4. Use lower temperature values for more deterministic (faster) outputs
    5. Leverage tool calling for complex multi-step tasks
    6. Consider batch processing for multiple similar requests
    7. Monitor response times to optimize for your use case
    
    🏆 Cerebras WSE advantage: Massive parallel processing with unified memory
    ⚡ Perfect for: Real-time chat, interactive apps, rapid prototyping
    🎯 Use cases: Customer service, gaming, live demos, edge applications
    """)
    
    print("\n🎉 Demo completed! Cerebras provides ultra-fast inference for real-time AI applications.")


if __name__ == "__main__":
    asyncio.run(main())