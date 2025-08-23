"""AssemblyAI transcription example."""

import asyncio
from pathlib import Path
from ai_sdk.providers.assemblyai import create_assemblyai, AssemblyAITranscriptionSettings


async def basic_transcription_example():
    """Basic transcription example."""
    print("=== Basic AssemblyAI Transcription ===")
    
    # Create provider (requires ASSEMBLYAI_API_KEY environment variable)
    provider = create_assemblyai()
    
    # Create transcription model
    model = provider.transcription("best")
    
    # Example audio file path (you'll need to provide your own audio file)
    audio_file = Path("path/to/your/audio.mp3")
    
    if not audio_file.exists():
        print(f"Audio file not found: {audio_file}")
        print("Please provide a valid audio file path")
        return
    
    try:
        # Read audio file
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        
        # Transcribe audio
        print("Transcribing audio...")
        result = await model.transcribe(audio_data)
        
        print(f"Transcription: {result.text}")
        print(f"Language: {result.language}")
        print(f"Duration: {result.duration_seconds}s")
        
        if result.segments:
            print(f"Number of word segments: {len(result.segments)}")
            print("First 5 segments:")
            for segment in result.segments[:5]:
                print(f"  {segment.start_second:.2f}s-{segment.end_second:.2f}s: {segment.text}")
        
    except Exception as e:
        print(f"Transcription error: {e}")


async def advanced_transcription_example():
    """Advanced transcription with speaker diarization and analysis."""
    print("\n=== Advanced AssemblyAI Transcription ===")
    
    provider = create_assemblyai()
    model = provider.transcription("best")
    
    # Configure advanced transcription options
    options = AssemblyAITranscriptionSettings(
        # Speaker identification
        speaker_labels=True,
        speakers_expected=2,
        
        # Content analysis
        sentiment_analysis=True,
        auto_chapters=True,
        auto_highlights=True,
        entity_detection=True,
        
        # Language processing  
        language_detection=True,
        format_text=True,
        punctuate=True,
        filter_profanity=True,
        
        # Audio processing
        disfluencies=False,  # Remove "um", "uh" etc.
        
        # Summarization
        summarization=True,
        summary_model="informative",
        summary_type="bullets",
        
        # Custom vocabulary
        word_boost=["AI", "machine learning", "Python", "AssemblyAI"],
    )
    
    # Example audio file path
    audio_file = Path("path/to/your/interview.mp3")
    
    if not audio_file.exists():
        print(f"Audio file not found: {audio_file}")
        print("Please provide a valid audio file path for advanced example")
        return
    
    try:
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        
        print("Transcribing with advanced options...")
        result = await model.transcribe(audio_data, options=options)
        
        print(f"Transcription: {result.text}")
        print(f"Detected Language: {result.language}")
        print(f"Duration: {result.duration_seconds}s")
        
        # The response object contains additional AssemblyAI-specific data
        response_data = result.response
        print(f"Raw response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'N/A'}")
        
    except Exception as e:
        print(f"Advanced transcription error: {e}")


async def pii_redaction_example():
    """Example of PII redaction capabilities."""
    print("\n=== PII Redaction Example ===")
    
    provider = create_assemblyai()
    model = provider.transcription("best")
    
    # Configure PII redaction
    options = AssemblyAITranscriptionSettings(
        redact_pii=True,
        redact_pii_policies=[
            "person_name",
            "phone_number", 
            "email_address",
            "credit_card_number",
            "ssn",
            "date_of_birth",
            "medical_condition",
        ],
        redact_pii_sub="entity_name",  # or "hash"
        
        # Also generate redacted audio file
        redact_pii_audio=True,
        redact_pii_audio_quality="mp3",
    )
    
    # Example audio with PII
    audio_file = Path("path/to/audio/with/pii.mp3")
    
    if not audio_file.exists():
        print(f"Audio file not found: {audio_file}")
        print("Please provide a valid audio file for PII redaction example")
        return
    
    try:
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        
        print("Transcribing with PII redaction...")
        result = await model.transcribe(audio_data, options=options)
        
        print(f"Redacted Transcription: {result.text}")
        print("PII has been replaced with entity names or hashes")
        
    except Exception as e:
        print(f"PII redaction error: {e}")


async def multilingual_example():
    """Example with automatic language detection."""
    print("\n=== Multilingual Transcription ===")
    
    provider = create_assemblyai()
    model = provider.transcription("best")
    
    # Configure for multilingual content
    options = AssemblyAITranscriptionSettings(
        language_detection=True,
        language_confidence_threshold=0.7,
        format_text=True,
        punctuate=True,
    )
    
    # Example with non-English audio
    audio_files = [
        "path/to/spanish.mp3",
        "path/to/french.mp3", 
        "path/to/german.mp3",
    ]
    
    for audio_path in audio_files:
        audio_file = Path(audio_path)
        if not audio_file.exists():
            print(f"Skipping {audio_path} - file not found")
            continue
        
        try:
            with open(audio_file, "rb") as f:
                audio_data = f.read()
            
            print(f"\nTranscribing {audio_file.name}...")
            result = await model.transcribe(audio_data, options=options)
            
            print(f"Detected Language: {result.language}")
            print(f"Text: {result.text[:100]}...")  # First 100 chars
            
        except Exception as e:
            print(f"Error transcribing {audio_file.name}: {e}")


async def real_time_webhook_example():
    """Example of using webhooks for real-time notifications."""
    print("\n=== Webhook Integration Example ===")
    
    provider = create_assemblyai()
    model = provider.transcription("best")
    
    # Configure webhook settings
    options = AssemblyAITranscriptionSettings(
        # Webhook configuration (replace with your webhook URL)
        webhook_url="https://your-app.com/webhook/assemblyai",
        webhook_auth_header_name="X-Webhook-Secret",
        webhook_auth_header_value="your-secret-key",
        
        # Enable features that work well with webhooks
        auto_chapters=True,
        summarization=True,
        summary_type="bullets",
        speaker_labels=True,
    )
    
    print("This example shows webhook configuration.")
    print("AssemblyAI will send POST requests to your webhook URL when:")
    print("1. Transcription is completed")
    print("2. Transcription fails")
    print("3. Redacted audio is ready (if enabled)")
    print("\nWebhook payload will include the full transcription results.")


if __name__ == "__main__":
    print("AssemblyAI Provider Examples")
    print("============================")
    print("Make sure to set ASSEMBLYAI_API_KEY environment variable")
    print("and provide valid audio file paths before running.\n")
    
    # Run examples
    asyncio.run(basic_transcription_example())
    asyncio.run(advanced_transcription_example())
    asyncio.run(pii_redaction_example())
    asyncio.run(multilingual_example())
    asyncio.run(real_time_webhook_example())