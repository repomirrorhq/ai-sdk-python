"""FAL.ai provider examples for image generation, speech synthesis, and transcription."""

import asyncio
from pathlib import Path
from ai_sdk.providers.fal import (
    create_fal, 
    FalImageSettings, 
    FalSpeechSettings,
    FalTranscriptionSettings,
    FalImageSizeCustom,
    FalVoiceSettings,
)


async def basic_image_generation_example():
    """Basic image generation with FAL."""
    print("=== Basic FAL Image Generation ===")
    
    # Create provider (requires FAL_API_KEY or FAL_KEY environment variable)
    provider = create_fal()
    
    try:
        # Create image model - using Flux Schnell for fast generation
        model = provider.image_model("fal-ai/flux/schnell")
        
        # Generate a single image
        print("Generating image...")
        result = await model.generate("A beautiful sunset over mountains with a lake reflection")
        
        print(f"Generated {len(result.images)} image(s)")
        
        # Save the first image
        output_path = Path("fal_sunset.png")
        with open(output_path, "wb") as f:
            f.write(result.images[0])
        
        print(f"Saved image to: {output_path}")
        
        # Show usage information
        if result.usage:
            print(f"Prompt tokens: {result.usage.prompt_tokens}")
        
    except Exception as e:
        print(f"Image generation error: {e}")


async def advanced_image_generation_example():
    """Advanced image generation with custom settings."""
    print("\n=== Advanced FAL Image Generation ===")
    
    provider = create_fal()
    
    try:
        # Use Flux Pro for higher quality
        model = provider.image_model("fal-ai/flux-pro/v1.1")
        
        # Configure advanced options
        options = FalImageSettings(
            image_size=FalImageSizeCustom(width=1024, height=1024),
            num_images=2,
            seed=42,  # For reproducible results
        )
        
        print("Generating high-quality images...")
        result = await model.generate(
            prompt="A cyberpunk cityscape at night with neon lights and flying cars, highly detailed, 8k resolution",
            options=options
        )
        
        print(f"Generated {len(result.images)} images with seed {options.seed}")
        
        # Save all generated images
        for i, image_data in enumerate(result.images):
            output_path = Path(f"fal_cyberpunk_{i}.png")
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"Saved image {i+1} to: {output_path}")
        
        # Access response metadata
        if result.response:
            response_data = result.response
            if "seed" in response_data:
                print(f"Actual seed used: {response_data['seed']}")
        
    except Exception as e:
        print(f"Advanced image generation error: {e}")


async def image_upscaling_example():
    """Image upscaling and enhancement with FAL."""
    print("\n=== FAL Image Upscaling ===")
    
    provider = create_fal()
    
    try:
        # Use an upscaling model
        model = provider.image_model("fal-ai/clarity-upscaler")
        
        # Note: For upscaling, you typically need to provide an input image
        # This is just an example of the API structure
        print("FAL upscaling models require input images.")
        print("Check FAL documentation for specific upscaling model requirements.")
        
        # Example for text-to-image upscaling workflow:
        # 1. Generate base image with standard model
        base_model = provider.image_model("fal-ai/flux/schnell") 
        base_result = await base_model.generate("A portrait of a wise old wizard")
        
        print("Generated base image for potential upscaling workflow")
        
        # Save base image
        with open("fal_wizard_base.png", "wb") as f:
            f.write(base_result.images[0])
        
    except Exception as e:
        print(f"Upscaling example error: {e}")


async def speech_synthesis_example():
    """Text-to-speech synthesis with FAL."""
    print("\n=== FAL Speech Synthesis ===")
    
    provider = create_fal()
    
    try:
        # Create speech model
        model = provider.speech_model("fal-ai/coqui-xtts")
        
        # Basic speech generation
        print("Generating speech...")
        result = await model.generate("Hello, this is a demonstration of FAL speech synthesis!")
        
        # Save audio file
        output_path = Path("fal_speech_basic.wav")
        with open(output_path, "wb") as f:
            f.write(result.audio)
        
        print(f"Saved speech to: {output_path}")
        
        # Show usage information
        if result.usage:
            print(f"Characters processed: {result.usage.characters}")
        
        # Show any warnings
        for warning in result.warnings:
            print(f"Warning: {warning}")
        
    except Exception as e:
        print(f"Speech synthesis error: {e}")


async def advanced_speech_synthesis_example():
    """Advanced speech synthesis with voice controls."""
    print("\n=== Advanced FAL Speech Synthesis ===")
    
    provider = create_fal()
    
    try:
        model = provider.speech_model("fal-ai/coqui-xtts")
        
        # Configure voice settings
        voice_settings = FalVoiceSettings(
            speed=1.1,  # Slightly faster
            vol=0.9,    # Slightly quieter
            pitch=0.8,  # Lower pitch
            emotion="happy",
            english_normalization=True,
        )
        
        options = FalSpeechSettings(
            voice_setting=voice_settings,
            language_boost="en",
            pronunciation_dict={
                "AI": "Artificial Intelligence",
                "FAL": "F-A-L",
            }
        )
        
        text = "Welcome to the AI SDK with FAL integration! This demonstrates advanced speech synthesis."
        
        print("Generating advanced speech with custom voice settings...")
        result = await model.generate(
            text=text,
            voice="female_narrator",  # If supported
            options=options
        )
        
        # Save enhanced audio
        output_path = Path("fal_speech_advanced.wav")
        with open(output_path, "wb") as f:
            f.write(result.audio)
        
        print(f"Saved enhanced speech to: {output_path}")
        
    except Exception as e:
        print(f"Advanced speech synthesis error: {e}")


async def audio_transcription_example():
    """Audio transcription with FAL."""
    print("\n=== FAL Audio Transcription ===")
    
    provider = create_fal()
    
    # Example audio file path
    audio_file = Path("path/to/your/audio.mp3")
    
    if not audio_file.exists():
        print(f"Audio file not found: {audio_file}")
        print("Please provide a valid audio file path for transcription example")
        return
    
    try:
        # Create transcription model
        model = provider.transcription_model("fal-ai/whisper")
        
        # Read audio file
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        
        # Configure transcription options
        options = FalTranscriptionSettings(
            language="en",
            task="transcribe",
        )
        
        print("Transcribing audio...")
        result = await model.transcribe(audio_data, options=options)
        
        print(f"Transcription: {result.text}")
        print(f"Language: {result.language}")
        
        if result.duration_seconds:
            print(f"Duration: {result.duration_seconds:.2f} seconds")
        
        # Access word-level segments if available
        if result.segments:
            print(f"Found {len(result.segments)} segments:")
            for segment in result.segments[:5]:  # Show first 5 segments
                print(f"  {segment.start_second:.2f}s-{segment.end_second:.2f}s: {segment.text}")
        
    except Exception as e:
        print(f"Transcription error: {e}")


async def diarization_example():
    """Speaker diarization example."""
    print("\n=== FAL Speaker Diarization ===")
    
    provider = create_fal()
    
    # Example audio file with multiple speakers
    audio_file = Path("path/to/conversation.mp3")
    
    if not audio_file.exists():
        print(f"Audio file not found: {audio_file}")
        print("Please provide a valid multi-speaker audio file")
        return
    
    try:
        # Use diarization model
        model = provider.transcription_model("fal-ai/whisper-diarization")
        
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        
        print("Running speaker diarization...")
        result = await model.transcribe(audio_data)
        
        print(f"Transcription with speakers: {result.text}")
        
        # Diarization results would be in segments or response metadata
        if result.segments:
            print("Speaker segments:")
            for segment in result.segments:
                print(f"  {segment.start_second:.2f}s-{segment.end_second:.2f}s: {segment.text}")
        
    except Exception as e:
        print(f"Diarization error: {e}")


async def batch_processing_example():
    """Batch processing multiple requests."""
    print("\n=== FAL Batch Processing ===")
    
    provider = create_fal()
    
    try:
        # Generate multiple images concurrently
        model = provider.image_model("fal-ai/flux/schnell")
        
        prompts = [
            "A serene forest with sunlight filtering through trees",
            "A futuristic space station orbiting Earth", 
            "A vintage car on a desert highway at sunset",
        ]
        
        print("Generating multiple images concurrently...")
        
        # Create tasks for concurrent generation
        tasks = [
            model.generate(prompt, seed=i*10) 
            for i, prompt in enumerate(prompts)
        ]
        
        # Wait for all generations to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Image {i+1} failed: {result}")
            else:
                output_path = Path(f"fal_batch_{i+1}.png")
                with open(output_path, "wb") as f:
                    f.write(result.images[0])
                print(f"Saved batch image {i+1} to: {output_path}")
        
    except Exception as e:
        print(f"Batch processing error: {e}")


if __name__ == "__main__":
    print("FAL.ai Provider Examples")
    print("========================")
    print("Make sure to set FAL_API_KEY or FAL_KEY environment variable")
    print("and provide valid file paths where needed.\n")
    
    # Run examples
    asyncio.run(basic_image_generation_example())
    asyncio.run(advanced_image_generation_example())
    asyncio.run(image_upscaling_example())
    asyncio.run(speech_synthesis_example())
    asyncio.run(advanced_speech_synthesis_example())
    asyncio.run(audio_transcription_example())
    asyncio.run(diarization_example())
    asyncio.run(batch_processing_example())