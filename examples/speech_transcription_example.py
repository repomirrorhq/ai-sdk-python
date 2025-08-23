"""Example demonstrating speech generation and transcription with AI SDK Python."""

import asyncio
from pathlib import Path

from ai_sdk import create_openai
from ai_sdk.core import generate_speech, transcribe


async def main():
    """Speech generation and transcription examples."""
    
    # Create OpenAI provider
    openai = create_openai()
    
    print("🎵 AI SDK Python - Speech & Transcription Examples")
    print("=" * 55)
    
    # Example 1: Basic speech generation
    print("\n1. Basic Speech Generation (TTS)")
    print("-" * 35)
    
    try:
        speech_model = openai.speech("tts-1")
        result = await generate_speech(
            model=speech_model,
            text="Hello! This is a test of OpenAI's text-to-speech capabilities using AI SDK Python.",
            voice="alloy"
        )
        
        print(f"✅ Generated speech audio ({len(result.audio.data)} bytes)")
        print(f"📊 Audio type: {result.audio.media_type}")
        
        # Save the audio
        with open("generated_speech_1.mp3", "wb") as f:
            f.write(result.audio.data)
        print("💾 Saved as 'generated_speech_1.mp3'")
        
    except Exception as e:
        print(f"❌ Error in basic speech generation: {str(e)}")
    
    # Example 2: Speech generation with different voices and settings
    print("\n2. Advanced Speech Generation")
    print("-" * 32)
    
    voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    for i, voice in enumerate(voices[:3]):  # Test first 3 voices
        try:
            speech_model = openai.speech("tts-1")
            result = await generate_speech(
                model=speech_model,
                text=f"This is the {voice} voice speaking. Each voice has its own unique character and tone.",
                voice=voice,
                speed=1.0
            )
            
            filename = f"generated_speech_voice_{voice}.mp3"
            with open(filename, "wb") as f:
                f.write(result.audio.data)
            
            print(f"✅ Generated speech with {voice} voice ({len(result.audio.data)} bytes)")
            print(f"💾 Saved as '{filename}'")
            
        except Exception as e:
            print(f"❌ Error with {voice} voice: {str(e)}")
    
    # Example 3: High-quality speech generation
    print("\n3. High-Quality Speech Generation")
    print("-" * 37)
    
    try:
        hd_speech_model = openai.speech("tts-1-hd")
        result = await generate_speech(
            model=hd_speech_model,
            text="This is high-definition speech generation using the TTS-1-HD model for improved audio quality.",
            voice="nova",
            speed=0.9,  # Slightly slower for clarity
            provider_options={
                "openai": {
                    "response_format": "mp3"
                }
            }
        )
        
        print(f"✅ Generated HD speech ({len(result.audio.data)} bytes)")
        
        with open("generated_speech_hd.mp3", "wb") as f:
            f.write(result.audio.data)
        print("💾 Saved as 'generated_speech_hd.mp3'")
        
    except Exception as e:
        print(f"❌ Error in HD speech generation: {str(e)}")
    
    # Example 4: Speech transcription
    print("\n4. Speech Transcription (STT)")
    print("-" * 30)
    
    # First, let's create some audio to transcribe (using our generated audio)
    if Path("generated_speech_1.mp3").exists():
        try:
            transcription_model = openai.transcription("whisper-1")
            result = await transcribe(
                model=transcription_model,
                audio="generated_speech_1.mp3"
            )
            
            print(f"✅ Transcribed audio successfully")
            print(f"📝 Transcribed text: \"{result.text}\"")
            print(f"📊 Response metadata: {result.response}")
            
        except Exception as e:
            print(f"❌ Error in transcription: {str(e)}")
    else:
        print("⏭️  Skipping transcription - no audio file available")
    
    # Example 5: Transcription with different parameters
    print("\n5. Advanced Transcription")
    print("-" * 27)
    
    if Path("generated_speech_hd.mp3").exists():
        try:
            transcription_model = openai.transcription("whisper-1")
            result = await transcribe(
                model=transcription_model,
                audio="generated_speech_hd.mp3",
                language="en",  # Specify language for better accuracy
                prompt="This is a transcription of AI-generated speech about text-to-speech capabilities.",
                temperature=0.0  # Lower temperature for more consistent results
            )
            
            print(f"✅ Advanced transcription completed")
            print(f"📝 Transcribed text: \"{result.text}\"")
            
            if result.provider_metadata.get("openai", {}).get("language"):
                print(f"🌐 Detected language: {result.provider_metadata['openai']['language']}")
            
        except Exception as e:
            print(f"❌ Error in advanced transcription: {str(e)}")
    else:
        print("⏭️  Skipping advanced transcription - no HD audio file available")
    
    # Example 6: Error handling
    print("\n6. Error Handling")
    print("-" * 18)
    
    try:
        speech_model = openai.speech("tts-1")
        result = await generate_speech(
            model=speech_model,
            text="",  # Empty text should cause an error
            voice="alloy"
        )
        
    except Exception as e:
        print(f"✅ Properly caught speech generation error: {type(e).__name__}: {str(e)}")
    
    try:
        transcription_model = openai.transcription("whisper-1")
        result = await transcribe(
            model=transcription_model,
            audio=b"invalid audio data"  # Invalid audio should cause an error
        )
        
    except Exception as e:
        print(f"✅ Properly caught transcription error: {type(e).__name__}: {str(e)}")
    
    print(f"\n🎉 Speech and transcription examples completed!")
    print("Check the current directory for generated MP3 files.")


def sync_example():
    """Synchronous examples using sync versions."""
    from ai_sdk.core import generate_speech_sync, transcribe_sync
    
    print("\n🔄 Synchronous Speech/Transcription")
    print("-" * 38)
    
    try:
        openai = create_openai()
        speech_model = openai.speech("tts-1")
        
        result = generate_speech_sync(
            model=speech_model,
            text="This is a synchronous speech generation example.",
            voice="echo"
        )
        
        print(f"✅ Synchronously generated speech ({len(result.audio.data)} bytes)")
        
        with open("sync_generated_speech.mp3", "wb") as f:
            f.write(result.audio.data)
        print("💾 Saved as 'sync_generated_speech.mp3'")
        
        # Try to transcribe it back
        transcription_model = openai.transcription("whisper-1")
        transcription_result = transcribe_sync(
            model=transcription_model,
            audio="sync_generated_speech.mp3"
        )
        
        print(f"✅ Synchronously transcribed speech")
        print(f"📝 Transcribed text: \"{transcription_result.text}\"")
        
    except Exception as e:
        print(f"❌ Error in sync speech/transcription: {str(e)}")


if __name__ == "__main__":
    # Run async examples
    asyncio.run(main())
    
    # Run sync example
    sync_example()