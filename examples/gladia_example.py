"""
Comprehensive Gladia Provider Example for AI SDK Python.

This example demonstrates the key features of the Gladia provider:
1. Basic audio transcription
2. Speaker diarization (speaker identification)
3. Multi-language detection and translation
4. Automatic summarization
5. Named entity recognition
6. Custom vocabulary
7. Subtitle generation
8. Content moderation
9. Advanced AI features
10. Error handling and best practices

Prerequisites:
- Install ai-sdk-python: pip install ai-sdk-python[gladia]
- Set GLADIA_API_KEY environment variable or pass api_key parameter
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List

from ai_sdk import transcribe
from ai_sdk.providers.gladia import (
    GladiaProvider,
    create_gladia_provider,
    GladiaTranscriptionOptions,
    GladiaDiarizationConfig,
    GladiaTranslationConfig,
    GladiaSummarizationConfig,
    GladiaCustomVocabularyConfig,
    GladiaCustomVocabularyItem,
    GladiaSubtitlesConfig,
)


async def basic_transcription():
    """Demonstrate basic audio transcription with Gladia."""
    print("=== Basic Audio Transcription ===")
    
    # Create provider (uses GLADIA_API_KEY from environment)
    provider = GladiaProvider()
    model = provider.transcription_model()
    
    # Load sample audio (you would replace this with your audio file)
    try:
        # For demo purposes, using a placeholder. In real usage:
        # with open("path/to/your/audio.wav", "rb") as f:
        #     audio_data = f.read()
        
        # Using placeholder for demo
        print("📝 Note: Replace this with actual audio file loading")
        print("Example: with open('audio.wav', 'rb') as f: audio_data = f.read()")
        
        # Simulated transcription call (would work with real audio)
        # result = await transcribe(
        #     model=model,
        #     audio=audio_data,
        #     media_type="audio/wav"
        # )
        # 
        # print(f"Transcription: {result.text}")
        # print(f"Language: {result.language}")
        # print(f"Duration: {result.duration:.2f} seconds")
        # print(f"Segments: {len(result.segments)}")
        
        print("✅ Basic transcription example prepared")
        
    except FileNotFoundError:
        print("⚠️  Audio file not found. Please provide a valid audio file path.")


async def speaker_diarization_example():
    """Demonstrate speaker diarization (speaker identification)."""
    print("\n=== Speaker Diarization Example ===")
    
    provider = GladiaProvider()
    model = provider.transcription_model()
    
    # Configure speaker diarization
    options = GladiaTranscriptionOptions(
        diarization=True,
        diarization_config=GladiaDiarizationConfig(
            min_speakers=2,
            max_speakers=5,
            enhanced=True  # Use enhanced diarization for better accuracy
        )
    )
    
    try:
        # Example with speaker identification
        print("🎯 Diarization configuration:")
        print(f"  - Enhanced diarization: {options.diarization_config.enhanced}")
        print(f"  - Min speakers: {options.diarization_config.min_speakers}")
        print(f"  - Max speakers: {options.diarization_config.max_speakers}")
        
        # In real usage:
        # result = await transcribe(
        #     model=model,
        #     audio=audio_data,
        #     media_type="audio/wav",
        #     options=options
        # )
        # 
        # print(f"\nTranscription with speakers:")
        # for segment in result.segments:
        #     speaker = segment.speaker or "Unknown"
        #     print(f"[{speaker}] {segment.text}")
        
        print("✅ Speaker diarization example prepared")
        
    except Exception as e:
        print(f"❌ Diarization example error: {e}")


async def multi_language_translation():
    """Demonstrate multi-language detection and translation."""
    print("\n=== Multi-Language Detection and Translation ===")
    
    provider = GladiaProvider()
    model = provider.transcription_model()
    
    # Configure language detection and translation
    options = GladiaTranscriptionOptions(
        detect_language=True,
        enable_code_switching=True,  # Support multiple languages in same audio
        translation=True,
        translation_config=GladiaTranslationConfig(
            target_languages=["en", "es", "fr"],  # Translate to English, Spanish, French
            model="enhanced",
            match_original_utterances=True
        )
    )
    
    print("🌍 Language configuration:")
    print(f"  - Auto language detection: {options.detect_language}")
    print(f"  - Code switching support: {options.enable_code_switching}")
    print(f"  - Translation targets: {options.translation_config.target_languages}")
    print(f"  - Translation model: {options.translation_config.model}")
    
    # In real usage:
    # result = await transcribe(
    #     model=model,
    #     audio=multilingual_audio_data,
    #     media_type="audio/wav",
    #     options=options
    # )
    # 
    # print(f"Original: {result.text}")
    # print(f"Detected language: {result.language}")
    # 
    # if result.provider_metadata and "gladia" in result.provider_metadata:
    #     gladia_meta = result.provider_metadata["gladia"]
    #     if gladia_meta.get("result", {}).get("translations"):
    #         for lang, translation in gladia_meta["result"]["translations"].items():
    #             print(f"Translation ({lang}): {translation}")
    
    print("✅ Multi-language translation example prepared")


async def automatic_summarization():
    """Demonstrate automatic summarization of transcriptions."""
    print("\n=== Automatic Summarization ===")
    
    provider = GladiaProvider()
    model = provider.transcription_model()
    
    # Configure summarization
    options = GladiaTranscriptionOptions(
        summarization=True,
        summarization_config=GladiaSummarizationConfig(
            type="bullet_points"  # Can be "general", "bullet_points", or "concise"
        ),
        named_entity_recognition=True,  # Also extract named entities
        sentiment_analysis=True,  # Analyze sentiment
        chapterization=True  # Create automatic chapters
    )
    
    print("📋 Summarization configuration:")
    print(f"  - Summary type: {options.summarization_config.type}")
    print(f"  - Named entity recognition: {options.named_entity_recognition}")
    print(f"  - Sentiment analysis: {options.sentiment_analysis}")
    print(f"  - Automatic chapters: {options.chapterization}")
    
    # In real usage:
    # result = await transcribe(
    #     model=model,
    #     audio=long_audio_data,  # Works best with longer audio
    #     media_type="audio/wav",
    #     options=options
    # )
    # 
    # print(f"Full transcript: {result.text}")
    # 
    # if result.provider_metadata and "gladia" in result.provider_metadata:
    #     gladia_meta = result.provider_metadata["gladia"]
    #     result_data = gladia_meta.get("result", {})
    #     
    #     if result_data.get("summarization"):
    #         print(f"Summary: {result_data['summarization']['summary']}")
    #     
    #     if result_data.get("named_entities"):
    #         print("Named entities:")
    #         for entity in result_data["named_entities"]:
    #             print(f"  - {entity['text']} ({entity['type']})")
    #     
    #     if result_data.get("sentiment_analysis"):
    #         sentiment = result_data["sentiment_analysis"]
    #         print(f"Overall sentiment: {sentiment['overall']} (confidence: {sentiment['confidence']})")
    
    print("✅ Automatic summarization example prepared")


async def custom_vocabulary_example():
    """Demonstrate custom vocabulary for improved accuracy."""
    print("\n=== Custom Vocabulary Example ===")
    
    provider = GladiaProvider()
    model = provider.transcription_model()
    
    # Define custom vocabulary with technical terms
    custom_vocab = GladiaCustomVocabularyConfig(
        vocabulary=[
            # Simple string terms
            "API",
            "JavaScript",
            "TypeScript",
            
            # Complex terms with pronunciation hints
            GladiaCustomVocabularyItem(
                value="Anthropic",
                intensity=0.8,
                pronunciations=["an-thro-pic", "AN-thro-pic"]
            ),
            GladiaCustomVocabularyItem(
                value="Claude",
                intensity=0.9,
                pronunciations=["klowd"]
            ),
            GladiaCustomVocabularyItem(
                value="GPT",
                intensity=0.7,
                pronunciations=["G-P-T", "gee-pee-tee"]
            )
        ],
        default_intensity=0.6
    )
    
    options = GladiaTranscriptionOptions(
        custom_vocabulary=True,
        custom_vocabulary_config=custom_vocab,
        punctuation_enhanced=True,
        name_consistency=True
    )
    
    print("🎯 Custom vocabulary configuration:")
    print(f"  - Number of custom terms: {len(custom_vocab.vocabulary)}")
    print(f"  - Default intensity: {custom_vocab.default_intensity}")
    print(f"  - Enhanced punctuation: {options.punctuation_enhanced}")
    print(f"  - Name consistency: {options.name_consistency}")
    
    print("Custom terms:")
    for term in custom_vocab.vocabulary:
        if isinstance(term, str):
            print(f"  - {term}")
        else:
            print(f"  - {term.value} (intensity: {term.intensity})")
    
    print("✅ Custom vocabulary example prepared")


async def subtitle_generation():
    """Demonstrate subtitle generation."""
    print("\n=== Subtitle Generation ===")
    
    provider = GladiaProvider()
    model = provider.transcription_model()
    
    # Configure subtitle generation
    options = GladiaTranscriptionOptions(
        subtitles=True,
        subtitles_config=GladiaSubtitlesConfig(
            formats=["srt", "vtt"],
            minimum_duration=1.0,  # Minimum 1 second per subtitle
            maximum_duration=6.0,  # Maximum 6 seconds per subtitle
            maximum_characters_per_row=45,
            maximum_rows_per_caption=2,
            style="compliance"  # Use compliance-friendly formatting
        ),
        sentences=True,  # Include sentence-level segmentation
        display_mode=True  # Optimize for display
    )
    
    print("🎬 Subtitle configuration:")
    print(f"  - Formats: {options.subtitles_config.formats}")
    print(f"  - Duration range: {options.subtitles_config.minimum_duration}-{options.subtitles_config.maximum_duration} seconds")
    print(f"  - Max characters per row: {options.subtitles_config.maximum_characters_per_row}")
    print(f"  - Max rows per caption: {options.subtitles_config.maximum_rows_per_caption}")
    print(f"  - Style: {options.subtitles_config.style}")
    
    # In real usage:
    # result = await transcribe(
    #     model=model,
    #     audio=video_audio_data,
    #     media_type="audio/wav",
    #     options=options
    # )
    # 
    # print(f"Transcript: {result.text}")
    # 
    # if result.provider_metadata and "gladia" in result.provider_metadata:
    #     gladia_meta = result.provider_metadata["gladia"]
    #     result_data = gladia_meta.get("result", {})
    #     
    #     if result_data.get("subtitles"):
    #         for format_type, subtitle_content in result_data["subtitles"].items():
    #             print(f"\n{format_type.upper()} subtitles:")
    #             print(subtitle_content[:300] + "..." if len(subtitle_content) > 300 else subtitle_content)
    
    print("✅ Subtitle generation example prepared")


async def content_moderation_example():
    """Demonstrate content moderation and safety features."""
    print("\n=== Content Moderation Example ===")
    
    provider = GladiaProvider()
    model = provider.transcription_model()
    
    # Configure content moderation and safety
    options = GladiaTranscriptionOptions(
        moderation=True,
        sentiment_analysis=True,
        named_entity_recognition=True
    )
    
    print("🛡️ Content moderation configuration:")
    print(f"  - Content moderation: {options.moderation}")
    print(f"  - Sentiment analysis: {options.sentiment_analysis}")
    print(f"  - Named entity recognition: {options.named_entity_recognition}")
    
    # In real usage:
    # result = await transcribe(
    #     model=model,
    #     audio=audio_data,
    #     media_type="audio/wav",
    #     options=options
    # )
    # 
    # print(f"Transcript: {result.text}")
    # 
    # if result.provider_metadata and "gladia" in result.provider_metadata:
    #     gladia_meta = result.provider_metadata["gladia"]
    #     result_data = gladia_meta.get("result", {})
    #     
    #     if result_data.get("moderation"):
    #         moderation = result_data["moderation"]
    #         print(f"Content safety score: {moderation.get('safety_score', 'N/A')}")
    #         
    #         if moderation.get("flagged_content"):
    #             print("Flagged content detected:")
    #             for flag in moderation["flagged_content"]:
    #                 print(f"  - {flag['category']}: {flag['severity']}")
    
    print("✅ Content moderation example prepared")


async def advanced_ai_features():
    """Demonstrate advanced AI features like structured data extraction."""
    print("\n=== Advanced AI Features ===")
    
    provider = GladiaProvider()
    model = provider.transcription_model()
    
    # Configure advanced AI features
    options = GladiaTranscriptionOptions(
        structured_data_extraction=True,
        structured_data_extraction_config={
            "classes": ["person", "organization", "location", "date", "money", "phone_number", "email"]
        },
        audio_to_llm=True,
        audio_to_llm_config={
            "prompts": [
                "Extract the main action items from this conversation",
                "Identify any decisions made during this meeting",
                "List any deadlines or dates mentioned"
            ]
        }
    )
    
    print("🤖 Advanced AI configuration:")
    print(f"  - Structured data extraction: {options.structured_data_extraction}")
    print(f"  - Data classes: {options.structured_data_extraction_config['classes']}")
    print(f"  - Audio to LLM: {options.audio_to_llm}")
    print(f"  - LLM prompts: {len(options.audio_to_llm_config.prompts)}")
    
    for i, prompt in enumerate(options.audio_to_llm_config.prompts, 1):
        print(f"    {i}. {prompt}")
    
    print("✅ Advanced AI features example prepared")


async def error_handling_example():
    """Demonstrate error handling and best practices."""
    print("\n=== Error Handling Example ===")
    
    try:
        # Invalid API key example
        provider = create_gladia_provider(api_key="invalid-key")
        model = provider.transcription_model()
        
        # This would fail with invalid API key
        print("🔍 Testing invalid API key handling...")
        # result = await transcribe(model=model, audio=b"fake_audio", media_type="audio/wav")
        
    except Exception as e:
        print(f"✅ Expected error with invalid API key: {type(e).__name__}: {e}")
    
    try:
        # Test with missing API key
        os.environ.pop("GLADIA_API_KEY", None)  # Remove if exists
        provider = GladiaProvider()
        
    except Exception as e:
        print(f"✅ Expected error with missing API key: {type(e).__name__}: {e}")
        # Restore for other examples
        os.environ["GLADIA_API_KEY"] = "demo-key"


async def provider_info_example():
    """Show provider capabilities and model information."""
    print("\n=== Provider Information ===")
    
    provider = GladiaProvider()
    
    # Get provider info
    provider_info = provider.get_provider_info()
    print(f"Provider: {provider_info['name']}")
    print(f"Description: {provider_info['description']}")
    print(f"API Version: {provider_info['api_version']}")
    print(f"Base URL: {provider_info['base_url']}")
    
    print(f"\nCapabilities:")
    for capability in provider_info['capabilities']:
        print(f"  - {capability.replace('_', ' ').title()}")
    
    print(f"\nSupported Modalities:")
    print(f"  Input: {', '.join(provider_info['supported_modalities']['input'])}")
    print(f"  Output: {', '.join(provider_info['supported_modalities']['output'])}")
    
    # Get available models
    models = provider.get_available_models()
    
    print(f"\nAvailable Models:")
    for model_type, model_info in models.items():
        print(f"\n{model_type.replace('_', ' ').title()}:")
        for model_id, info in model_info.items():
            print(f"  {model_id}:")
            print(f"    Description: {info['description']}")
            print(f"    Max file size: {info['max_file_size']}")
            print(f"    Max duration: {info['max_duration']}")
            print(f"    Supported formats: {', '.join(info['supported_formats'])}")
            
            if info.get('features'):
                print(f"    Features:")
                for feature in info['features']:
                    print(f"      - {feature}")


async def batch_processing_example():
    """Demonstrate processing multiple audio files."""
    print("\n=== Batch Processing Example ===")
    
    provider = GladiaProvider()
    model = provider.transcription_model()
    
    # Simulate multiple audio files
    audio_files = [
        {"name": "meeting1.wav", "type": "meeting"},
        {"name": "interview1.mp3", "type": "interview"}, 
        {"name": "lecture1.m4a", "type": "lecture"}
    ]
    
    print(f"Processing {len(audio_files)} audio files...")
    
    for i, file_info in enumerate(audio_files, 1):
        print(f"\n📄 File {i}: {file_info['name']} ({file_info['type']})")
        
        # Configure options based on content type
        if file_info['type'] == 'meeting':
            options = GladiaTranscriptionOptions(
                diarization=True,
                diarization_config=GladiaDiarizationConfig(min_speakers=2, max_speakers=8),
                summarization=True,
                summarization_config=GladiaSummarizationConfig(type="bullet_points")
            )
        elif file_info['type'] == 'interview':
            options = GladiaTranscriptionOptions(
                diarization=True,
                diarization_config=GladiaDiarizationConfig(number_of_speakers=2),
                sentiment_analysis=True
            )
        else:  # lecture
            options = GladiaTranscriptionOptions(
                chapterization=True,
                summarization=True,
                summarization_config=GladiaSummarizationConfig(type="general")
            )
        
        print(f"  Configuration: {file_info['type']}-optimized settings")
        print(f"  - Diarization: {options.diarization}")
        print(f"  - Summarization: {options.summarization}")
        
        # In real usage, process each file:
        # with open(file_info['name'], 'rb') as f:
        #     audio_data = f.read()
        # 
        # result = await transcribe(
        #     model=model,
        #     audio=audio_data,
        #     media_type="audio/wav",
        #     options=options
        # )
        # 
        # print(f"  Result: {len(result.text)} characters transcribed")
    
    print("\n✅ Batch processing example prepared")


async def main():
    """Run all examples."""
    print("Gladia Provider Examples for AI SDK Python")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("GLADIA_API_KEY")
    if not api_key:
        print("WARNING: GLADIA_API_KEY not found. Some examples may fail.")
        print("Set your API key: export GLADIA_API_KEY='your-api-key'")
        print("Get your API key at: https://gladia.io")
        print()
        # Set a demo key for the examples to run
        os.environ["GLADIA_API_KEY"] = "demo-key-for-examples"
    
    try:
        await basic_transcription()
        await speaker_diarization_example()
        await multi_language_translation()
        await automatic_summarization()
        await custom_vocabulary_example()
        await subtitle_generation()
        await content_moderation_example()
        await advanced_ai_features()
        await batch_processing_example()
        await error_handling_example()
        await provider_info_example()
        
        print("\n" + "=" * 50)
        print("All Gladia examples completed successfully!")
        print("\n📚 Key Features Demonstrated:")
        print("  ✅ Basic transcription")
        print("  ✅ Speaker diarization")
        print("  ✅ Multi-language support")
        print("  ✅ Real-time translation")
        print("  ✅ Automatic summarization")
        print("  ✅ Custom vocabulary")
        print("  ✅ Subtitle generation")
        print("  ✅ Content moderation")
        print("  ✅ Advanced AI features")
        print("  ✅ Batch processing")
        print("  ✅ Error handling")
        
        print("\n🚀 Next Steps:")
        print("  1. Get your Gladia API key: https://gladia.io")
        print("  2. Replace the demo audio loading with your actual audio files")
        print("  3. Uncomment the transcribe() calls to run real transcriptions")
        print("  4. Explore advanced features like structured data extraction")
        
    except Exception as e:
        print(f"\n❌ Example failed: {type(e).__name__}: {e}")
        print("Check your API key and internet connection.")


if __name__ == "__main__":
    asyncio.run(main())