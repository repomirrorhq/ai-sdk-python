"""Example demonstrating image generation with AI SDK Python."""

import asyncio
from typing import Optional

from ai_sdk import create_openai
from ai_sdk.core import generate_image


async def main():
    """Image generation examples."""
    
    # Create OpenAI provider
    openai = create_openai()
    
    print("🎨 AI SDK Python - Image Generation Examples")
    print("=" * 50)
    
    # Example 1: Basic image generation with DALL-E 3
    print("\n1. Basic Image Generation (DALL-E 3)")
    print("-" * 40)
    
    try:
        image_model = openai.image("dall-e-3")
        result = await generate_image(
            model=image_model,
            prompt="A beautiful sunset over a mountain lake with reflections, digital art style",
            size="1024x1024"
        )
        
        print(f"✅ Generated {len(result.images)} image(s)")
        print(f"📊 Image info: {len(result.images[0].data)} bytes, type: {result.images[0].media_type}")
        
        # Save the image
        with open("generated_image_1.png", "wb") as f:
            f.write(result.images[0].data)
        print("💾 Saved as 'generated_image_1.png'")
        
    except Exception as e:
        print(f"❌ Error in basic generation: {str(e)}")
    
    # Example 2: Multiple images with DALL-E 2
    print("\n2. Multiple Image Generation (DALL-E 2)")
    print("-" * 45)
    
    try:
        dalle2_model = openai.image("dall-e-2")
        result = await generate_image(
            model=dalle2_model,
            prompt="A cute robot playing with colorful balls, cartoon style",
            n=3,
            size="512x512"
        )
        
        print(f"✅ Generated {len(result.images)} images")
        
        # Save all images
        for i, img in enumerate(result.images):
            filename = f"generated_image_2_{i+1}.png"
            with open(filename, "wb") as f:
                f.write(img.data)
            print(f"💾 Saved image {i+1} as '{filename}' ({len(img.data)} bytes)")
        
    except Exception as e:
        print(f"❌ Error in multiple generation: {str(e)}")
    
    # Example 3: Advanced parameters
    print("\n3. Advanced Parameters")
    print("-" * 25)
    
    try:
        image_model = openai.image("dall-e-3")
        result = await generate_image(
            model=image_model,
            prompt="A majestic lion in an African savanna at golden hour",
            size="1792x1024",  # Wide aspect ratio
            provider_options={
                "openai": {
                    "style": "vivid",  # OpenAI-specific parameter
                    "quality": "hd"
                }
            }
        )
        
        print(f"✅ Generated HD image with vivid style")
        print(f"📊 Image: {len(result.images[0].data)} bytes, type: {result.images[0].media_type}")
        
        with open("generated_image_3_hd.png", "wb") as f:
            f.write(result.images[0].data)
        print("💾 Saved as 'generated_image_3_hd.png'")
        
    except Exception as e:
        print(f"❌ Error in advanced generation: {str(e)}")
    
    # Example 4: Aspect ratio conversion
    print("\n4. Aspect Ratio Usage")
    print("-" * 23)
    
    try:
        image_model = openai.image("dall-e-3") 
        result = await generate_image(
            model=image_model,
            prompt="A vertical portrait of a woman in renaissance style",
            aspect_ratio="9:16"  # Will be converted to 1024x1792 for DALL-E
        )
        
        print(f"✅ Generated portrait image with 9:16 aspect ratio")
        
        with open("generated_image_4_portrait.png", "wb") as f:
            f.write(result.images[0].data)
        print("💾 Saved as 'generated_image_4_portrait.png'")
        
    except Exception as e:
        print(f"❌ Error in aspect ratio generation: {str(e)}")
    
    # Example 5: Error handling
    print("\n5. Error Handling")
    print("-" * 18)
    
    try:
        image_model = openai.image("dall-e-3")
        result = await generate_image(
            model=image_model,
            prompt="", # Empty prompt should cause an error
        )
        
    except Exception as e:
        print(f"✅ Properly caught error: {type(e).__name__}: {str(e)}")
    
    # Example 6: Image generation with metadata inspection
    print("\n6. Metadata Inspection")
    print("-" * 24)
    
    try:
        image_model = openai.image("dall-e-2")
        result = await generate_image(
            model=image_model,
            prompt="A futuristic city with flying cars, sci-fi concept art",
            n=2,
            size="256x256"
        )
        
        print(f"✅ Generated {len(result.images)} images")
        print(f"⚠️  Warnings: {len(result.warnings)}")
        print(f"📝 Response metadata: {result.responses[0]}")
        
        if result.provider_metadata:
            print(f"🏢 Provider metadata: {list(result.provider_metadata.keys())}")
        
    except Exception as e:
        print(f"❌ Error in metadata inspection: {str(e)}")
    
    print(f"\n🎉 Image generation examples completed!")
    print("Check the current directory for generated PNG files.")


def sync_example():
    """Synchronous example using generate_image_sync."""
    from ai_sdk.core import generate_image_sync
    
    print("\n🔄 Synchronous Image Generation")
    print("-" * 35)
    
    try:
        openai = create_openai()
        image_model = openai.image("dall-e-2")
        
        result = generate_image_sync(
            model=image_model,
            prompt="A peaceful zen garden with cherry blossoms",
            size="512x512"
        )
        
        print(f"✅ Synchronously generated image ({len(result.images[0].data)} bytes)")
        
        with open("sync_generated_image.png", "wb") as f:
            f.write(result.images[0].data)
        print("💾 Saved as 'sync_generated_image.png'")
        
    except Exception as e:
        print(f"❌ Error in sync generation: {str(e)}")


if __name__ == "__main__":
    # Run async examples
    asyncio.run(main())
    
    # Run sync example
    sync_example()