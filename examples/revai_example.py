"""RevAI transcription example.

This example demonstrates how to use the RevAI provider for speech-to-text transcription.
"""

import asyncio
import os
from ai_sdk import create_revai, transcribe

async def main():
    """Main example function."""
    
    # Create RevAI provider
    # Requires REVAI_API_KEY environment variable to be set
    try:
        revai_provider = create_revai()
        print("✓ RevAI provider created successfully")
    except Exception as e:
        print(f"✗ Failed to create RevAI provider: {e}")
        print("Make sure to set REVAI_API_KEY environment variable")
        return
    
    # Create transcription model
    # Available models: 'machine', 'low_cost', 'fusion'
    try:
        transcription_model = await revai_provider.transcription_model("machine")
        print("✓ RevAI transcription model created successfully")
    except Exception as e:
        print(f"✗ Failed to create transcription model: {e}")
        return
    
    # Example: Transcribe audio file (if available)
    audio_file_path = "examples/sample_audio.wav"  # Replace with actual audio file
    if os.path.exists(audio_file_path):
        try:
            print(f"📄 Transcribing audio file: {audio_file_path}")
            
            with open(audio_file_path, "rb") as f:
                audio_data = f.read()
            
            # Transcribe with RevAI
            result = await transcribe(
                model=transcription_model,
                audio=audio_data,
                media_type="audio/wav"
            )
            
            print(f"📝 Transcription result:")
            print(f"   Text: {result.text}")
            print(f"   Language: {result.language}")
            print(f"   Duration: {result.duration_seconds}s")
            print(f"   Segments: {len(result.segments)}")
            
            # Show first few segments
            for i, segment in enumerate(result.segments[:3]):
                print(f"   Segment {i+1}: '{segment.text}' [{segment.start_second:.2f}s - {segment.end_second:.2f}s]")
                
        except Exception as e:
            print(f"✗ Transcription failed: {e}")
    else:
        print(f"ℹ️  Audio file not found: {audio_file_path}")
        print("   To test transcription, add a WAV audio file at that path")
    
    # Example: Test advanced options
    print("\n🔧 Available RevAI transcription options:")
    print("   - verbatim: Include filler words and false starts")
    print("   - speaker_diarization: Identify different speakers")
    print("   - custom_vocabulary: Boost recognition of specific terms")
    print("   - summarization_config: Generate summaries")
    print("   - translation_config: Translate to other languages")
    print("   - filter_profanity: Filter out profanity")
    print("   - remove_disfluencies: Remove 'um', 'uh', etc.")
    
    print("\n✅ RevAI provider example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())