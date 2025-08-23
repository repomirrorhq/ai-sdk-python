"""
Comprehensive Amazon Bedrock Provider Example
=============================================

This example demonstrates the complete capabilities of the Bedrock provider including:
- Text generation with various models (Claude, Llama, Titan)
- Embedding generation with Titan and Cohere models
- Image generation with Nova Canvas and Titan Image Generator
- AWS authentication methods (SigV4 and API key)

Requirements:
    pip install ai-sdk[bedrock]
    # or
    pip install ai-sdk boto3

Setup:
    export AWS_ACCESS_KEY_ID=your_access_key
    export AWS_SECRET_ACCESS_KEY=your_secret_key
    export AWS_REGION=us-east-1
    # or set BEDROCK_API_KEY for API key authentication
"""

import asyncio
import os
from ai_sdk import generateText, streamText, generateObject, embed, generateImage
from ai_sdk.providers import create_bedrock


async def demonstrate_bedrock_capabilities():
    """Demonstrate all Bedrock provider capabilities."""
    
    print("🚀 Amazon Bedrock Provider - Complete Demonstration")
    print("=" * 60)
    
    # Create Bedrock provider with AWS credentials
    bedrock = create_bedrock(
        region=os.getenv("AWS_REGION", "us-east-1"),
        # Credentials will be loaded from environment or AWS credential chain
    )
    
    # 1. Text Generation with Different Models
    print("\n1. 📝 TEXT GENERATION EXAMPLES")
    print("-" * 40)
    
    # Claude 3.5 Sonnet - Best for complex reasoning
    print("\n🧠 Claude 3.5 Sonnet (Complex Reasoning):")
    claude_result = await generateText(
        model=bedrock.language_model("anthropic.claude-3-5-sonnet-20241022-v2:0"),
        prompt="Explain quantum entanglement in simple terms with an analogy",
        max_tokens=200
    )
    print(f"Response: {claude_result.text}")
    print(f"Tokens: {claude_result.usage.total_tokens}")
    
    # Amazon Titan - Good for general tasks
    print("\n🏢 Amazon Titan Text Express (General Purpose):")
    titan_result = await generateText(
        model=bedrock.language_model("amazon.titan-text-express-v1:0"),
        prompt="Write a brief product description for a smart home device",
        max_tokens=150
    )
    print(f"Response: {titan_result.text}")
    print(f"Tokens: {titan_result.usage.total_tokens}")
    
    # Meta Llama - Great for coding and analysis
    print("\n🦙 Meta Llama 3.1 70B (Code & Analysis):")
    llama_result = await generateText(
        model=bedrock.language_model("meta.llama3-1-70b-instruct-v1:0"),
        prompt="Write a Python function to calculate fibonacci sequence",
        max_tokens=200
    )
    print(f"Response: {llama_result.text}")
    print(f"Tokens: {llama_result.usage.total_tokens}")
    
    # 2. Streaming Generation
    print("\n2. 🌊 STREAMING TEXT GENERATION")
    print("-" * 40)
    
    print("\n⚡ Streaming Claude response:")
    stream = streamText(
        model=bedrock.language_model("anthropic.claude-3-haiku-20240307-v1:0"),
        prompt="Tell me a short story about AI and creativity (keep it under 100 words)",
        max_tokens=150
    )
    
    full_text = ""
    async for chunk in stream:
        if chunk.type == "text-delta":
            print(chunk.text, end="", flush=True)
            full_text += chunk.text
        elif chunk.type == "finish":
            print(f"\n\n📊 Streaming Stats: {chunk.usage.total_tokens} tokens")
    
    # 3. Structured Output Generation
    print("\n3. 🏗️  STRUCTURED OUTPUT WITH BEDROCK")
    print("-" * 40)
    
    from pydantic import BaseModel, Field
    from typing import List
    
    class ProductAnalysis(BaseModel):
        name: str = Field(description="Product name")
        category: str = Field(description="Product category")
        pros: List[str] = Field(description="List of advantages")
        cons: List[str] = Field(description="List of disadvantages") 
        rating: int = Field(description="Rating out of 10", ge=1, le=10)
        summary: str = Field(description="Brief summary")
    
    print("\n📋 Generating structured product analysis:")
    structured_result = await generateObject(
        model=bedrock.language_model("anthropic.claude-3-sonnet-20240229-v1:0"),
        schema=ProductAnalysis,
        prompt="Analyze the iPhone 15 Pro as a product",
    )
    
    analysis = structured_result.object
    print(f"Product: {analysis.name}")
    print(f"Category: {analysis.category}")
    print(f"Rating: {analysis.rating}/10")
    print(f"Pros: {', '.join(analysis.pros)}")
    print(f"Cons: {', '.join(analysis.cons)}")
    print(f"Summary: {analysis.summary}")
    print(f"Tokens used: {structured_result.usage.total_tokens}")
    
    # 4. Embedding Generation
    print("\n4. 🔍 EMBEDDING GENERATION")
    print("-" * 40)
    
    # Titan embeddings - great for general purpose
    print("\n📊 Amazon Titan Text Embeddings v2:")
    texts_to_embed = [
        "Machine learning is transforming healthcare",
        "Cloud computing enables scalable applications", 
        "Artificial intelligence enhances decision making"
    ]
    
    titan_embeddings = []
    for text in texts_to_embed:
        embedding_result = await embed(
            model=bedrock.embedding_model("amazon.titan-embed-text-v2:0"),
            text=text,
            provider_options={
                "bedrock": {
                    "dimensions": 512,  # Smaller dimension for demo
                    "normalize": True
                }
            }
        )
        titan_embeddings.append(embedding_result.embedding)
        print(f"Text: '{text[:50]}...'")
        print(f"Embedding dimensions: {len(embedding_result.embedding)}")
        print(f"First 5 values: {embedding_result.embedding[:5]}")
        print(f"Tokens used: {embedding_result.usage.total_tokens}\n")
    
    # Calculate similarity between embeddings
    import numpy as np
    
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    sim_1_2 = cosine_similarity(titan_embeddings[0], titan_embeddings[1])
    sim_1_3 = cosine_similarity(titan_embeddings[0], titan_embeddings[2])
    sim_2_3 = cosine_similarity(titan_embeddings[1], titan_embeddings[2])
    
    print("🔗 Embedding Similarities:")
    print(f"Text 1 ↔ Text 2: {sim_1_2:.4f}")
    print(f"Text 1 ↔ Text 3: {sim_1_3:.4f}")
    print(f"Text 2 ↔ Text 3: {sim_2_3:.4f}")
    
    # Cohere multilingual embeddings
    print("\n🌍 Cohere Multilingual Embeddings:")
    multilingual_texts = [
        "Hello, how are you?",
        "Hola, ¿cómo estás?",
        "Bonjour, comment allez-vous?"
    ]
    
    for text in multilingual_texts:
        cohere_result = await embed(
            model=bedrock.embedding_model("cohere.embed-multilingual-v3:0"),
            text=text
        )
        print(f"Text: '{text}'")
        print(f"Embedding dimensions: {len(cohere_result.embedding)}")
        print(f"Tokens used: {cohere_result.usage.total_tokens}\n")
    
    # 5. Image Generation
    print("\n5. 🎨 IMAGE GENERATION")
    print("-" * 40)
    
    # Nova Canvas - Advanced image generation
    print("\n🖼️  Amazon Nova Canvas (Advanced Generation):")
    try:
        nova_result = await generateImage(
            model=bedrock.image_model("us.amazon.nova-canvas-v1:0"),
            prompt="A serene mountain landscape at sunset with a crystal clear lake reflection",
            options={
                "size": "1024x1024",
                "n": 1,
                "provider_options": {
                    "bedrock": {
                        "quality": "premium",
                        "cfg_scale": 8.0,
                        "negative_text": "blurry, low quality, distorted"
                    }
                }
            }
        )
        print(f"Generated {len(nova_result.images)} image(s)")
        print(f"Image data length: {len(nova_result.images[0])} characters (base64)")
        print(f"Model used: {nova_result.response_metadata['model_id']}")
        print("✅ Nova Canvas generation successful!")
        
    except Exception as e:
        print(f"⚠️ Nova Canvas not available in this region: {e}")
    
    # Titan Image Generator - Reliable image generation
    print("\n🏔️ Amazon Titan Image Generator:")
    try:
        titan_img_result = await generateImage(
            model=bedrock.image_model("amazon.titan-image-generator-v2:0"),
            prompt="A futuristic city with flying cars and neon lights",
            options={
                "size": "1024x1024",
                "seed": 42,
                "provider_options": {
                    "bedrock": {
                        "quality": "premium",
                        "negative_text": "dark, gloomy"
                    }
                }
            }
        )
        print(f"Generated {len(titan_img_result.images)} image(s)")
        print(f"Image data length: {len(titan_img_result.images[0])} characters (base64)")
        print("✅ Titan Image generation successful!")
        
    except Exception as e:
        print(f"⚠️ Titan Image Generator error: {e}")
    
    # 6. Advanced Authentication Examples
    print("\n6. 🔐 AUTHENTICATION METHODS")
    print("-" * 40)
    
    # Example 1: Explicit credentials
    print("\n🔑 Method 1: Explicit AWS Credentials")
    bedrock_explicit = create_bedrock(
        region="us-east-1",
        credentials={
            "access_key_id": "your-access-key-id",
            "secret_access_key": "your-secret-access-key",
            # "session_token": "optional-session-token"
        }
    )
    print("✅ Provider created with explicit credentials")
    
    # Example 2: API Key authentication (simpler)
    print("\n🎫 Method 2: API Key Authentication") 
    if os.getenv("BEDROCK_API_KEY"):
        bedrock_apikey = create_bedrock(
            region="us-east-1",
            api_key=os.getenv("BEDROCK_API_KEY")
        )
        print("✅ Provider created with API key")
    else:
        print("💡 Set BEDROCK_API_KEY environment variable for API key auth")
    
    # Example 3: Custom credential provider
    print("\n⚙️ Method 3: Custom Credential Provider")
    
    async def custom_credential_provider():
        # Your custom logic to fetch credentials
        return {
            "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "session_token": os.getenv("AWS_SESSION_TOKEN")
        }
    
    bedrock_custom = create_bedrock(
        region="us-east-1",
        credential_provider=custom_credential_provider
    )
    print("✅ Provider created with custom credential provider")
    
    # 7. Multi-Model Comparison
    print("\n7. ⚖️  MULTI-MODEL COMPARISON")
    print("-" * 40)
    
    comparison_prompt = "Explain the benefits of renewable energy in exactly 50 words"
    models_to_compare = [
        ("anthropic.claude-3-haiku-20240307-v1:0", "Claude 3 Haiku"),
        ("amazon.titan-text-express-v1:0", "Titan Express"),
        ("cohere.command-text-v14:0", "Cohere Command")
    ]
    
    print(f"\n📊 Comparing models on prompt: '{comparison_prompt}'")
    print()
    
    for model_id, model_name in models_to_compare:
        try:
            result = await generateText(
                model=bedrock.language_model(model_id),
                prompt=comparison_prompt,
                max_tokens=75
            )
            word_count = len(result.text.split())
            print(f"🤖 {model_name}:")
            print(f"Response ({word_count} words): {result.text}")
            print(f"Tokens: {result.usage.total_tokens}")
            print()
        except Exception as e:
            print(f"⚠️ {model_name} error: {e}")
            print()
    
    print("🎉 BEDROCK DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("\n✅ Successfully demonstrated:")
    print("   • Text generation with multiple models")
    print("   • Streaming responses") 
    print("   • Structured output generation")
    print("   • Embedding generation (Titan & Cohere)")
    print("   • Image generation (Nova & Titan)")
    print("   • Multiple authentication methods")
    print("   • Multi-model comparison")
    print("\n🚀 Amazon Bedrock is ready for production use!")
    
    # Clean up
    await bedrock.close()


if __name__ == "__main__":
    # Run the comprehensive demonstration
    asyncio.run(demonstrate_bedrock_capabilities())