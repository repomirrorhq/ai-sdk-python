#!/usr/bin/env python3
"""
ElevenLabs Provider Example

This example demonstrates how to use the ElevenLabs provider for:
1. Text-to-speech synthesis with custom voice settings
2. Speech-to-text transcription with speaker diarization
3. Advanced features like voice cloning and context awareness

Make sure to set your ElevenLabs API key:
export ELEVENLABS_API_KEY="your-api-key-here"
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Optional

from ai_sdk.providers.elevenlabs import ElevenLabsProvider


async def speech_synthesis_examples():
    """Demonstrate ElevenLabs speech synthesis capabilities."""
    print("🎤 ElevenLabs Speech Synthesis Examples")
    print("=" * 50)
    
    # Initialize provider
    provider = ElevenLabsProvider()
    
    # Get speech model
    speech_model = provider.speech("eleven_v3")  # Latest multilingual model
    
    # Example 1: Basic speech synthesis
    print("\n1. Basic Speech Synthesis")
    print("-" * 30)
    
    try:
        result = await speech_model.generate(
            text="Hello! This is a demonstration of ElevenLabs speech synthesis.",
            voice="21m00Tcm4TlvDq8ikWAM",  # Rachel (default voice)
        )
        
        print(f"✅ Generated speech:")
        print(f"   Model: {result.model_id}")
        print(f"   Audio format: {result.audio.format}")
        print(f"   Audio size: {len(result.audio.data)} bytes")
        print(f"   Sample rate: {result.audio.sample_rate} Hz")
        
        # Save audio file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(result.audio.data)
            print(f"   Saved to: {f.name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Custom voice settings
    print("\n2. Custom Voice Settings")
    print("-" * 30)
    
    try:
        result = await speech_model.generate(
            text="This voice has been customized for stability, clarity, and style.",
            voice="21m00Tcm4TlvDq8ikWAM",
            speed=1.1,  # Slightly faster
            provider_options={
                "voice_settings": {
                    "stability": 0.7,      # More stable voice
                    "similarity_boost": 0.6,  # Closer to original voice
                    "style": 0.4,          # More expressive
                    "use_speaker_boost": True,
                },
                "language_code": "en",
            }
        )
        
        print(f"✅ Generated custom voice speech:")
        print(f"   Audio size: {len(result.audio.data)} bytes")
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(result.audio.data)
            print(f"   Saved to: {f.name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: Different output formats
    print("\n3. Different Output Formats")
    print("-" * 30)
    
    formats = ["mp3_44100_128", "wav", "pcm_44100"]
    text = "Testing different audio formats."
    
    for fmt in formats:
        try:
            result = await speech_model.generate(
                text=text,
                voice="21m00Tcm4TlvDq8ikWAM",
                output_format=fmt,
            )
            
            print(f"✅ {fmt}: {len(result.audio.data)} bytes")
            
        except Exception as e:
            print(f"❌ {fmt}: Error - {e}")
    
    # Example 4: Multilingual synthesis
    print("\n4. Multilingual Synthesis")
    print("-" * 30)
    
    multilingual_texts = [
        ("Hello, how are you today?", "en"),
        ("Hola, ¿cómo estás hoy?", "es"),
        ("Bonjour, comment allez-vous aujourd'hui?", "fr"),
        ("Hallo, wie geht es dir heute?", "de"),
    ]
    
    for text, lang_code in multilingual_texts:
        try:
            result = await speech_model.generate(
                text=text,
                voice="21m00Tcm4TlvDq8ikWAM",
                language=lang_code,
            )
            
            print(f"✅ {lang_code}: Generated {len(result.audio.data)} bytes")
            
        except Exception as e:
            print(f"❌ {lang_code}: Error - {e}")
    
    # Example 5: Context-aware synthesis
    print("\n5. Context-Aware Synthesis")
    print("-" * 30)
    
    try:
        # Generate with context for better flow
        result = await speech_model.generate(
            text="This is the main content of our conversation.",
            voice="21m00Tcm4TlvDq8ikWAM",
            provider_options={
                "previous_text": "Welcome to our discussion.",
                "next_text": "Let's explore this topic further.",
                "seed": 42,  # For reproducible results
            }
        )
        
        print(f"✅ Context-aware speech generated: {len(result.audio.data)} bytes")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def transcription_examples():
    """Demonstrate ElevenLabs transcription capabilities."""
    print("\n\n🎧 ElevenLabs Transcription Examples")
    print("=" * 50)
    
    # Initialize provider
    provider = ElevenLabsProvider()
    
    # Get transcription model
    transcription_model = provider.transcription("scribe_v1")
    
    # Note: For real examples, you would need actual audio files
    # This example shows the API structure
    
    print("\n1. Basic Transcription (API structure)")
    print("-" * 30)
    print("# Example audio file transcription:")
    print("# with open('audio.mp3', 'rb') as f:")
    print("#     audio_data = f.read()")
    print("# ")
    print("# result = await transcription_model.transcribe(")
    print("#     audio=audio_data,")
    print("#     media_type='audio/mp3'")
    print("# )")
    print("# ")
    print("# print(f'Transcribed text: {result.text}')")
    print("# print(f'Language: {result.language}')")
    print("# print(f'Duration: {result.duration_seconds}s')")
    
    print("\n2. Advanced Transcription with Diarization (API structure)")
    print("-" * 30)
    print("# result = await transcription_model.transcribe(")
    print("#     audio=audio_data,")
    print("#     media_type='audio/mp3',")
    print("#     provider_options={")
    print("#         'diarize': True,")
    print("#         'num_speakers': 2,")
    print("#         'timestamps_granularity': 'word',")
    print("#         'tag_audio_events': True,")
    print("#         'language_code': 'en',")
    print("#     }")
    print("# )")
    print("# ")
    print("# for segment in result.segments:")
    print("#     print(f'{segment.start_time:.2f}s - {segment.end_time:.2f}s: {segment.text}')")
    print("#     if segment.speaker_id:")
    print("#         print(f'  Speaker: {segment.speaker_id}')")
    
    print("\n3. Supported File Formats")
    print("-" * 30)
    formats = [
        ("MP3", "audio/mp3"),
        ("WAV", "audio/wav"), 
        ("M4A", "audio/mp4"),
        ("FLAC", "audio/flac"),
        ("OGG", "audio/ogg"),
        ("WebM", "audio/webm"),
    ]
    
    for fmt_name, media_type in formats:
        print(f"✅ {fmt_name}: {media_type}")
    
    print("\n4. Transcription Options")
    print("-" * 30)
    options = [
        ("Language Detection", "Automatic language detection with confidence scores"),
        ("Speaker Diarization", "Identify different speakers in the audio"),
        ("Timestamp Granularity", "Word-level or character-level timestamps"),
        ("Audio Event Tagging", "Tag events like laughter, applause, etc."),
        ("Multi-speaker Support", "Handle up to 32 speakers"),
        ("High Accuracy", "Advanced speech recognition models"),
    ]
    
    for feature, description in options:
        print(f"✅ {feature}: {description}")


async def advanced_features_examples():
    """Demonstrate advanced ElevenLabs features."""
    print("\n\n🚀 Advanced ElevenLabs Features")
    print("=" * 50)
    
    provider = ElevenLabsProvider()
    
    # Example 1: Voice analysis and selection
    print("\n1. Voice Selection Guide")
    print("-" * 30)
    
    voices = [
        ("21m00Tcm4TlvDq8ikWAM", "Rachel", "American English, calm and clear"),
        ("AZnzlk1XvdvUeBnXmlld", "Domi", "American English, confident"),
        ("EXAVITQu4vr4xnSDxMaL", "Bella", "American English, engaging"),
        ("ErXwobaYiN019PkySvjV", "Antoni", "American English, well-rounded"),
        ("MF3mGyEYCl7XYWbV9V6O", "Elli", "American English, emotional"),
        ("TxGEqnHWrfWFTfGW9XjX", "Josh", "American English, deep"),
    ]
    
    for voice_id, name, description in voices:
        print(f"✅ {name} ({voice_id}): {description}")
    
    # Example 2: Production best practices
    print("\n2. Production Best Practices")
    print("-" * 30)
    
    best_practices = [
        "Use consistent voice settings across your application",
        "Cache generated audio for repeated content",
        "Implement proper error handling and retries",
        "Monitor API usage and implement rate limiting",
        "Use context (previous_text/next_text) for better flow",
        "Choose appropriate output format for your use case",
        "Test with different languages if building multilingual apps",
        "Consider voice cloning for brand-specific voices",
    ]
    
    for i, practice in enumerate(best_practices, 1):
        print(f"{i}. {practice}")
    
    # Example 3: Error handling patterns
    print("\n3. Error Handling Example")
    print("-" * 30)
    print("from ai_sdk.errors import APICallError, AISDKError")
    print("")
    print("try:")
    print("    result = await speech_model.generate(text='Hello world')")
    print("except APICallError as e:")
    print("    print(f'API error: {e.message}')")
    print("    print(f'Status code: {e.status_code}')")
    print("except AISDKError as e:")
    print("    print(f'SDK error: {e}')")
    print("except Exception as e:")
    print("    print(f'Unexpected error: {e}')")


async def integration_examples():
    """Show how to integrate ElevenLabs with other AI SDK features."""
    print("\n\n🔗 Integration Examples")
    print("=" * 50)
    
    print("\n1. Voice Assistant Pipeline")
    print("-" * 30)
    print("# Combine with OpenAI for a complete voice assistant")
    print("from ai_sdk import OpenAI")
    print("from ai_sdk.providers.elevenlabs import ElevenLabsProvider")
    print("")
    print("async def voice_assistant(user_audio):")
    print("    # 1. Transcribe user input")
    print("    elevenlabs = ElevenLabsProvider()")
    print("    transcription = await elevenlabs.transcription('scribe_v1').transcribe(user_audio)")
    print("    ")
    print("    # 2. Generate response with OpenAI")
    print("    openai = OpenAI()")
    print("    response = await openai.language_model('gpt-4').generate(")
    print("        messages=[{'role': 'user', 'content': transcription.text}]")
    print("    )")
    print("    ")
    print("    # 3. Convert response to speech")
    print("    speech = await elevenlabs.speech('eleven_v3').generate(")
    print("        text=response.text")
    print("    )")
    print("    ")
    print("    return speech.audio")
    
    print("\n2. Content Generation Pipeline")
    print("-" * 30)
    print("# Generate content and convert to multiple formats")
    print("async def content_to_audio_pipeline(topic):")
    print("    # Generate article with OpenAI")
    print("    openai = OpenAI()")
    print("    article = await openai.language_model('gpt-4').generate(")
    print("        messages=[{'role': 'user', 'content': f'Write an article about {topic}'}]")
    print("    )")
    print("    ")
    print("    # Convert to speech with different voices")
    print("    elevenlabs = ElevenLabsProvider()")
    print("    speech_model = elevenlabs.speech('eleven_v3')")
    print("    ")
    print("    # Narrator voice")
    print("    audio = await speech_model.generate(")
    print("        text=article.text,")
    print("        voice='21m00Tcm4TlvDq8ikWAM',  # Rachel")
    print("        provider_options={'voice_settings': {'stability': 0.8}}")
    print("    )")
    print("    ")
    print("    return audio")
    
    print("\n3. Podcast Generation")
    print("-" * 30)
    print("# Create multi-speaker podcast content")
    print("async def generate_podcast(script_segments):")
    print("    elevenlabs = ElevenLabsProvider()")
    print("    speech_model = elevenlabs.speech('eleven_v3')")
    print("    ")
    print("    audio_segments = []")
    print("    for segment in script_segments:")
    print("        audio = await speech_model.generate(")
    print("            text=segment['text'],")
    print("            voice=segment['voice_id'],")
    print("            provider_options={")
    print("                'voice_settings': segment['voice_settings'],")
    print("                'previous_text': segment.get('context'),")
    print("            }")
    print("        )")
    print("        audio_segments.append(audio.audio.data)")
    print("    ")
    print("    # Combine segments (would need audio processing library)")
    print("    return audio_segments")


async def main():
    """Run all ElevenLabs examples."""
    print("🎵 ElevenLabs AI Provider - Comprehensive Examples")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("❌ Please set your ELEVENLABS_API_KEY environment variable")
        print("   export ELEVENLABS_API_KEY='your-api-key-here'")
        print("\n   You can get your API key from: https://elevenlabs.io/app/settings")
        return
    
    try:
        # Run examples
        await speech_synthesis_examples()
        await transcription_examples()
        await advanced_features_examples()
        await integration_examples()
        
        print("\n\n🎉 All ElevenLabs examples completed!")
        print("=" * 60)
        
        print("\nNext Steps:")
        print("1. Try the examples with your own audio files")
        print("2. Experiment with different voices and settings")
        print("3. Integrate ElevenLabs with your applications")
        print("4. Explore voice cloning for custom voices")
        print("5. Build voice assistants and audio applications")
        
    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())