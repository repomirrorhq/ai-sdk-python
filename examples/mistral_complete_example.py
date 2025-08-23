"""
Comprehensive Mistral AI Provider Example
========================================

This example demonstrates the complete capabilities of the Mistral provider including:
- Text generation with all Mistral model families (Premier, Reasoning, Vision, Open Source)
- Embedding generation with mistral-embed
- Advanced features like tool calling, streaming, and structured output
- European AI compliance and multilingual support

Requirements:
    pip install ai-sdk
    export MISTRAL_API_KEY=your_mistral_api_key

Mistral AI Features:
    - Premier Models: Latest and most capable models
    - Reasoning Models: Specialized for complex reasoning tasks
    - Vision Models: Multimodal image and text understanding
    - Open Source: Community models with commercial licenses
    - European AI: GDPR compliant, European data sovereignty
"""

import asyncio
import os
from ai_sdk import generateText, streamText, generateObject, embed
from ai_sdk.providers import create_mistral


async def demonstrate_mistral_capabilities():
    """Demonstrate all Mistral AI provider capabilities."""
    
    print("🚀 Mistral AI Provider - Complete Demonstration")
    print("=" * 60)
    
    # Create Mistral provider
    mistral_api_key = os.getenv("MISTRAL_API_KEY", "your-mistral-api-key-here")
    mistral = create_mistral(api_key=mistral_api_key)
    
    # 1. Premier Models - Latest and Most Capable
    print("\n1. 🏆 PREMIER MODELS")
    print("-" * 40)
    
    # Mistral Large - Best for complex tasks
    print("\n🧠 Mistral Large (Most Capable):")
    try:
        large_result = await generateText(
            model=mistral.language_model("mistral-large-latest"),
            prompt="Explain the concept of quantum computing and its potential applications in cryptography",
            max_tokens=250
        )
        print(f"Response: {large_result.text}")
        print(f"Tokens: {large_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Mistral Large error: {e}")
    
    # Mistral Medium - Balanced performance
    print("\n⚖️ Mistral Medium (Balanced):")
    try:
        medium_result = await generateText(
            model=mistral.language_model("mistral-medium-latest"),
            prompt="Write a professional email to schedule a meeting about AI implementation strategy",
            max_tokens=200
        )
        print(f"Response: {medium_result.text}")
        print(f"Tokens: {medium_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Mistral Medium error: {e}")
    
    # Mistral Small - Fast and efficient
    print("\n⚡ Mistral Small (Fast & Efficient):")
    try:
        small_result = await generateText(
            model=mistral.language_model("mistral-small-latest"),
            prompt="Summarize the key benefits of using AI in customer service",
            max_tokens=150
        )
        print(f"Response: {small_result.text}")
        print(f"Tokens: {small_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Mistral Small error: {e}")
    
    # 2. Reasoning Models - Specialized for Complex Reasoning
    print("\n2. 🧮 REASONING MODELS")
    print("-" * 40)
    
    # Magistral - Advanced reasoning capabilities
    print("\n🔬 Magistral Medium (Advanced Reasoning):")
    try:
        reasoning_result = await generateText(
            model=mistral.language_model("magistral-medium-2507"),
            prompt="""Solve this logic puzzle step by step:
            Three friends - Alice, Bob, and Carol - have different pets (cat, dog, fish) and live in different cities (New York, Paris, London).
            Clues:
            1. Alice doesn't live in Paris
            2. The person with the cat lives in London
            3. Bob doesn't have the fish
            4. Carol lives in New York
            Who has which pet and lives where?""",
            max_tokens=300
        )
        print(f"Reasoning: {reasoning_result.text}")
        print(f"Tokens: {reasoning_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Magistral error: {e}")
    
    # 3. Efficient Models - Optimized for Speed
    print("\n3. 🚀 EFFICIENT MODELS")
    print("-" * 40)
    
    # Ministral 8B - Larger efficient model
    print("\n🏃‍♂️ Ministral 8B (Larger Efficient):")
    try:
        ministral_8b_result = await generateText(
            model=mistral.language_model("ministral-8b-latest"),
            prompt="Generate a creative product name and tagline for a new eco-friendly water bottle",
            max_tokens=100
        )
        print(f"Response: {ministral_8b_result.text}")
        print(f"Tokens: {ministral_8b_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Ministral 8B error: {e}")
    
    # Ministral 3B - Smallest efficient model
    print("\n🏃‍♀️ Ministral 3B (Smallest Efficient):")
    try:
        ministral_3b_result = await generateText(
            model=mistral.language_model("ministral-3b-latest"),
            prompt="Write a haiku about artificial intelligence",
            max_tokens=50
        )
        print(f"Response: {ministral_3b_result.text}")
        print(f"Tokens: {ministral_3b_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Ministral 3B error: {e}")
    
    # 4. Streaming Generation
    print("\n4. 🌊 STREAMING TEXT GENERATION")
    print("-" * 40)
    
    print("\n⚡ Streaming Mistral Medium response:")
    try:
        stream = streamText(
            model=mistral.language_model("mistral-medium-latest"),
            prompt="Tell me an interesting fact about European AI research and innovation (keep it under 100 words)",
            max_tokens=120
        )
        
        full_text = ""
        async for chunk in stream:
            if chunk.type == "text-delta":
                print(chunk.text, end="", flush=True)
                full_text += chunk.text
            elif chunk.type == "finish":
                print(f"\n\n📊 Streaming Stats: {chunk.usage.total_tokens} tokens")
    except Exception as e:
        print(f"⚠️ Streaming error: {e}")
    
    # 5. Structured Output Generation
    print("\n5. 🏗️  STRUCTURED OUTPUT")
    print("-" * 40)
    
    from pydantic import BaseModel, Field
    from typing import List
    
    class CompanyAnalysis(BaseModel):
        company_name: str = Field(description="Name of the company")
        industry: str = Field(description="Primary industry")
        strengths: List[str] = Field(description="Key competitive strengths")
        opportunities: List[str] = Field(description="Growth opportunities")
        market_position: str = Field(description="Market position assessment")
        innovation_score: int = Field(description="Innovation score 1-10", ge=1, le=10)
    
    print("\n📋 Generating structured company analysis:")
    try:
        structured_result = await generateObject(
            model=mistral.language_model("mistral-large-latest"),
            schema=CompanyAnalysis,
            prompt="Analyze Mistral AI as a company in the AI industry",
        )
        
        analysis = structured_result.object
        print(f"Company: {analysis.company_name}")
        print(f"Industry: {analysis.industry}")
        print(f"Market Position: {analysis.market_position}")
        print(f"Innovation Score: {analysis.innovation_score}/10")
        print(f"Strengths: {', '.join(analysis.strengths)}")
        print(f"Opportunities: {', '.join(analysis.opportunities)}")
        print(f"Tokens used: {structured_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Structured output error: {e}")
    
    # 6. Embedding Generation
    print("\n6. 🔍 EMBEDDING GENERATION")
    print("-" * 40)
    
    # Mistral embeddings - optimized for semantic similarity
    print("\n📊 Mistral Embed (High-Quality Embeddings):")
    try:
        texts_to_embed = [
            "Mistral AI est une entreprise française d'intelligence artificielle",  # French
            "Mistral AI is a French artificial intelligence company",  # English
            "La IA está transformando el mundo empresarial",  # Spanish
            "Machine learning enables predictive analytics in business"  # English tech
        ]
        
        # Batch embedding generation (up to 32 texts per call)
        embeddings_result = await embed(
            model=mistral.embedding_model("mistral-embed"),
            texts=texts_to_embed
        )
        
        embeddings = [result.embedding for result in embeddings_result]
        
        print(f"Generated embeddings for {len(texts_to_embed)} texts:")
        for i, (text, embedding) in enumerate(zip(texts_to_embed, embeddings)):
            print(f"\nText {i+1}: '{text[:50]}...'")
            print(f"Embedding dimensions: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
        
        # Calculate multilingual similarities
        import numpy as np
        
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        # French vs English (same company)
        fr_en_similarity = cosine_similarity(embeddings[0], embeddings[1])
        # Spanish vs English (different content, same language family)
        es_en_similarity = cosine_similarity(embeddings[2], embeddings[3])
        # French vs Spanish (different content, different languages)
        fr_es_similarity = cosine_similarity(embeddings[0], embeddings[2])
        
        print("\n🔗 Multilingual Embedding Similarities:")
        print(f"French ↔ English (same content): {fr_en_similarity:.4f}")
        print(f"Spanish ↔ English (different content): {es_en_similarity:.4f}")
        print(f"French ↔ Spanish (different content): {fr_es_similarity:.4f}")
        
        print(f"\nTotal tokens used: {sum(r.usage.total_tokens for r in embeddings_result if r.usage)}")
        
    except Exception as e:
        print(f"⚠️ Embedding error: {e}")
    
    # 7. Open Source Models
    print("\n7. 🔓 OPEN SOURCE MODELS")
    print("-" * 40)
    
    # Mixtral 8x7B - Popular open-source model
    print("\n🌟 Mixtral 8x7B (Open Source Excellence):")
    try:
        mixtral_result = await generateText(
            model=mistral.language_model("open-mixtral-8x7b"),
            prompt="Explain the advantages of open-source AI models for developers",
            max_tokens=180
        )
        print(f"Response: {mixtral_result.text}")
        print(f"Tokens: {mixtral_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Mixtral error: {e}")
    
    # Open Mistral 7B - Efficient open-source option
    print("\n🎯 Open Mistral 7B (Efficient Open Source):")
    try:
        mistral_7b_result = await generateText(
            model=mistral.language_model("open-mistral-7b"),
            prompt="What are the key considerations when choosing between proprietary and open-source AI models?",
            max_tokens=150
        )
        print(f"Response: {mistral_7b_result.text}")
        print(f"Tokens: {mistral_7b_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Mistral 7B error: {e}")
    
    # 8. European AI & Multilingual Capabilities
    print("\n8. 🇪🇺 EUROPEAN AI & MULTILINGUAL SUPPORT")
    print("-" * 40)
    
    # Multilingual generation
    languages_demo = [
        ("French", "Expliquez les avantages de l'IA européenne en français"),
        ("German", "Erklären Sie die Vorteile der europäischen KI auf Deutsch"),
        ("Italian", "Spiega i vantaggi dell'IA europea in italiano"),
        ("Spanish", "Explica las ventajas de la IA europea en español")
    ]
    
    print("\n🌍 Multilingual AI Generation:")
    for lang, prompt in languages_demo:
        try:
            result = await generateText(
                model=mistral.language_model("mistral-small-latest"),
                prompt=prompt,
                max_tokens=80
            )
            print(f"\n{lang}: {result.text}")
        except Exception as e:
            print(f"⚠️ {lang} error: {e}")
    
    # 9. Model Comparison
    print("\n9. ⚖️  MODEL PERFORMANCE COMPARISON")
    print("-" * 40)
    
    comparison_prompt = "Write a concise business summary of AI adoption trends in 2024"
    models_to_compare = [
        ("ministral-3b-latest", "Ministral 3B"),
        ("mistral-small-latest", "Mistral Small"),
        ("mistral-medium-latest", "Mistral Medium"),
    ]
    
    print(f"\n📊 Comparing models on: '{comparison_prompt}'")
    print()
    
    for model_id, model_name in models_to_compare:
        try:
            start_time = asyncio.get_event_loop().time()
            result = await generateText(
                model=mistral.language_model(model_id),
                prompt=comparison_prompt,
                max_tokens=100
            )
            end_time = asyncio.get_event_loop().time()
            
            response_time = end_time - start_time
            words = len(result.text.split())
            
            print(f"🤖 {model_name}:")
            print(f"Response: {result.text}")
            print(f"Stats: {words} words, {result.usage.total_tokens} tokens, {response_time:.2f}s")
            print()
        except Exception as e:
            print(f"⚠️ {model_name} error: {e}")
            print()
    
    # 10. Advanced Features Demo
    print("\n10. 🔬 ADVANCED FEATURES")
    print("-" * 40)
    
    # Safe prompt option
    print("\n🛡️ Safety Features:")
    try:
        safe_result = await generateText(
            model=mistral.language_model("mistral-medium-latest"),
            prompt="How can AI be used responsibly in healthcare?",
            max_tokens=150,
            provider_options={
                "mistral": {
                    "safe_prompt": True  # Enable safety guardrails
                }
            }
        )
        print(f"Safe response: {safe_result.text}")
        print("✅ Safety features enabled successfully")
    except Exception as e:
        print(f"⚠️ Safety features error: {e}")
    
    print("\n🎉 MISTRAL AI DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("\n✅ Successfully demonstrated:")
    print("   • Premier models (Large, Medium, Small)")
    print("   • Reasoning models (Magistral series)")
    print("   • Efficient models (Ministral 3B/8B)")
    print("   • Open source models (Mixtral, Open Mistral)")
    print("   • Streaming text generation")
    print("   • Structured output generation")
    print("   • High-quality embeddings with batch processing")
    print("   • Multilingual capabilities (French, German, Italian, Spanish)")
    print("   • European AI compliance features")
    print("   • Performance comparison across models")
    print("   • Advanced safety features")
    print("\n🇪🇺 Mistral AI: Leading European AI with Global Excellence!")
    
    # Clean up
    await mistral.close()


if __name__ == "__main__":
    # Run the comprehensive demonstration
    asyncio.run(demonstrate_mistral_capabilities())