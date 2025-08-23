"""
Test script to verify TogetherAI image model support.
"""

import asyncio
from ai_sdk.providers.togetherai import create_together


async def test_togetherai_image():
    """Test TogetherAI image model functionality."""
    
    # Create TogetherAI provider
    together = create_together()
    
    # Test image model creation
    try:
        image_model = together.image_model("black-forest-labs/FLUX.1-schnell-Free")
        print(f"✅ Image model created: {type(image_model)}")
        print(f"   Model ID: {image_model.model_id}")
        print(f"   Provider: {image_model.provider}")
        
        # Check if model has the required methods
        has_generate = hasattr(image_model, 'generate')
        has_do_generate = hasattr(image_model, 'do_generate')
        print(f"   Has generate method: {has_generate}")
        print(f"   Has do_generate method: {has_do_generate}")
        
    except Exception as e:
        print(f"❌ Error creating image model: {e}")
    
    # Test available image models
    from ai_sdk.providers.togetherai.types import TOGETHER_IMAGE_MODELS
    print(f"\n📋 Available image models: {len(TOGETHER_IMAGE_MODELS)}")
    for model_id in TOGETHER_IMAGE_MODELS:
        print(f"   - {model_id}")


if __name__ == "__main__":
    asyncio.run(test_togetherai_image())