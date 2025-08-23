"""
Comprehensive DeepSeek Provider Example for AI SDK Python.

This example demonstrates the key features of the DeepSeek provider:
1. Basic text generation with deepseek-chat
2. Advanced reasoning with deepseek-reasoner
3. Streaming responses with reasoning steps
4. Tool calling and function execution
5. JSON mode for structured outputs
6. Prompt caching metrics and optimization
7. Cost-effective high-quality generation
8. Mathematical and logical reasoning tasks
9. Multi-step problem solving
10. Error handling and best practices

Prerequisites:
- Install ai-sdk-python: pip install ai-sdk-python[deepseek]
- Set DEEPSEEK_API_KEY environment variable or pass api_key parameter
"""

import asyncio
import json
import os
from typing import Any, Dict, List

from ai_sdk import generate_text, stream_text
from ai_sdk.providers.deepseek import (
    DeepSeekProvider,
    create_deepseek_provider,
    DeepSeekChatModelId,
    DeepSeekProviderSettings
)
from ai_sdk.core.types import ChatPrompt, UserMessage, SystemMessage
from ai_sdk.tools.core import create_tool


async def basic_text_generation():
    """Demonstrate basic text generation with DeepSeek chat model."""
    print("=== Basic Text Generation ===")
    
    # Create provider (uses DEEPSEEK_API_KEY from environment)
    provider = DeepSeekProvider()
    model = provider.language_model("deepseek-chat")
    
    # Simple text generation
    result = await generate_text(
        model=model,
        prompt="Explain the concept of machine learning in simple terms.",
        max_output_tokens=300,
        temperature=0.7
    )
    
    print(f"Generated text: {result.text}")
    print(f"Usage: {result.usage}")
    print(f"Finish reason: {result.finish_reason}")
    
    # Show DeepSeek-specific metadata
    if result.provider_metadata and "deepseek" in result.provider_metadata:
        deepseek_meta = result.provider_metadata["deepseek"]
        print(f"DeepSeek finish reason: {deepseek_meta.get('finish_reason')}")
        
        # Show cache metrics if available
        cache_info = provider.get_cache_metrics(result)
        if cache_info:
            print(f"Cache efficiency: {cache_info.get('efficiency', 'unknown')}")
            print(f"Cache hit rate: {cache_info.get('hit_rate', 0):.2%}")


async def reasoning_model_example():
    """Demonstrate advanced reasoning with deepseek-reasoner."""
    print("\n=== Advanced Reasoning Model ===")
    
    provider = DeepSeekProvider()
    model = provider.language_model("deepseek-reasoner")
    
    # Create reasoning options
    reasoning_opts = provider.create_reasoning_options(
        enable_reasoning_output=True,
        reasoning_effort="high"
    )
    
    # Complex reasoning problem
    result = await generate_text(
        model=model,
        prompt="""
        Solve this step by step:
        
        A train leaves Station A at 2:00 PM traveling at 60 mph toward Station B.
        Another train leaves Station B at 2:30 PM traveling at 80 mph toward Station A.
        If the stations are 350 miles apart, at what time will the trains meet?
        
        Show your reasoning process clearly.
        """,
        max_output_tokens=600,
        temperature=0.1,
        provider_options=reasoning_opts
    )
    
    print(f"Reasoning solution:\n{result.text}")
    
    # Show reasoning metadata if available
    if result.provider_metadata and "deepseek" in result.provider_metadata:
        deepseek_meta = result.provider_metadata["deepseek"]
        if "reasoning_content" in deepseek_meta:
            print(f"\nInternal reasoning process:")
            print(f"{deepseek_meta['reasoning_content'][:200]}...")


async def streaming_reasoning():
    """Demonstrate streaming with reasoning model."""
    print("\n=== Streaming Reasoning ===")
    
    provider = DeepSeekProvider()
    model = provider.language_model("deepseek-reasoner")
    
    print("Problem: Prove that the square root of 2 is irrational.")
    print("Streaming solution: ", end="", flush=True)
    
    async for part in stream_text(
        model=model,
        prompt="Provide a mathematical proof that the square root of 2 is irrational. Show each step clearly.",
        max_output_tokens=500,
        temperature=0.2
    ):
        if hasattr(part, 'delta') and part.delta:
            print(part.delta, end="", flush=True)
        elif hasattr(part, 'finish_reason'):
            print(f"\n\nStream finished: {part.finish_reason}")
            if part.usage:
                print(f"Usage: {part.usage}")
            
            # Show cache metrics
            if hasattr(part, 'provider_metadata'):
                cache_info = provider.get_cache_metrics(part)
                if cache_info:
                    print(f"Cache hit tokens: {cache_info.get('hit_tokens', 0)}")
                    print(f"Cache miss tokens: {cache_info.get('miss_tokens', 0)}")


async def tool_calling_example():
    """Demonstrate tool calling with DeepSeek models."""
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
    
    unit_converter_tool = create_tool(
        name="unit_converter",
        description="Convert between different units",
        parameters={
            "type": "object",
            "properties": {
                "value": {
                    "type": "number",
                    "description": "Value to convert"
                },
                "from_unit": {
                    "type": "string",
                    "description": "Unit to convert from"
                },
                "to_unit": {
                    "type": "string", 
                    "description": "Unit to convert to"
                }
            },
            "required": ["value", "from_unit", "to_unit"]
        }
    )
    
    provider = DeepSeekProvider()
    model = provider.language_model("deepseek-chat")
    
    result = await generate_text(
        model=model,
        prompt="Calculate 15% tip on a $87.50 restaurant bill and convert the total to euros (assuming 1 USD = 0.85 EUR).",
        tools=[calculator_tool, unit_converter_tool],
        max_output_tokens=300
    )
    
    print(f"Response: {result.text}")
    
    if result.tool_calls:
        print(f"Tool calls made: {len(result.tool_calls)}")
        for i, tool_call in enumerate(result.tool_calls):
            print(f"  {i+1}. {tool_call['name']}: {tool_call['arguments']}")


async def json_mode_example():
    """Demonstrate JSON mode for structured outputs."""
    print("\n=== JSON Mode Example ===")
    
    provider = DeepSeekProvider()
    model = provider.language_model("deepseek-chat")
    
    # Define JSON schema for analysis
    schema = {
        "type": "object",
        "properties": {
            "analysis": {
                "type": "object",
                "properties": {
                    "main_theme": {"type": "string"},
                    "key_points": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "complexity_level": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"]
                    },
                    "estimated_reading_time": {"type": "integer"}
                }
            },
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"]
                        }
                    }
                }
            },
            "confidence_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            }
        },
        "required": ["analysis", "recommendations", "confidence_score"]
    }
    
    result = await generate_text(
        model=model,
        prompt="""
        Analyze this text about quantum computing:
        
        "Quantum computing represents a paradigm shift in computational capability, leveraging quantum mechanical phenomena like superposition and entanglement to process information in fundamentally different ways than classical computers. While still in early stages, quantum computers show promise for solving certain problems exponentially faster than classical systems, particularly in cryptography, optimization, and simulation of quantum systems."
        """,
        response_format={
            "type": "json",
            "schema": schema
        },
        max_output_tokens=400
    )
    
    print(f"JSON Response: {result.text}")
    
    try:
        parsed_json = json.loads(result.text)
        analysis = parsed_json.get("analysis", {})
        print(f"\nParsed Analysis:")
        print(f"Main Theme: {analysis.get('main_theme')}")
        print(f"Complexity: {analysis.get('complexity_level')}")
        print(f"Key Points: {len(analysis.get('key_points', []))} identified")
        print(f"Confidence: {parsed_json.get('confidence_score', 0):.2%}")
    except json.JSONDecodeError:
        print("Failed to parse JSON response")


async def mathematical_reasoning():
    """Demonstrate mathematical problem solving with reasoning model."""
    print("\n=== Mathematical Reasoning ===")
    
    provider = DeepSeekProvider()
    model = provider.language_model("deepseek-reasoner")
    
    # Complex mathematical problem
    result = await generate_text(
        model=model,
        prompt="""
        Solve this calculus problem step by step:
        
        Find the area between the curves y = x² and y = 2x - x² in the first quadrant.
        
        Show all steps including:
        1. Finding intersection points
        2. Setting up the integral
        3. Evaluating the integral
        4. Final answer with units
        """,
        max_output_tokens=800,
        temperature=0.1
    )
    
    print(f"Mathematical solution:\n{result.text}")
    
    if result.usage:
        print(f"\nToken usage: {result.usage.total_tokens}")


async def logical_reasoning_chain():
    """Demonstrate multi-step logical reasoning."""
    print("\n=== Logical Reasoning Chain ===")
    
    provider = DeepSeekProvider()
    model = provider.language_model("deepseek-reasoner")
    
    # Create a conversation for multi-step reasoning
    prompt = ChatPrompt(messages=[
        SystemMessage(
            content="You are a logic expert. Solve problems step by step with clear reasoning."
        ),
        UserMessage(
            content="""
            Solve this logic puzzle:
            
            Five friends (Alice, Bob, Carol, David, Eve) live in different colored houses 
            (red, blue, green, yellow, white) and have different pets (cat, dog, fish, bird, rabbit).
            
            Clues:
            1. Alice lives in the red house
            2. The person with the cat lives in the blue house
            3. Carol has a dog
            4. The person in the green house has a bird
            5. David doesn't live in the yellow or white house
            6. Eve doesn't have a fish or rabbit
            7. Bob lives next to Alice (houses are in a row)
            8. The white house is at one end
            
            Who has which pet and lives in which house?
            """
        )
    ])
    
    result = await generate_text(
        model=model,
        prompt=prompt,
        max_output_tokens=1000,
        temperature=0.1
    )
    
    print(f"Logic puzzle solution:\n{result.text}")


async def cost_effectiveness_demo():
    """Demonstrate cost-effective generation for bulk tasks."""
    print("\n=== Cost Effectiveness Demo ===")
    
    provider = DeepSeekProvider()
    model = provider.language_model("deepseek-chat")
    
    # Multiple tasks to show cost efficiency
    tasks = [
        "Summarize the benefits of renewable energy in 2 sentences.",
        "Write a haiku about artificial intelligence.",
        "Explain photosynthesis to a 10-year-old.", 
        "List 5 tips for time management.",
        "Describe the water cycle briefly."
    ]
    
    total_tokens = 0
    
    for i, task in enumerate(tasks, 1):
        result = await generate_text(
            model=model,
            prompt=task,
            max_output_tokens=150,
            temperature=0.7
        )
        
        print(f"Task {i}: {task}")
        print(f"Response: {result.text}")
        
        if result.usage:
            total_tokens += result.usage.total_tokens
        
        # Show cache metrics
        cache_info = provider.get_cache_metrics(result)
        if cache_info:
            print(f"Cache efficiency: {cache_info.get('efficiency', 'unknown')}")
        
        print("-" * 40)
    
    print(f"Total tokens used across all tasks: {total_tokens}")


async def error_handling_example():
    """Demonstrate error handling and best practices."""
    print("\n=== Error Handling ===")
    
    try:
        # Invalid API key example
        provider = create_deepseek_provider(api_key="invalid-key")
        model = provider.language_model("deepseek-chat")
        
        result = await generate_text(
            model=model,
            prompt="This will fail",
            max_output_tokens=50
        )
        
    except Exception as e:
        print(f"Expected error with invalid API key: {type(e).__name__}: {e}")
    
    try:
        # Invalid reasoning effort example
        provider = DeepSeekProvider()
        invalid_opts = provider.create_reasoning_options(reasoning_effort="invalid")
        
    except Exception as e:
        print(f"Expected error with invalid reasoning effort: {type(e).__name__}: {e}")


async def provider_info_example():
    """Show provider capabilities and model information."""
    print("\n=== Provider Information ===")
    
    provider = DeepSeekProvider()
    
    # Get provider info
    provider_info = provider.get_provider_info()
    print(f"Provider: {provider_info['name']}")
    print(f"Description: {provider_info['description']}")
    print(f"Capabilities: {', '.join(provider_info['capabilities'])}")
    print(f"Special Features: {', '.join(provider_info['special_features'])}")
    
    # Get available models
    models = provider.get_available_models()
    
    print(f"\nAvailable Models:")
    for model_id, info in models["language_models"].items():
        print(f"  {model_id}:")
        print(f"    {info['description']}")
        print(f"    Context: {info.get('context_length', 'Unknown')} tokens")
        print(f"    Pricing: {info.get('pricing', 'Unknown')}")
        print(f"    Use Cases: {', '.join(info.get('use_cases', []))}")
        if info.get('supports_reasoning'):
            print(f"    Special: Advanced reasoning capabilities")


async def comparison_demo():
    """Compare deepseek-chat vs deepseek-reasoner on the same task."""
    print("\n=== Model Comparison ===")
    
    provider = DeepSeekProvider()
    
    problem = "Explain why the Monty Hall problem is counterintuitive and what the correct strategy is."
    
    models = ["deepseek-chat", "deepseek-reasoner"]
    
    for model_id in models:
        print(f"\n--- {model_id.upper()} ---")
        model = provider.language_model(model_id)
        
        result = await generate_text(
            model=model,
            prompt=problem,
            max_output_tokens=300,
            temperature=0.3
        )
        
        print(f"Response: {result.text[:400]}...")
        if result.usage:
            print(f"Tokens: {result.usage.total_tokens}")
        
        cache_info = provider.get_cache_metrics(result)
        if cache_info:
            print(f"Cache efficiency: {cache_info.get('efficiency', 'unknown')}")


async def main():
    """Run all examples."""
    print("DeepSeek Provider Examples for AI SDK Python")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("WARNING: DEEPSEEK_API_KEY not found. Some examples may fail.")
        print("Set your API key: export DEEPSEEK_API_KEY='your-api-key'")
        print()
    
    try:
        await basic_text_generation()
        await reasoning_model_example()
        await streaming_reasoning()
        await tool_calling_example()
        await json_mode_example()
        await mathematical_reasoning()
        await logical_reasoning_chain()
        await cost_effectiveness_demo()
        await error_handling_example()
        await provider_info_example()
        await comparison_demo()
        
        print("\n" + "=" * 60)
        print("All DeepSeek examples completed successfully!")
        print("Key takeaways:")
        print("  • DeepSeek offers cost-effective high-quality models")
        print("  • deepseek-reasoner excels at complex reasoning tasks")
        print("  • Prompt caching can significantly reduce costs")
        print("  • OpenAI compatibility makes integration seamless")
        print("  • Advanced reasoning capabilities rival premium models")
        
    except Exception as e:
        print(f"\nExample failed: {type(e).__name__}: {e}")
        print("Check your API key and internet connection.")


if __name__ == "__main__":
    asyncio.run(main())