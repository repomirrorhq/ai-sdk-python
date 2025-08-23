#!/usr/bin/env python3
"""
Example demonstrating the Anthropic provider for AI SDK Python.

This example shows how to use Claude models for text generation,
streaming, and tool calling.

Make sure to set your ANTHROPIC_API_KEY environment variable:
export ANTHROPIC_API_KEY="your-anthropic-api-key"
"""

import asyncio
import os
from ai_sdk import generate_text, stream_text, create_anthropic
from ai_sdk.core.types import Message, Content


async def main():
    """Run Anthropic provider examples."""
    
    # Check if API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        print("Please set your Anthropic API key:")
        print("export ANTHROPIC_API_KEY='your-anthropic-api-key'")
        return
    
    # Create Anthropic provider
    anthropic = create_anthropic()
    model = anthropic.language_model("claude-3-sonnet-20240229")
    
    print("🤖 Anthropic Claude Examples")
    print("=" * 50)
    
    # Example 1: Simple text generation
    print("\n1️⃣ Simple Text Generation")
    print("-" * 30)
    
    try:
        result = await generate_text(
            model=model,
            prompt="Explain quantum computing in simple terms."
        )
        print(f"✅ Generated text ({result.usage.total_tokens} tokens):")
        print(f"📝 {result.text[:200]}...")
        print(f"🏁 Finish reason: {result.finish_reason}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Conversation with system message
    print("\n2️⃣ Conversation with System Message")
    print("-" * 30)
    
    messages = [
        Message(
            role="system",
            content=[Content(type="text", text="You are a helpful Python programming assistant. Keep responses concise and practical.")]
        ),
        Message(
            role="user", 
            content=[Content(type="text", text="How do I handle exceptions in Python?")]
        )
    ]
    
    try:
        result = await generate_text(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
        )
        print(f"✅ Assistant response ({result.usage.total_tokens} tokens):")
        print(f"📝 {result.text[:300]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: Streaming text generation
    print("\n3️⃣ Streaming Text Generation")
    print("-" * 30)
    
    try:
        stream_result = await stream_text(
            model=model,
            prompt="Write a short story about a robot learning to paint.",
            max_tokens=200,
        )
        
        print("🔄 Streaming response:")
        full_text = ""
        async for part in stream_result.stream:
            if part.type == "text-delta":
                print(part.text_delta, end="", flush=True)
                full_text += part.text_delta
            elif part.type == "finish":
                print(f"\n✅ Stream finished: {part.finish_reason}")
                if part.usage:
                    print(f"📊 Total tokens: {part.usage.total_tokens}")
        
        print(f"\n📝 Complete text length: {len(full_text)} characters")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 4: Multi-turn conversation
    print("\n4️⃣ Multi-turn Conversation")
    print("-" * 30)
    
    conversation = [
        Message(
            role="user",
            content=[Content(type="text", text="What's the capital of France?")]
        )
    ]
    
    try:
        # First turn
        result = await generate_text(
            model=model,
            messages=conversation,
            max_tokens=100,
        )
        
        print(f"👤 User: What's the capital of France?")
        print(f"🤖 Claude: {result.text}")
        
        # Add assistant response to conversation
        conversation.append(Message(
            role="assistant",
            content=[Content(type="text", text=result.text)]
        ))
        
        # Second turn
        conversation.append(Message(
            role="user",
            content=[Content(type="text", text="What's interesting about its architecture?")]
        ))
        
        result = await generate_text(
            model=model,
            messages=conversation,
            max_tokens=200,
        )
        
        print(f"👤 User: What's interesting about its architecture?")
        print(f"🤖 Claude: {result.text[:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 5: Different Claude models
    print("\n5️⃣ Different Claude Models")
    print("-" * 30)
    
    models_to_try = [
        ("claude-3-haiku-20240307", "Claude 3 Haiku (fast, cost-effective)"),
        ("claude-3-sonnet-20240229", "Claude 3 Sonnet (balanced)"),
        # ("claude-3-opus-20240229", "Claude 3 Opus (most capable)")  # Uncomment if you have access
    ]
    
    for model_id, description in models_to_try:
        try:
            test_model = anthropic.language_model(model_id)
            result = await generate_text(
                model=test_model,
                prompt="Say hello in French and explain the phrase briefly.",
                max_tokens=100,
            )
            print(f"✅ {description}:")
            print(f"   {result.text[:100]}...")
            print(f"   Tokens: {result.usage.total_tokens}")
            
        except Exception as e:
            print(f"❌ {description}: {e}")
    
    # Example 6: Advanced parameters
    print("\n6️⃣ Advanced Parameters")
    print("-" * 30)
    
    try:
        result = await generate_text(
            model=model,
            prompt="Write a creative short poem about programming.",
            temperature=0.9,  # High creativity
            top_p=0.9,
            top_k=40,
            max_tokens=150,
            stop_sequences=["The End"]
        )
        
        print(f"✅ Creative poem (temp=0.9):")
        print(f"📝 {result.text}")
        print(f"🎯 Stop reason: {result.finish_reason}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🎉 Anthropic Claude examples completed!")
    print("💡 Try experimenting with different models and parameters.")


if __name__ == "__main__":
    asyncio.run(main())