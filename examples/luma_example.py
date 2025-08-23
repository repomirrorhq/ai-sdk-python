"""
Comprehensive Luma AI Provider Example for AI SDK Python.

This example demonstrates the key features of the Luma provider:
1. Basic image generation with Photon models
2. High-quality image synthesis
3. Custom aspect ratios and sizing
4. Different model options (photon-1 vs photon-flash-1)
5. Advanced generation settings
6. Batch image generation
7. Error handling and best practices
8. Provider capabilities and model information

Prerequisites:
- Install ai-sdk-python: pip install ai-sdk-python[luma]
- Set LUMA_API_KEY environment variable or pass api_key parameter
- Get your API key from: https://lumalabs.ai/
"""

import asyncio
import base64
import os
from pathlib import Path
from typing import Any, Dict, List

from ai_sdk import generate_image
from ai_sdk.providers.luma import (
    LumaProvider,
    create_luma_provider,
    LumaImageModelId,
    LumaImageOptions,
)


async def basic_image_generation():
    """Demonstrate basic image generation with Luma Photon models."""
    print("=== Basic Image Generation ===")
    
    # Create provider (uses LUMA_API_KEY from environment)
    provider = LumaProvider()
    model = provider.image_model("photon-1")
    
    # Simple image generation
    prompt = "A majestic mountain landscape at sunset with vibrant orange and purple clouds, photorealistic"
    
    print(f"Generating image with prompt: '{prompt}'")
    print("Using model: photon-1 (high-quality)")
    
    try:
        result = await generate_image(
            model=model,
            prompt=prompt,
            aspect_ratio="16:9"
        )
        
        print(f"✅ Image generated successfully!")
        print(f"   Model: {result.model_id}")
        print(f"   Images: {len(result.images)}")
        print(f"   Image size: {len(result.images[0])} bytes")
        
        # Save image (optional)
        if result.images:
            output_path = "luma_basic_example.png"
            with open(output_path, "wb") as f:
                f.write(result.images[0])
            print(f"   Saved to: {output_path}")
            
        if result.provider_metadata and "luma" in result.provider_metadata:
            luma_meta = result.provider_metadata["luma"]
            print(f"   Generation ID: {luma_meta.get('generation_id')}")
            print(f"   Aspect ratio: {luma_meta.get('aspect_ratio')}")
        
    except Exception as e:
        print(f"❌ Generation failed: {type(e).__name__}: {e}")


async def model_comparison():
    """Compare different Luma models (photon-1 vs photon-flash-1)."""
    print("\n=== Model Comparison ===")
    
    provider = LumaProvider()
    prompt = "A futuristic cityscape with flying cars and neon lights, digital art style"
    
    models_to_test = [
        ("photon-1", "High-quality model (slower, better quality)"),
        ("photon-flash-1", "Fast model (faster, good quality)")
    ]
    
    print(f"Prompt: '{prompt}'")
    print("Comparing models:")
    
    for model_id, description in models_to_test:
        print(f"\n🎨 Testing {model_id}: {description}")
        
        try:
            model = provider.image_model(model_id)
            
            import time
            start_time = time.time()
            
            result = await generate_image(
                model=model,
                prompt=prompt,
                aspect_ratio="1:1"
            )
            
            duration = time.time() - start_time
            
            print(f"   ✅ Success! Generated in {duration:.1f} seconds")
            print(f"   Image size: {len(result.images[0])} bytes")
            
            # Save comparison images
            output_path = f"luma_{model_id.replace('-', '_')}_comparison.png"
            with open(output_path, "wb") as f:
                f.write(result.images[0])
            print(f"   Saved to: {output_path}")
            
        except Exception as e:
            print(f"   ❌ Failed: {type(e).__name__}: {e}")


async def aspect_ratio_examples():
    """Demonstrate various aspect ratios and sizing options."""
    print("\n=== Aspect Ratio Examples ===")
    
    provider = LumaProvider()
    model = provider.image_model("photon-flash-1")  # Use fast model for demos
    
    aspect_ratios = [
        ("1:1", "Square format - perfect for social media"),
        ("16:9", "Widescreen format - great for wallpapers"),
        ("4:3", "Traditional format - good for prints"),
        ("3:4", "Portrait format - ideal for mobile"),
        ("21:9", "Ultra-wide format - cinematic feel")
    ]
    
    base_prompt = "A serene Japanese garden with cherry blossoms and a traditional bridge"
    
    print(f"Base prompt: '{base_prompt}'")
    print("Testing different aspect ratios:")
    
    for aspect_ratio, description in aspect_ratios:
        print(f"\n📐 Aspect ratio {aspect_ratio}: {description}")
        
        try:
            result = await generate_image(
                model=model,
                prompt=base_prompt,
                aspect_ratio=aspect_ratio
            )
            
            print(f"   ✅ Generated successfully")
            print(f"   Image size: {len(result.images[0])} bytes")
            
            # Save with descriptive filename
            safe_ratio = aspect_ratio.replace(":", "_")
            output_path = f"luma_aspect_{safe_ratio}.png"
            with open(output_path, "wb") as f:
                f.write(result.images[0])
            print(f"   Saved to: {output_path}")
            
        except Exception as e:
            print(f"   ❌ Failed: {type(e).__name__}: {e}")


async def advanced_generation_settings():
    """Demonstrate advanced generation settings and options."""
    print("\n=== Advanced Generation Settings ===")
    
    provider = LumaProvider()
    model = provider.image_model("photon-1")
    
    # Custom polling settings for faster feedback
    options = LumaImageOptions(
        aspect_ratio="16:9",
        poll_interval_millis=250,  # Poll every 0.25 seconds
        max_poll_attempts=240      # Wait up to 1 minute
    )
    
    prompt = """
    A magnificent dragon soaring through storm clouds, lightning illuminating its scales,
    epic fantasy art, highly detailed, dramatic lighting, 8K resolution, masterpiece
    """
    
    print("🎯 Advanced settings:")
    print(f"   Aspect ratio: {options.aspect_ratio}")
    print(f"   Poll interval: {options.poll_interval_millis}ms")
    print(f"   Max attempts: {options.max_poll_attempts}")
    print(f"\nPrompt: {prompt.strip()}")
    
    try:
        import time
        start_time = time.time()
        
        result = await generate_image(
            model=model,
            prompt=prompt,
            options=options
        )
        
        duration = time.time() - start_time
        
        print(f"\n✅ Advanced generation completed in {duration:.1f} seconds")
        print(f"   Image size: {len(result.images[0])} bytes")
        
        # Save high-quality result
        output_path = "luma_advanced_dragon.png"
        with open(output_path, "wb") as f:
            f.write(result.images[0])
        print(f"   Saved to: {output_path}")
        
        # Show metadata
        if result.provider_metadata and "luma" in result.provider_metadata:
            luma_meta = result.provider_metadata["luma"]
            print(f"   Generation ID: {luma_meta.get('generation_id')}")
            print(f"   Image URL: {luma_meta.get('image_url', 'N/A')[:50]}...")
        
    except Exception as e:
        print(f"❌ Advanced generation failed: {type(e).__name__}: {e}")


async def creative_prompt_variations():
    """Demonstrate creative prompt variations and styles."""
    print("\n=== Creative Prompt Variations ===")
    
    provider = LumaProvider()
    model = provider.image_model("photon-1")
    
    # Different artistic styles for the same subject
    base_subject = "a wise old owl perched on an ancient tree branch"
    
    style_variations = [
        ("photorealistic", "ultra-realistic, high detail, professional wildlife photography"),
        ("impressionist", "impressionist painting style, soft brushstrokes, dreamy atmosphere"),
        ("cyberpunk", "cyberpunk style, neon colors, futuristic, digital art"),
        ("watercolor", "watercolor painting, soft colors, artistic, traditional media"),
        ("minimalist", "minimalist art, clean lines, simple composition, modern")
    ]
    
    print(f"Base subject: '{base_subject}'")
    print("Exploring different artistic styles:")
    
    for style_name, style_prompt in style_variations:
        print(f"\n🎨 Style: {style_name}")
        
        full_prompt = f"{base_subject}, {style_prompt}"
        print(f"   Prompt: {full_prompt}")
        
        try:
            result = await generate_image(
                model=model,
                prompt=full_prompt,
                aspect_ratio="1:1"
            )
            
            print(f"   ✅ Generated {style_name} style")
            
            # Save with style in filename
            output_path = f"luma_owl_{style_name}.png"
            with open(output_path, "wb") as f:
                f.write(result.images[0])
            print(f"   Saved to: {output_path}")
            
        except Exception as e:
            print(f"   ❌ Failed: {type(e).__name__}: {e}")


async def batch_generation_example():
    """Demonstrate generating multiple images with different prompts."""
    print("\n=== Batch Generation Example ===")
    
    provider = LumaProvider()
    model = provider.image_model("photon-flash-1")  # Use fast model for batch
    
    # Collection of prompts for a themed series
    nature_prompts = [
        "A crystal clear mountain lake reflecting snow-capped peaks",
        "An ancient redwood forest with rays of sunlight filtering through",
        "A vibrant coral reef teeming with tropical fish",
        "A vast desert landscape with sand dunes under starry sky",
        "A peaceful meadow filled with wildflowers and butterflies"
    ]
    
    print(f"🎨 Generating {len(nature_prompts)} nature scenes:")
    print("Using photon-flash-1 for faster batch processing")
    
    results = []
    
    for i, prompt in enumerate(nature_prompts, 1):
        print(f"\n{i}. {prompt}")
        
        try:
            result = await generate_image(
                model=model,
                prompt=prompt,
                aspect_ratio="16:9"
            )
            
            print(f"   ✅ Generated successfully ({len(result.images[0])} bytes)")
            
            # Save with numbered filename
            output_path = f"luma_nature_{i:02d}.png"
            with open(output_path, "wb") as f:
                f.write(result.images[0])
            print(f"   Saved to: {output_path}")
            
            results.append(result)
            
            # Small delay to be respectful to the API
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Failed: {type(e).__name__}: {e}")
    
    print(f"\n✅ Batch generation completed: {len(results)}/{len(nature_prompts)} successful")


async def error_handling_example():
    """Demonstrate error handling and best practices."""
    print("\n=== Error Handling Example ===")
    
    try:
        # Invalid API key example
        provider = create_luma_provider(api_key="invalid-key")
        model = provider.image_model("photon-1")
        
        result = await generate_image(
            model=model,
            prompt="Test image",
            aspect_ratio="1:1"
        )
        
    except Exception as e:
        print(f"✅ Expected error with invalid API key: {type(e).__name__}: {e}")
    
    try:
        # Test with missing API key
        original_key = os.environ.get("LUMA_API_KEY")
        if "LUMA_API_KEY" in os.environ:
            del os.environ["LUMA_API_KEY"]
        
        provider = LumaProvider()
        
    except Exception as e:
        print(f"✅ Expected error with missing API key: {type(e).__name__}: {e}")
        # Restore key if it existed
        if original_key:
            os.environ["LUMA_API_KEY"] = original_key
    
    try:
        # Test invalid model ID
        provider = LumaProvider()
        model = provider.image_model("invalid-model")
        
    except Exception as e:
        print(f"✅ Expected error with invalid model: {type(e).__name__}: {e}")
    
    # Test timeout settings
    print("\n⏱️  Testing custom timeout settings:")
    provider = create_luma_provider(timeout=30.0)  # 30 second timeout
    print("   Custom timeout configured: 30 seconds")


async def provider_info_example():
    """Show provider capabilities and model information."""
    print("\n=== Provider Information ===")
    
    provider = LumaProvider()
    
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
    for model_type, model_dict in models.items():
        print(f"\n{model_type.replace('_', ' ').title()}:")
        for model_id, info in model_dict.items():
            print(f"  {model_id}:")
            print(f"    Description: {info['description']}")
            print(f"    Max resolution: {info['max_resolution']}")
            print(f"    Generation time: {info['typical_generation_time']}")
            
            if info.get('features'):
                print(f"    Features:")
                for feature in info['features']:
                    print(f"      - {feature}")


async def image_analysis_example():
    """Analyze generated images and show statistics."""
    print("\n=== Image Analysis Example ===")
    
    provider = LumaProvider()
    model = provider.image_model("photon-1")
    
    # Generate a test image
    prompt = "A colorful abstract geometric pattern with vibrant blues and oranges"
    
    print(f"Generating test image: '{prompt}'")
    
    try:
        result = await generate_image(
            model=model,
            prompt=prompt,
            aspect_ratio="1:1"
        )
        
        image_data = result.images[0]
        
        print(f"✅ Image generated successfully")
        print(f"📊 Image Analysis:")
        print(f"   File size: {len(image_data):,} bytes ({len(image_data) / 1024:.1f} KB)")
        print(f"   Base64 length: {len(base64.b64encode(image_data)):,} characters")
        
        # Detect file format from first few bytes
        if image_data.startswith(b'\x89PNG'):
            format_type = "PNG"
        elif image_data.startswith(b'\xff\xd8'):
            format_type = "JPEG"
        else:
            format_type = "Unknown"
        
        print(f"   Detected format: {format_type}")
        
        # Save with analysis filename
        output_path = f"luma_analysis_example.{format_type.lower()}"
        with open(output_path, "wb") as f:
            f.write(image_data)
        print(f"   Saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {type(e).__name__}: {e}")


async def main():
    """Run all examples."""
    print("Luma AI Provider Examples for AI SDK Python")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("LUMA_API_KEY")
    if not api_key:
        print("WARNING: LUMA_API_KEY not found. Some examples may fail.")
        print("Set your API key: export LUMA_API_KEY='your-api-key'")
        print("Get your API key at: https://lumalabs.ai/")
        print()
    
    try:
        await basic_image_generation()
        await model_comparison()
        await aspect_ratio_examples()
        await advanced_generation_settings()
        await creative_prompt_variations()
        await batch_generation_example()
        await error_handling_example()
        await provider_info_example()
        await image_analysis_example()
        
        print("\n" + "=" * 50)
        print("All Luma examples completed successfully!")
        
        print("\n📚 Key Features Demonstrated:")
        print("  ✅ Basic image generation")
        print("  ✅ Model comparison (photon-1 vs photon-flash-1)")
        print("  ✅ Custom aspect ratios")
        print("  ✅ Advanced generation settings")
        print("  ✅ Creative prompt variations")
        print("  ✅ Batch image generation")
        print("  ✅ Error handling")
        print("  ✅ Provider information")
        print("  ✅ Image analysis")
        
        print("\n🎨 Generated Images:")
        generated_files = [
            "luma_basic_example.png",
            "luma_photon_1_comparison.png", 
            "luma_photon_flash_1_comparison.png",
            "luma_aspect_1_1.png",
            "luma_aspect_16_9.png",
            "luma_aspect_4_3.png",
            "luma_aspect_3_4.png", 
            "luma_aspect_21_9.png",
            "luma_advanced_dragon.png",
            "luma_owl_photorealistic.png",
            "luma_owl_impressionist.png",
            "luma_owl_cyberpunk.png",
            "luma_owl_watercolor.png",
            "luma_owl_minimalist.png",
            "luma_nature_01.png",
            "luma_nature_02.png", 
            "luma_nature_03.png",
            "luma_nature_04.png",
            "luma_nature_05.png",
            "luma_analysis_example.png"
        ]
        
        existing_files = [f for f in generated_files if Path(f).exists()]
        print(f"  📁 {len(existing_files)} images saved to current directory")
        
        print("\n🚀 Next Steps:")
        print("  1. Get your Luma API key: https://lumalabs.ai/")
        print("  2. Experiment with different prompts and styles")
        print("  3. Try different aspect ratios for various use cases")
        print("  4. Use photon-flash-1 for quick iterations")
        print("  5. Use photon-1 for highest quality results")
        
    except Exception as e:
        print(f"\n❌ Example failed: {type(e).__name__}: {e}")
        print("Check your API key and internet connection.")


if __name__ == "__main__":
    asyncio.run(main())