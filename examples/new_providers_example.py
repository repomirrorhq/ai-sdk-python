"""
Example demonstrating the newly integrated providers: Cohere, xAI, Perplexity, and DeepSeek.

This example showcases the expanded AI SDK Python ecosystem with multiple providers
offering different capabilities:
- Cohere: Enterprise RAG and embeddings
- xAI: Real-time AI with web knowledge  
- Perplexity: Search-augmented generation
- DeepSeek: High-performance reasoning
"""

import asyncio
import os
from ai_sdk import (
    generate_text,
    stream_text, 
    embed,
    embed_many,
    create_cohere,
    create_xai,
    create_perplexity,
    create_deepseek,
)

async def demonstrate_cohere():
    """Demonstrate Cohere's enterprise RAG capabilities."""
    print("🤖 Cohere Provider - Enterprise RAG & Embeddings")
    print("=" * 60)
    
    try:
        # Create Cohere provider
        cohere = create_cohere()
        
        # Test text generation with Command-R
        print("\n📝 Text Generation with Command-R:")
        result = await generate_text(
            model=cohere.language_model("command-r"),
            prompt="Explain the benefits of retrieval-augmented generation (RAG) for enterprise applications.",
            max_output_tokens=200
        )
        print(f"Response: {result.text[:300]}...")
        print(f"Usage: {result.usage.total_tokens} tokens")
        
        # Test embeddings with multilingual model
        print("\n🔍 Text Embeddings for RAG:")
        embedding_result = await embed(
            model=cohere.embedding_model("embed-multilingual-v3.0"),
            values=["Enterprise document search", "Knowledge management system"]
        )
        print(f"Generated {len(embedding_result.embeddings)} embeddings")
        print(f"Embedding dimension: {len(embedding_result.embeddings[0])}")
        
    except Exception as e:
        print(f"Cohere error (likely missing API key): {e}")


async def demonstrate_xai():
    """Demonstrate xAI's Grok models with real-time capabilities."""
    print("\n\n🚀 xAI Provider - Grok with Real-time Knowledge")
    print("=" * 60)
    
    try:
        # Create xAI provider
        xai = create_xai()
        
        # Test with Grok model
        print("\n🧠 Grok Reasoning:")
        result = await generate_text(
            model=xai.language_model("grok-beta"),
            prompt="What are the latest developments in AI that happened this week?",
            max_output_tokens=300
        )
        print(f"Grok Response: {result.text[:400]}...")
        
        # Test streaming with fast model
        print("\n⚡ Streaming with Grok (first few chunks):")
        async for chunk in stream_text(
            model=xai.language_model("grok-beta"),
            prompt="Explain quantum computing in simple terms.",
            max_output_tokens=150
        ):
            if hasattr(chunk, 'delta'):
                print(f"Delta: {chunk.delta}", end="")
                break  # Just show first chunk for demo
        print("...")
        
    except Exception as e:
        print(f"xAI error (likely missing API key): {e}")


async def demonstrate_perplexity():
    """Demonstrate Perplexity's search-augmented generation."""
    print("\n\n🔍 Perplexity Provider - Search-Augmented AI")
    print("=" * 60)
    
    try:
        # Create Perplexity provider
        perplexity = create_perplexity()
        
        # Test search-augmented generation
        print("\n🌐 Search-Enhanced Response:")
        result = await generate_text(
            model=perplexity.language_model("llama-3.1-sonar-large-128k-online"),
            prompt="What are the current trends in sustainable energy technology?",
            max_output_tokens=250
        )
        print(f"Perplexity Response: {result.text[:400]}...")
        
        # Check for citations in provider metadata
        if hasattr(result, 'provider_metadata') and result.provider_metadata:
            print("✅ Response includes real-time web information")
        
    except Exception as e:
        print(f"Perplexity error (likely missing API key): {e}")


async def demonstrate_deepseek():
    """Demonstrate DeepSeek's high-performance reasoning."""
    print("\n\n🧮 DeepSeek Provider - Advanced Reasoning")
    print("=" * 60)
    
    try:
        # Create DeepSeek provider
        deepseek = create_deepseek()
        
        # Test reasoning with DeepSeek model
        print("\n🤔 Advanced Reasoning:")
        result = await generate_text(
            model=deepseek.language_model("deepseek-chat"),
            prompt="Solve this step by step: If a train travels 120 km in 2 hours, and then travels 180 km in 3 hours, what is the average speed for the entire journey?",
            max_output_tokens=300
        )
        print(f"DeepSeek Response: {result.text[:400]}...")
        
        # Test with reasoning model if available
        try:
            print("\n🔬 Using DeepSeek Reasoner:")
            reasoner_result = await generate_text(
                model=deepseek.language_model("deepseek-reasoner"),
                prompt="Analyze the potential impacts of artificial intelligence on healthcare over the next decade.",
                max_output_tokens=200
            )
            print(f"Reasoner Response: {reasoner_result.text[:300]}...")
        except:
            print("DeepSeek reasoner model not available or accessible")
        
    except Exception as e:
        print(f"DeepSeek error (likely missing API key): {e}")


async def demonstrate_multi_provider_comparison():
    """Compare responses from multiple providers for the same prompt."""
    print("\n\n⚖️ Multi-Provider Comparison")
    print("=" * 60)
    
    prompt = "What is the most important challenge facing humanity today?"
    
    providers = [
        ("Cohere", create_cohere, "command-r"),
        ("xAI", create_xai, "grok-beta"), 
        ("Perplexity", create_perplexity, "llama-3.1-sonar-large-128k-online"),
        ("DeepSeek", create_deepseek, "deepseek-chat"),
    ]
    
    for name, provider_factory, model_id in providers:
        try:
            provider = provider_factory()
            result = await generate_text(
                model=provider.language_model(model_id),
                prompt=prompt,
                max_output_tokens=150
            )
            print(f"\n{name}: {result.text[:200]}...")
        except Exception as e:
            print(f"\n{name}: Error - {str(e)[:100]}...")


async def demonstrate_embeddings_comparison():
    """Compare embedding capabilities across providers."""
    print("\n\n📊 Embeddings Comparison")
    print("=" * 60)
    
    texts = [
        "Machine learning applications in healthcare",
        "Natural language processing for customer service",
        "Computer vision for autonomous vehicles"
    ]
    
    # Test Cohere embeddings
    try:
        cohere = create_cohere()
        cohere_embeddings = await embed_many(
            model=cohere.embedding_model("embed-english-v3.0"),
            values=texts
        )
        print(f"✅ Cohere embeddings: {len(cohere_embeddings.embeddings)} vectors of {len(cohere_embeddings.embeddings[0])} dimensions")
    except Exception as e:
        print(f"❌ Cohere embeddings error: {str(e)[:100]}...")


def show_provider_capabilities():
    """Show capabilities of newly integrated providers."""
    print("\n\n🎯 Provider Capabilities Summary")
    print("=" * 60)
    
    capabilities = {
        "Cohere": {
            "Models": ["command-r-plus", "command-r", "command"],
            "Specialties": ["Enterprise RAG", "Multilingual embeddings", "Document search"],
            "Embeddings": ["embed-english-v3.0", "embed-multilingual-v3.0"],
            "Features": ["Tool calling", "Citations", "JSON mode"]
        },
        "xAI": {
            "Models": ["grok-4", "grok-3", "grok-2-vision"],
            "Specialties": ["Real-time knowledge", "Web search", "Reasoning"],
            "Embeddings": None,
            "Features": ["Streaming", "Tool calling", "Multimodal"]
        },
        "Perplexity": {
            "Models": ["llama-3.1-sonar-large-128k-online", "llama-3.1-sonar-small-128k-online"],
            "Specialties": ["Search-augmented generation", "Real-time information", "Citations"],
            "Embeddings": None,
            "Features": ["Web search", "Source attribution", "Current events"]
        },
        "DeepSeek": {
            "Models": ["deepseek-chat", "deepseek-reasoner", "deepseek-coder"],
            "Specialties": ["Advanced reasoning", "Code generation", "Mathematical problem solving"],
            "Embeddings": None,
            "Features": ["Step-by-step reasoning", "Caching metrics", "High performance"]
        }
    }
    
    for provider, info in capabilities.items():
        print(f"\n🔸 {provider}:")
        print(f"   Models: {', '.join(info['Models'][:2])}...")
        print(f"   Specialties: {', '.join(info['Specialties'])}")
        if info['Embeddings']:
            print(f"   Embeddings: {', '.join(info['Embeddings'])}")
        print(f"   Key Features: {', '.join(info['Features'])}")


async def main():
    """Run all demonstrations."""
    print("🌟 AI SDK Python - New Provider Integration Demo")
    print("=" * 80)
    print("Demonstrating 4 newly integrated providers expanding the AI ecosystem")
    print("\n💡 Note: Set environment variables for API keys:")
    print("   - COHERE_API_KEY")
    print("   - XAI_API_KEY") 
    print("   - PERPLEXITY_API_KEY")
    print("   - DEEPSEEK_API_KEY")
    
    # Show capabilities overview
    show_provider_capabilities()
    
    # Demonstrate each provider
    await demonstrate_cohere()
    await demonstrate_xai()
    await demonstrate_perplexity() 
    await demonstrate_deepseek()
    
    # Multi-provider demos
    await demonstrate_multi_provider_comparison()
    await demonstrate_embeddings_comparison()
    
    print("\n\n✨ Integration Complete!")
    print("=" * 80)
    print("🎯 AI SDK Python now supports 12 major providers:")
    print("   Core: OpenAI, Anthropic, Google, Azure")
    print("   Performance: Groq, Together, Mistral")  
    print("   Cloud: AWS Bedrock")
    print("   NEW: Cohere, xAI, Perplexity, DeepSeek")
    print("\n🚀 The Python AI ecosystem is now comprehensive and production-ready!")


if __name__ == "__main__":
    asyncio.run(main())