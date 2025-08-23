#!/usr/bin/env python3
"""
Enhanced Streaming Examples

This example demonstrates advanced streaming features including:
- Smooth streaming with configurable delays and chunking
- Custom chunking strategies (word, sentence, character-based)
- Performance comparisons between smooth and regular streaming
- Real-time typing effects for better UX

Requirements:
- Set appropriate API keys for the provider you want to test
- For OpenAI: OPENAI_API_KEY
- For Anthropic: ANTHROPIC_API_KEY
"""

import asyncio
import time
from ai_sdk import stream_text
from ai_sdk.providers.openai import create_openai
from ai_sdk.providers.anthropic import create_anthropic
from ai_sdk.streaming import smooth_stream, word_chunker, sentence_chunker, character_chunker


async def demo_regular_streaming():
    """Demo regular streaming without smoothing"""
    print("=== Regular Streaming (No Smoothing) ===\n")
    
    try:
        openai = create_openai()
        model = openai.chat_model("gpt-4-turbo")
        
        start_time = time.time()
        text_parts = []
        
        stream = stream_text(
            model=model,
            prompt="Write a short paragraph about the benefits of AI streaming interfaces.",
            max_tokens=150
        )
        
        async for chunk in stream:
            if chunk.type == "text-delta":
                text_delta = getattr(chunk, 'text_delta', '')
                text_parts.append(text_delta)
                print(text_delta, end="", flush=True)
        
        elapsed = time.time() - start_time
        total_text = ''.join(text_parts)
        print(f"\n\nRegular streaming completed in {elapsed:.2f}s")
        print(f"Generated {len(total_text)} characters\n")
        
    except Exception as e:
        print(f"Error with regular streaming: {e}\n")


async def demo_smooth_streaming():
    """Demo smooth streaming with word-by-word output"""
    print("=== Smooth Streaming (Word-by-Word) ===\n")
    
    try:
        openai = create_openai()
        model = openai.chat_model("gpt-4-turbo")
        
        # Create smooth streaming transform
        smooth_transform = smooth_stream(delay_ms=50, chunking="word")
        
        start_time = time.time()
        text_parts = []
        
        stream = stream_text(
            model=model,
            prompt="Write a short paragraph about the benefits of AI streaming interfaces.",
            max_tokens=150
        )
        
        # Apply smooth streaming
        smooth_stream_iter = smooth_transform(stream)
        
        async for chunk in smooth_stream_iter:
            if chunk.type == "text-delta":
                text_delta = getattr(chunk, 'text_delta', '')
                text_parts.append(text_delta)
                print(text_delta, end="", flush=True)
        
        elapsed = time.time() - start_time
        total_text = ''.join(text_parts)
        print(f"\n\nSmooth streaming completed in {elapsed:.2f}s")
        print(f"Generated {len(total_text)} characters\n")
        
    except Exception as e:
        print(f"Error with smooth streaming: {e}\n")


async def demo_sentence_streaming():
    """Demo streaming with sentence-by-sentence output"""
    print("=== Sentence-by-Sentence Streaming ===\n")
    
    try:
        openai = create_openai()
        model = openai.chat_model("gpt-4-turbo")
        
        # Create sentence-based streaming transform
        smooth_transform = smooth_stream(delay_ms=200, chunking=sentence_chunker)
        
        stream = stream_text(
            model=model,
            prompt="Explain artificial intelligence in 3 sentences.",
            max_tokens=100
        )
        
        # Apply sentence streaming
        smooth_stream_iter = smooth_transform(stream)
        
        async for chunk in smooth_stream_iter:
            if chunk.type == "text-delta":
                text_delta = getattr(chunk, 'text_delta', '')
                print(f"[SENTENCE] {text_delta}")
                
    except Exception as e:
        print(f"Error with sentence streaming: {e}\n")


async def demo_character_streaming():
    """Demo character-by-character streaming for typewriter effect"""
    print("=== Character-by-Character Typewriter Effect ===\n")
    
    try:
        openai = create_openai()
        model = openai.chat_model("gpt-4-turbo")
        
        # Create character-based streaming (typewriter effect)
        char_chunker = character_chunker(1)
        smooth_transform = smooth_stream(delay_ms=20, chunking=char_chunker)
        
        stream = stream_text(
            model=model,
            prompt="Hello, world! This is a typewriter effect demo.",
            max_tokens=50
        )
        
        # Apply character streaming
        smooth_stream_iter = smooth_transform(stream)
        
        print("Typewriter effect: ", end="", flush=True)
        async for chunk in smooth_stream_iter:
            if chunk.type == "text-delta":
                text_delta = getattr(chunk, 'text_delta', '')
                print(text_delta, end="", flush=True)
        
        print("\n")
        
    except Exception as e:
        print(f"Error with character streaming: {e}\n")


async def demo_custom_chunking():
    """Demo custom chunking strategies"""
    print("=== Custom Chunking Strategies ===\n")
    
    try:
        openai = create_openai()
        model = openai.chat_model("gpt-4-turbo")
        
        # Custom chunker that breaks on punctuation
        def punctuation_chunker(buffer: str) -> str:
            import re
            match = re.search(r'[^,.;!?]*[,.;!?]+\s*', buffer)
            if not match:
                return None
            return buffer[:match.end()]
        
        smooth_transform = smooth_stream(delay_ms=100, chunking=punctuation_chunker)
        
        stream = stream_text(
            model=model,
            prompt="List three benefits of AI: 1) efficiency, 2) accuracy, 3) scalability.",
            max_tokens=100
        )
        
        # Apply custom streaming
        smooth_stream_iter = smooth_transform(stream)
        
        print("Punctuation-based chunking:\n")
        async for chunk in smooth_stream_iter:
            if chunk.type == "text-delta":
                text_delta = getattr(chunk, 'text_delta', '')
                print(f"[CHUNK] {text_delta.strip()}")
        
    except Exception as e:
        print(f"Error with custom chunking: {e}\n")


async def demo_anthropic_smooth_streaming():
    """Demo smooth streaming with Anthropic Claude"""
    print("=== Anthropic Claude with Smooth Streaming ===\n")
    
    try:
        anthropic = create_anthropic()
        model = anthropic.chat_model("claude-3-sonnet-20240229")
        
        smooth_transform = smooth_stream(delay_ms=30, chunking="word")
        
        stream = stream_text(
            model=model,
            prompt="Write a haiku about streaming AI.",
            max_tokens=50
        )
        
        smooth_stream_iter = smooth_transform(stream)
        
        print("Anthropic Claude haiku with smooth streaming:\n")
        async for chunk in smooth_stream_iter:
            if chunk.type == "text-delta":
                text_delta = getattr(chunk, 'text_delta', '')
                print(text_delta, end="", flush=True)
        
        print("\n")
        
    except Exception as e:
        print(f"Error with Anthropic streaming: {e}\n")


async def demo_multi_speed_streaming():
    """Demo different streaming speeds"""
    print("=== Multi-Speed Streaming Comparison ===\n")
    
    speeds = [
        ("Very Fast", 5),
        ("Fast", 20), 
        ("Normal", 50),
        ("Slow", 100),
        ("Very Slow", 200)
    ]
    
    try:
        openai = create_openai()
        model = openai.chat_model("gpt-4-turbo")
        
        for speed_name, delay_ms in speeds:
            print(f"--- {speed_name} ({delay_ms}ms delay) ---")
            
            smooth_transform = smooth_stream(delay_ms=delay_ms, chunking="word")
            
            stream = stream_text(
                model=model,
                prompt="Quick brown fox jumps over lazy dog.",
                max_tokens=30
            )
            
            smooth_stream_iter = smooth_transform(stream)
            
            start_time = time.time()
            async for chunk in smooth_stream_iter:
                if chunk.type == "text-delta":
                    text_delta = getattr(chunk, 'text_delta', '')
                    print(text_delta, end="", flush=True)
            
            elapsed = time.time() - start_time
            print(f" (took {elapsed:.2f}s)")
            print()
        
    except Exception as e:
        print(f"Error with multi-speed streaming: {e}\n")


async def main():
    """Run all streaming demos"""
    print("🚀 Enhanced Streaming Examples for AI SDK Python\n")
    print("This demo showcases various streaming strategies for better UX.\n")
    
    demos = [
        ("Regular Streaming", demo_regular_streaming),
        ("Smooth Streaming", demo_smooth_streaming),
        ("Sentence Streaming", demo_sentence_streaming),
        ("Character Streaming", demo_character_streaming),
        ("Custom Chunking", demo_custom_chunking),
        ("Anthropic Streaming", demo_anthropic_smooth_streaming),
        ("Multi-Speed Streaming", demo_multi_speed_streaming),
    ]
    
    for name, demo_func in demos:
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print('='*60)
        
        try:
            await demo_func()
        except Exception as e:
            print(f"Demo '{name}' failed: {e}")
        
        # Small pause between demos
        await asyncio.sleep(1)
    
    print("\n✨ All streaming demos completed!")
    print("\nKey takeaways:")
    print("- Smooth streaming improves perceived performance")
    print("- Word-by-word streaming feels more natural than dumping all text")
    print("- Character streaming creates typewriter effects")  
    print("- Custom chunking enables creative streaming strategies")
    print("- Delay timing affects user experience significantly")


if __name__ == "__main__":
    import os
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  No API keys found!")
        print("Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY environment variables")
        print("Example: export OPENAI_API_KEY=your_key_here")
        exit(1)
    
    asyncio.run(main())