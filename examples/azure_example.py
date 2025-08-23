#!/usr/bin/env python3
"""
Azure OpenAI Provider Example

This example demonstrates how to use the Azure OpenAI provider with various models
and features including text generation, streaming, embeddings, and structured objects.

Setup:
1. Set your Azure OpenAI credentials:
   export AZURE_API_KEY="your-azure-api-key"
   export AZURE_RESOURCE_NAME="your-resource-name"

2. Deploy models in Azure OpenAI Studio (use these as deployment IDs):
   - GPT-4 or GPT-3.5-turbo for chat
   - text-embedding-ada-002 for embeddings

3. Run: python azure_example.py
"""

import asyncio
import os
from typing import List

from ai_sdk import generate_object, generate_text, stream_object, stream_text, embed
from ai_sdk.providers.azure import create_azure
from pydantic import BaseModel


# Example data models for structured generation
class WeatherInfo(BaseModel):
    location: str
    temperature: int
    condition: str
    humidity: int


class BookRecommendation(BaseModel):
    title: str
    author: str
    genre: str
    rating: float
    description: str


async def main():
    print("🚀 Azure OpenAI Provider Examples\n")
    
    # Create Azure provider
    try:
        azure = create_azure(
            # Optionally specify credentials directly:
            # api_key="your-azure-api-key",
            # resource_name="your-resource-name",
            
            # Use deployment-based URLs if needed for some models
            # use_deployment_based_urls=True,
            
            # Custom API version (optional)
            # api_version="2024-08-01-preview",
        )
        print("✅ Azure OpenAI provider initialized")
    except ValueError as e:
        print(f"❌ Failed to initialize Azure provider: {e}")
        print("\n💡 Make sure to set AZURE_API_KEY and AZURE_RESOURCE_NAME environment variables")
        return
    
    print("\n" + "="*60)
    
    # 1. Basic text generation
    print("1️⃣  Basic Text Generation")
    print("-" * 30)
    
    try:
        result = await generate_text(
            model=azure.chat("gpt-35-turbo"),  # Use your deployment ID
            prompt="Write a haiku about artificial intelligence.",
        )
        print(f"Generated text: {result.text}")
        print(f"Usage: {result.usage}")
    except Exception as e:
        print(f"❌ Text generation failed: {e}")
    
    print("\n" + "="*60)
    
    # 2. Streaming text generation
    print("2️⃣  Streaming Text Generation")
    print("-" * 35)
    
    try:
        print("🌊 Streaming response: ", end="", flush=True)
        
        async for part in stream_text(
            model=azure.chat("gpt-35-turbo"),  # Use your deployment ID
            prompt="Explain quantum computing in simple terms.",
            max_tokens=150,
        ):
            if hasattr(part, 'text'):
                print(part.text, end="", flush=True)
        
        print("\n")
    except Exception as e:
        print(f"❌ Streaming failed: {e}")
    
    print("\n" + "="*60)
    
    # 3. Conversation with multiple messages
    print("3️⃣  Multi-turn Conversation")
    print("-" * 30)
    
    try:
        result = await generate_text(
            model=azure.chat("gpt-35-turbo"),  # Use your deployment ID
            messages=[
                {"role": "system", "content": "You are a helpful cooking assistant."},
                {"role": "user", "content": "I have eggs, flour, and milk. What can I make?"},
                {"role": "assistant", "content": "You can make pancakes! Would you like a recipe?"},
                {"role": "user", "content": "Yes, please give me a simple recipe."},
            ],
            temperature=0.7,
        )
        print(f"Assistant: {result.text}")
    except Exception as e:
        print(f"❌ Conversation failed: {e}")
    
    print("\n" + "="*60)
    
    # 4. Structured object generation
    print("4️⃣  Structured Object Generation")
    print("-" * 38)
    
    try:
        weather = await generate_object(
            model=azure.chat("gpt-35-turbo"),  # Use your deployment ID
            prompt="Generate weather information for Paris, France today.",
            schema=WeatherInfo,
        )
        print(f"Weather data: {weather}")
        print(f"Location: {weather.location}")
        print(f"Temperature: {weather.temperature}°C")
        print(f"Condition: {weather.condition}")
    except Exception as e:
        print(f"❌ Object generation failed: {e}")
    
    print("\n" + "="*60)
    
    # 5. Streaming structured objects
    print("5️⃣  Streaming Object Generation")
    print("-" * 36)
    
    try:
        print("📚 Generating book recommendation...")
        
        async for part in stream_object(
            model=azure.chat("gpt-35-turbo"),  # Use your deployment ID  
            prompt="Recommend a science fiction book published after 2010.",
            schema=BookRecommendation,
        ):
            if hasattr(part, 'object') and part.object:
                print(f"📖 Current object: {part.object}")
            elif hasattr(part, 'text_delta'):
                print(f"📝 Text delta: {part.text_delta}")
    except Exception as e:
        print(f"❌ Object streaming failed: {e}")
    
    print("\n" + "="*60)
    
    # 6. Embeddings (if you have an embedding model deployed)
    print("6️⃣  Text Embeddings")
    print("-" * 20)
    
    try:
        # Create embedding model
        embedding_model = azure.embedding("text-embedding-ada-002")  # Use your deployment ID
        
        # Generate embeddings for multiple texts
        texts = [
            "Machine learning is transforming technology",
            "Artificial intelligence enables automation",
            "Deep learning uses neural networks",
        ]
        
        embeddings = await embed(
            model=embedding_model,
            values=texts,
        )
        
        print(f"Generated {len(embeddings.embeddings)} embeddings")
        print(f"Embedding dimensions: {len(embeddings.embeddings[0])}")
        print(f"Usage: {embeddings.usage}")
        
        # Calculate similarity between first two texts
        from ai_sdk.utils import cosine_similarity
        similarity = cosine_similarity(embeddings.embeddings[0], embeddings.embeddings[1])
        print(f"Similarity between first two texts: {similarity:.3f}")
        
    except Exception as e:
        print(f"❌ Embeddings failed: {e}")
        print("💡 Make sure you have a text-embedding model deployed in Azure")
    
    print("\n" + "="*60)
    print("✅ Azure OpenAI examples completed!")
    print("\n💡 Tips for Azure OpenAI:")
    print("   • Use deployment IDs as model names (not OpenAI model names)")
    print("   • Make sure your deployed models match the ones used in examples")
    print("   • Monitor token usage and costs in Azure portal")
    print("   • Consider using deployment-based URLs for certain models if needed")


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("AZURE_API_KEY"):
        print("❌ AZURE_API_KEY environment variable is not set")
        print("Please set it with: export AZURE_API_KEY='your-azure-api-key'")
        exit(1)
    
    if not os.getenv("AZURE_RESOURCE_NAME"):
        print("❌ AZURE_RESOURCE_NAME environment variable is not set") 
        print("Please set it with: export AZURE_RESOURCE_NAME='your-resource-name'")
        exit(1)
    
    print("Azure OpenAI API Key: ✅ Found")
    print("Azure Resource Name: ✅ Found")
    
    asyncio.run(main())