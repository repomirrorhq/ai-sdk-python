#!/usr/bin/env python3
"""Comprehensive reasoning example for AI SDK Python.

This example demonstrates reasoning capabilities with OpenAI o1 models 
and Google Gemini models, showing how to:

1. Use reasoning models for complex problem solving
2. Track reasoning tokens and costs
3. Extract reasoning content from responses
4. Handle reasoning-specific model constraints

Requirements:
- OPENAI_API_KEY environment variable
- GOOGLE_API_KEY environment variable (for Gemini)
"""

import asyncio
import os
from typing import Optional

from ai_sdk import (
    generate_text, 
    extract_reasoning_text, 
    has_reasoning_tokens,
    get_reasoning_token_ratio
)
from ai_sdk.providers import OpenAIProvider, GoogleProvider
from ai_sdk.providers.openai import is_reasoning_model, REASONING_MODELS
from ai_sdk.providers.types import Content, ReasoningContent


async def demonstrate_openai_o1_reasoning():
    """Demonstrate OpenAI o1 model reasoning capabilities."""
    print("🧠 OpenAI o1 Reasoning Model Demo")
    print("=" * 50)
    
    # Initialize OpenAI provider
    openai_provider = OpenAIProvider(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Use the latest o1 model
    model = openai_provider.language_model("o1-2024-12-17")
    
    print(f"✅ Using reasoning model: o1-2024-12-17")
    print(f"   Is reasoning model: {is_reasoning_model('o1-2024-12-17')}")
    print(f"   Available reasoning models: {', '.join(REASONING_MODELS)}")
    print()
    
    # Complex mathematical reasoning problem
    problem = """
    A rectangular garden has a perimeter of 40 meters and an area of 91 square meters.
    What are the dimensions of the garden? Show your complete reasoning process.
    """
    
    print("🔍 Problem:")
    print(problem.strip())
    print("\n⏳ Generating response with reasoning...")
    
    try:
        result = await generate_text(
            model=model,
            messages=[
                {"role": "user", "content": problem}
            ],
            # Note: o1 models automatically filter out unsupported parameters
            # like temperature, top_p, etc.
        )
        
        print(f"\n📊 Usage Statistics:")
        print(f"   Prompt tokens: {result.usage.prompt_tokens}")
        print(f"   Completion tokens: {result.usage.completion_tokens}")
        print(f"   Reasoning tokens: {result.usage.reasoning_tokens}")
        print(f"   Total tokens: {result.usage.total_tokens}")
        
        if has_reasoning_tokens(result.usage):
            ratio = get_reasoning_token_ratio(result.usage)
            print(f"   Reasoning token ratio: {ratio:.2%}")
            print(f"   💰 Note: Reasoning tokens are typically charged differently")
        
        print(f"\n✨ Response:")
        print(result.text)
        
        # Extract any reasoning content (o1 models may include internal reasoning)
        if isinstance(result.content, list):
            reasoning_text = extract_reasoning_text(result.content)
            if reasoning_text:
                print(f"\n🧠 Extracted reasoning:")
                print(reasoning_text[:500] + "..." if len(reasoning_text) > 500 else reasoning_text)
        
    except Exception as e:
        print(f"❌ Error with OpenAI o1: {e}")
    
    print("\n" + "-" * 50 + "\n")


async def demonstrate_gemini_reasoning():
    """Demonstrate Google Gemini reasoning capabilities."""
    print("🚀 Google Gemini Reasoning Demo")
    print("=" * 40)
    
    # Initialize Google provider
    google_provider = GoogleProvider(
        api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Use Gemini 2.5 Pro with reasoning capabilities
    model = google_provider.language_model("gemini-2.5-pro")
    
    print(f"✅ Using model: gemini-2.5-pro")
    print()
    
    # Logic puzzle that benefits from reasoning
    problem = """
    Five people (Alice, Bob, Carol, Dave, Eve) are seated around a circular table.
    We know:
    1. Alice is sitting directly opposite to Bob
    2. Carol is sitting to the immediate right of Alice
    3. Dave is not sitting next to Bob
    4. Eve is sitting between Bob and Dave

    Determine the seating arrangement. Think through this step by step.
    """
    
    print("🧩 Logic Puzzle:")
    print(problem.strip())
    print("\n⏳ Generating response with reasoning...")
    
    try:
        result = await generate_text(
            model=model,
            messages=[
                {"role": "user", "content": problem}
            ],
            temperature=0.7  # Gemini supports temperature (unlike o1)
        )
        
        print(f"\n📊 Usage Statistics:")
        print(f"   Prompt tokens: {result.usage.prompt_tokens}")
        print(f"   Completion tokens: {result.usage.completion_tokens}")
        
        if result.usage.reasoning_tokens:
            print(f"   Reasoning tokens: {result.usage.reasoning_tokens}")
            ratio = get_reasoning_token_ratio(result.usage)
            print(f"   Reasoning token ratio: {ratio:.2%}")
        
        print(f"   Total tokens: {result.usage.total_tokens}")
        
        # Check for reasoning content in the response
        reasoning_found = False
        if isinstance(result.content, list):
            reasoning_text = extract_reasoning_text(result.content)
            if reasoning_text:
                reasoning_found = True
                print(f"\n🧠 Gemini's internal reasoning process:")
                print(reasoning_text[:500] + "..." if len(reasoning_text) > 500 else reasoning_text)
                
                # Show provider-specific metadata if available
                for content in result.content:
                    if isinstance(content, ReasoningContent) and content.provider_metadata:
                        google_data = content.provider_metadata.data.get("google", {})
                        if "thoughtSignature" in google_data:
                            print(f"\n🏷️  Thought signature: {google_data['thoughtSignature']}")
        
        if not reasoning_found:
            print(f"\n💭 No explicit reasoning content found (may be embedded in response)")
        
        print(f"\n✨ Response:")
        print(result.text)
        
    except Exception as e:
        print(f"❌ Error with Gemini: {e}")
    
    print("\n" + "-" * 40 + "\n")


async def compare_reasoning_approaches():
    """Compare different reasoning approaches."""
    print("⚖️  Reasoning Model Comparison")
    print("=" * 35)
    
    comparison_problem = """
    You are given the equation: x³ - 6x² + 11x - 6 = 0
    Find all real roots and explain your method.
    """
    
    print("🔢 Mathematical Problem:")
    print(comparison_problem.strip())
    print()
    
    # Test with different providers if available
    providers_to_test = []
    
    if os.getenv("OPENAI_API_KEY"):
        providers_to_test.append(("OpenAI o1-mini", OpenAIProvider(), "o1-mini"))
        
    if os.getenv("GOOGLE_API_KEY"):
        providers_to_test.append(("Gemini 2.5 Flash", GoogleProvider(), "gemini-2.5-flash"))
    
    for name, provider, model_id in providers_to_test:
        try:
            print(f"🔍 Testing {name}...")
            model = provider.language_model(model_id)
            
            result = await generate_text(
                model=model,
                messages=[{"role": "user", "content": comparison_problem}]
            )
            
            print(f"   📊 {name} - Tokens: {result.usage.total_tokens}", end="")
            if result.usage.reasoning_tokens:
                print(f" (reasoning: {result.usage.reasoning_tokens})", end="")
            print()
            
            # Show first few lines of response
            response_lines = result.text.split('\n')[:3]
            for line in response_lines:
                if line.strip():
                    print(f"   📝 {line.strip()[:80]}...")
                    break
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error with {name}: {e}")
    
    print("-" * 35 + "\n")


async def demonstrate_reasoning_utilities():
    """Demonstrate reasoning utility functions."""
    print("🛠️  Reasoning Utilities Demo")
    print("=" * 30)
    
    from ai_sdk.core.reasoning import ReasoningExtractor, add_usage
    from ai_sdk.providers.types import Usage
    
    # Create reasoning extractor
    extractor = ReasoningExtractor()
    
    # Simulate reasoning content
    reasoning1 = extractor.add_reasoning("First, I need to analyze the problem structure...")
    reasoning2 = extractor.add_reasoning("Then I'll consider the constraints and variables...")
    reasoning3 = extractor.add_reasoning("Finally, I'll synthesize the solution...")
    
    print("🧠 Reasoning parts added:")
    for i, part in enumerate(extractor.reasoning_parts, 1):
        print(f"   {i}. {part.text[:50]}...")
    
    combined = extractor.get_combined_reasoning()
    print(f"\n📝 Combined reasoning ({len(combined)} chars):")
    print(combined[:200] + "..." if len(combined) > 200 else combined)
    
    # Usage arithmetic
    usage1 = Usage(prompt_tokens=100, completion_tokens=200, total_tokens=300, reasoning_tokens=50)
    usage2 = Usage(prompt_tokens=80, completion_tokens=150, total_tokens=230, reasoning_tokens=30)
    
    combined_usage = add_usage(usage1, usage2)
    
    print(f"\n➕ Usage combination demo:")
    print(f"   Usage 1: {usage1.total_tokens} total ({usage1.reasoning_tokens} reasoning)")
    print(f"   Usage 2: {usage2.total_tokens} total ({usage2.reasoning_tokens} reasoning)")
    print(f"   Combined: {combined_usage.total_tokens} total ({combined_usage.reasoning_tokens} reasoning)")
    
    if has_reasoning_tokens(combined_usage):
        ratio = get_reasoning_token_ratio(combined_usage)
        print(f"   Reasoning ratio: {ratio:.1%}")
    
    print("\n" + "-" * 30)


def print_setup_instructions():
    """Print setup instructions for the example."""
    print("📋 Setup Instructions")
    print("=" * 25)
    print()
    print("To run this example, you need to set up API keys:")
    print()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
    else:
        print("✅ OPENAI_API_KEY configured")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found") 
        print("   Set it with: export GOOGLE_API_KEY='your-api-key'")
    else:
        print("✅ GOOGLE_API_KEY configured")
    
    print()
    print("💡 Tips:")
    print("   - o1 models are optimized for reasoning but cost more")
    print("   - Reasoning tokens are often charged at different rates")
    print("   - Use reasoning models for complex problem-solving tasks")
    print()
    print("-" * 25 + "\n")


async def main():
    """Run all reasoning demonstrations."""
    print("🧠 AI SDK Python - Reasoning Models Example")
    print("=" * 50)
    print()
    
    print_setup_instructions()
    
    # Demonstrate different reasoning capabilities
    await demonstrate_reasoning_utilities()
    
    if os.getenv("OPENAI_API_KEY"):
        await demonstrate_openai_o1_reasoning()
    else:
        print("⏭️  Skipping OpenAI o1 demo (API key not configured)\n")
    
    if os.getenv("GOOGLE_API_KEY"):
        await demonstrate_gemini_reasoning()
    else:
        print("⏭️  Skipping Gemini demo (API key not configured)\n")
    
    if os.getenv("OPENAI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
        await compare_reasoning_approaches()
    
    print("🎉 Reasoning demonstration complete!")
    print("\n💡 Key takeaways:")
    print("   • Reasoning models excel at complex problem-solving")
    print("   • Different providers have different reasoning approaches")  
    print("   • Monitor reasoning token usage for cost optimization")
    print("   • Extract reasoning content for debugging and analysis")


if __name__ == "__main__":
    asyncio.run(main())