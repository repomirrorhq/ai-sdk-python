"""
Enhanced TogetherAI Example with Image Generation

This example demonstrates the full capabilities of the TogetherAI provider
including chat, embeddings, and image generation with proper API handling.
"""

import asyncio
import base64
import os
from ai_sdk import (
    generate_text,
    generate_object,
    generate_image,
    embed,
    create_together
)
from pydantic import BaseModel


class CreativeProject(BaseModel):
    """A creative project description."""
    title: str
    description: str
    style: str
    mood: str


async def togetherai_chat_example():
    """Example using TogetherAI for text generation."""
    print("🗣️ TogetherAI Chat Example")
    print("-" * 40)
    
    together = create_together()
    
    # Use a popular chat model
    result = await generate_text(
        model=together("meta-llama/Llama-3.3-70B-Instruct-Turbo"),
        messages=[{
            "role": "user",
            "content": "Explain quantum computing in simple terms."
        }],
        max_tokens=200,
        temperature=0.7
    )
    
    print(f"Response: {result.text}")
    print(f"Usage: {result.usage}")


async def togetherai_structured_example():
    """Example using TogetherAI for structured output generation."""
    print("\n📋 TogetherAI Structured Output Example")
    print("-" * 40)
    
    together = create_together()
    
    result = await generate_object(
        model=together("meta-llama/Llama-3.1-70B-Instruct-Turbo"),
        schema=CreativeProject,
        messages=[{
            "role": "user",
            "content": "Create a creative project idea for a sci-fi short story."
        }],
        temperature=0.8
    )
    
    project = result.object
    print(f"Project: {project.title}")
    print(f"Description: {project.description}")
    print(f"Style: {project.style}")
    print(f"Mood: {project.mood}")


async def togetherai_image_example():
    """Example using TogetherAI for image generation."""
    print("\n🎨 TogetherAI Image Generation Example")
    print("-" * 40)
    
    together = create_together()
    
    try:
        # Test with FLUX model (free tier)
        result = await generate_image(
            model=together.image_model("black-forest-labs/FLUX.1-schnell-Free"),
            prompt="A futuristic city at sunset with flying cars and neon lights, cyberpunk style",
            size="1024x1024",
            n=1
        )
        
        print(f"✅ Generated {len(result.images)} image(s)")
        print(f"Response metadata: {result.response_metadata}")
        
        # Save the first image
        if result.images and result.images[0].get("b64_json"):
            image_data = base64.b64decode(result.images[0]["b64_json"])
            with open("togetherai_generated_image.png", "wb") as f:
                f.write(image_data)
            print("💾 Image saved as 'togetherai_generated_image.png'")
        
    except Exception as e:
        print(f"❌ Image generation error: {e}")
        print("(This might be expected if no API key is provided)")


async def togetherai_embedding_example():
    """Example using TogetherAI for text embeddings."""
    print("\n🔍 TogetherAI Embedding Example")
    print("-" * 40)
    
    together = create_together()
    
    try:
        texts = [
            "The quick brown fox jumps over the lazy dog",
            "AI models are transforming how we work with technology",
            "Together AI provides access to many open-source models"
        ]
        
        result = await embed(
            model=together.text_embedding_model("togethercomputer/m2-bert-80M-8k-retrieval"),
            texts=texts
        )
        
        print(f"✅ Generated embeddings for {len(texts)} texts")
        print(f"Embedding dimensions: {len(result.embeddings[0])}")
        print(f"Usage: {result.usage}")
        
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        print("(This might be expected if no API key is provided)")


async def togetherai_model_showcase():
    """Showcase different TogetherAI model types."""
    print("\n🏆 TogetherAI Model Showcase")
    print("-" * 40)
    
    together = create_together()
    
    # Show available model types
    print("📋 Available model types:")
    print("  - Chat Models: LLaMA 3.3, LLaMA 3.2, Mixtral, Gemma, Qwen")
    print("  - Image Models: FLUX.1, Stable Diffusion")
    print("  - Embedding Models: M2-BERT, UAE-Large, BGE")
    
    # Demonstrate model creation (without API calls)
    chat_model = together("meta-llama/Llama-3.3-70B-Instruct-Turbo")
    image_model = together.image_model("black-forest-labs/FLUX.1-schnell-Free")
    embedding_model = together.text_embedding_model("BAAI/bge-large-en-v1.5")
    
    print(f"\n✅ Chat model: {chat_model.model_id}")
    print(f"✅ Image model: {image_model.model_id}")
    print(f"✅ Embedding model: {embedding_model.model_id}")
    
    # Show supported image sizes
    supported_sizes = image_model.get_supported_sizes()
    print(f"\n📐 Supported image sizes: {supported_sizes[:5]}... (showing first 5)")
    print(f"🔢 Max images per call: {image_model.get_max_images_per_call()}")


def print_api_key_info():
    """Print API key setup information."""
    print("🔑 TogetherAI API Key Setup")
    print("-" * 40)
    print("To run these examples with real API calls:")
    print("1. Get your API key from https://api.together.xyz/")
    print("2. Set environment variable: export TOGETHER_AI_API_KEY=your-key")
    print("3. Or pass it directly: create_together(TogetherAIProviderSettings(api_key='your-key'))")
    print()


async def main():
    """Run all TogetherAI examples."""
    print("🤖 Enhanced TogetherAI Examples")
    print("=" * 50)
    
    print_api_key_info()
    
    # Check if API key is available
    has_api_key = bool(os.getenv("TOGETHER_AI_API_KEY") or os.getenv("TOGETHER_API_KEY"))
    
    if has_api_key:
        print("✅ API key found, running live examples...\n")
        await togetherai_chat_example()
        await togetherai_structured_example()
        await togetherai_image_example()
        await togetherai_embedding_example()
    else:
        print("ℹ️  No API key found, running showcase only...\n")
    
    await togetherai_model_showcase()
    
    print("\n🎉 Examples completed!")
    print("For more information, visit: https://docs.together.ai/")


if __name__ == "__main__":
    asyncio.run(main())