#!/usr/bin/env python3
"""
LMNT Speech Synthesis Example

This example demonstrates how to use the LMNT provider for high-quality text-to-speech 
synthesis with various voices, models, and customization options.

LMNT provides two main models:
- Aurora: Advanced conversational model with full feature support
- Blizzard: Basic speech synthesis model

Set your LMNT_API_KEY environment variable or pass it directly.
"""

import asyncio
import os
from pathlib import Path

from ai_sdk.providers.lmnt import create_lmnt, LMNTProvider


async def basic_speech_synthesis():
    """Basic text-to-speech with LMNT."""
    print("🎯 Basic Speech Synthesis")
    print("=" * 50)
    
    # Create provider
    lmnt = create_lmnt()  # Uses LMNT_API_KEY env var
    
    # Get Aurora model (advanced features)
    model = lmnt.speech("aurora")
    
    # Generate speech
    result = await model.generate(
        text="Welcome to LMNT's advanced speech synthesis technology!",
        voice="ava"  # Default voice
    )
    
    print(f"✅ Generated speech: {len(result.audio.data)} bytes")
    print(f"📊 Format: {result.audio.format}")
    print(f"📡 Sample Rate: {result.audio.sample_rate}Hz")
    
    if result.warnings:
        print(f"⚠️  Warnings: {', '.join(result.warnings)}")
    
    # Save to file
    output_file = "lmnt_basic.mp3"
    with open(output_file, "wb") as f:
        f.write(result.audio.data)
    print(f"💾 Saved to: {output_file}")
    print()


async def conversational_speech():
    """Generate conversational-style speech (Aurora model only)."""
    print("🗣️  Conversational Speech Style")
    print("=" * 50)
    
    lmnt = create_lmnt()
    model = lmnt.speech("aurora")
    
    # Conversational text (more natural for dialogue)
    text = "Hey there! How's your day going? I hope you're having a great time learning about AI!"
    
    result = await model.generate(
        text=text,
        voice="narrator",  # Professional narrator voice
        provider_options={
            "conversational": True,    # Conversational vs reading style
            "speed": 1.1,             # Slightly faster
            "temperature": 0.7,       # More expressive
            "top_p": 0.8,            # Balanced stability/variety
        }
    )
    
    print(f"✅ Generated conversational speech: {len(result.audio.data)} bytes")
    print(f"🎭 Style: Conversational")
    print(f"⚡ Speed: 1.1x")
    
    # Save to file
    output_file = "lmnt_conversational.mp3"
    with open(output_file, "wb") as f:
        f.write(result.audio.data)
    print(f"💾 Saved to: {output_file}")
    print()


async def professional_announcement():
    """Generate professional-style announcement with high quality."""
    print("📢 Professional Announcement")
    print("=" * 50)
    
    lmnt = create_lmnt()
    model = lmnt.speech("aurora")
    
    text = """
    Welcome to the AI-powered conference. Today's presentations will cover 
    the latest advances in natural language processing, computer vision, 
    and machine learning applications.
    """
    
    result = await model.generate(
        text=text.strip(),
        voice="professional_male",  # Professional voice
        output_format="wav",       # High quality WAV format
        provider_options={
            "sample_rate": 24000,   # High sample rate
            "conversational": False, # Reading style
            "speed": 0.95,          # Slightly slower for clarity
            "top_p": 0.3,          # Very consistent
            "length": 30.0,        # Max 30 seconds
        }
    )
    
    print(f"✅ Generated announcement: {len(result.audio.data)} bytes")
    print(f"🎵 Format: WAV (high quality)")
    print(f"📡 Sample Rate: 24kHz")
    print(f"🎯 Style: Professional reading")
    
    # Save to file
    output_file = "lmnt_announcement.wav"
    with open(output_file, "wb") as f:
        f.write(result.audio.data)
    print(f"💾 Saved to: {output_file}")
    print()


async def multi_voice_demo():
    """Demonstrate different voices and languages."""
    print("🌍 Multi-Voice & Language Demo")
    print("=" * 50)
    
    lmnt = create_lmnt()
    model = lmnt.speech("aurora")
    
    # Different voice samples
    voices_and_texts = [
        ("ava", "en", "Hello, I'm Ava. Nice to meet you!"),
        ("narrator", "en", "In a world of endless possibilities..."),
        ("storyteller", "en", "Once upon a time, in a digital realm..."),
        ("professional_female", "en", "Thank you for joining today's presentation."),
    ]
    
    for i, (voice, lang, text) in enumerate(voices_and_texts, 1):
        print(f"🎤 Voice {i}: {voice}")
        
        result = await model.generate(
            text=text,
            voice=voice,
            language=lang,
            provider_options={
                "conversational": "storyteller" in voice,
                "speed": 1.0,
                "format": "mp3",
            }
        )
        
        output_file = f"lmnt_voice_{i}_{voice}.mp3"
        with open(output_file, "wb") as f:
            f.write(result.audio.data)
        
        print(f"   📝 Text: '{text[:30]}...'")
        print(f"   💾 Saved to: {output_file}")
        print(f"   📊 Size: {len(result.audio.data)} bytes")
        print()


async def deterministic_generation():
    """Generate deterministic speech using seed values."""
    print("🎲 Deterministic Generation (with seeds)")
    print("=" * 50)
    
    lmnt = create_lmnt()
    model = lmnt.speech("aurora")
    
    text = "This is a test of deterministic speech generation."
    seed = 42
    
    # Generate the same text twice with same seed
    print(f"🌱 Using seed: {seed}")
    
    results = []
    for i in range(2):
        result = await model.generate(
            text=text,
            voice="ava",
            provider_options={
                "seed": seed,
                "temperature": 0.5,
            }
        )
        results.append(result)
        
        output_file = f"lmnt_deterministic_{i+1}.mp3"
        with open(output_file, "wb") as f:
            f.write(result.audio.data)
        
        print(f"   Generation {i+1}: {len(result.audio.data)} bytes -> {output_file}")
    
    # Check if results are identical
    if results[0].audio.data == results[1].audio.data:
        print("✅ Deterministic generation successful - identical results!")
    else:
        print("⚠️  Results differ (this may be expected with some randomness)")
    print()


async def blizzard_model_demo():
    """Demonstrate the Blizzard model (basic synthesis)."""
    print("❄️  Blizzard Model Demo")
    print("=" * 50)
    
    lmnt = create_lmnt()
    model = lmnt.speech("blizzard")  # Basic model
    
    text = "This is the Blizzard model - a reliable choice for basic speech synthesis."
    
    result = await model.generate(
        text=text,
        voice="ava",
        provider_options={
            "speed": 1.0,
            "format": "mp3",
            # Note: conversational, length, etc. not supported by Blizzard
        }
    )
    
    print(f"✅ Generated with Blizzard model: {len(result.audio.data)} bytes")
    print(f"🔧 Model: Basic synthesis (no advanced features)")
    
    # Save to file
    output_file = "lmnt_blizzard.mp3"
    with open(output_file, "wb") as f:
        f.write(result.audio.data)
    print(f"💾 Saved to: {output_file}")
    print()


async def error_handling_demo():
    """Demonstrate error handling with invalid inputs."""
    print("🚨 Error Handling Demo")
    print("=" * 50)
    
    lmnt = create_lmnt()
    model = lmnt.speech("aurora")
    
    # Test cases with expected errors
    test_cases = [
        ("Text too long", "x" * 5001),  # Over 5000 character limit
        ("Invalid speed", "Hello world", {"speed": 5.0}),  # Speed > 2.0
        ("Invalid top_p", "Hello world", {"top_p": 2.0}),   # top_p > 1.0
    ]
    
    for case_name, text, options in test_cases:
        print(f"🧪 Test: {case_name}")
        try:
            if isinstance(text, str) and len(text) > 100:
                # For long text test
                result = await model.generate(text=text, voice="ava")
            else:
                # For options tests
                result = await model.generate(
                    text=text,
                    voice="ava",
                    provider_options=options or {}
                )
            print(f"   ❌ Expected error but got success: {len(result.audio.data)} bytes")
        except Exception as e:
            print(f"   ✅ Expected error caught: {type(e).__name__}: {str(e)[:60]}...")
        print()


async def format_comparison():
    """Compare different audio formats."""
    print("🎵 Audio Format Comparison")
    print("=" * 50)
    
    lmnt = create_lmnt()
    model = lmnt.speech("aurora")
    
    text = "This is a test of different audio formats."
    formats = ["mp3", "wav", "aac"]  # Most commonly used formats
    
    for fmt in formats:
        print(f"🎼 Format: {fmt.upper()}")
        
        result = await model.generate(
            text=text,
            voice="ava",
            output_format=fmt,
            provider_options={
                "sample_rate": 24000 if fmt != "mp3" else None,  # MP3 doesn't need explicit sample rate
            }
        )
        
        output_file = f"lmnt_format_test.{fmt}"
        with open(output_file, "wb") as f:
            f.write(result.audio.data)
        
        print(f"   📊 Size: {len(result.audio.data):,} bytes")
        print(f"   💾 Saved to: {output_file}")
        print()


async def main():
    """Run all LMNT examples."""
    print("🎤 LMNT Speech Synthesis Examples")
    print("=" * 60)
    print()
    
    # Check API key
    if not os.getenv("LMNT_API_KEY"):
        print("❌ Error: LMNT_API_KEY environment variable not set")
        print("   Please set your LMNT API key:")
        print("   export LMNT_API_KEY='your-api-key-here'")
        return
    
    try:
        # Run examples
        await basic_speech_synthesis()
        await conversational_speech()
        await professional_announcement()
        await multi_voice_demo()
        await deterministic_generation()
        await blizzard_model_demo()
        await format_comparison()
        await error_handling_demo()
        
        print("🎉 All LMNT examples completed successfully!")
        print("\n📁 Generated audio files:")
        
        # List generated files
        audio_files = [
            f for f in os.listdir(".")
            if f.startswith("lmnt_") and f.endswith((".mp3", ".wav", ".aac"))
        ]
        
        for file in sorted(audio_files):
            file_size = os.path.getsize(file)
            print(f"   📄 {file} ({file_size:,} bytes)")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())