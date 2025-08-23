"""
Comprehensive Perplexity Provider Example for AI SDK Python.

This example demonstrates the key features of the Perplexity provider:
1. Real-time search-augmented text generation
2. Citation and source tracking
3. Domain and recency filtering
4. Related question suggestions  
5. Streaming responses with search results
6. Current events and news queries
7. Research and analysis tasks
8. JSON mode for structured outputs
9. Error handling and best practices

Prerequisites:
- Install ai-sdk-python: pip install ai-sdk-python[perplexity]
- Set PERPLEXITY_API_KEY environment variable or pass api_key parameter
"""

import asyncio
import json
import os
from typing import Any, Dict, List

from ai_sdk import generate_text, stream_text
from ai_sdk.providers.perplexity import (
    PerplexityProvider,
    create_perplexity_provider,
    PerplexityLanguageModelId,
    PerplexityProviderSettings
)
from ai_sdk.core.types import ChatPrompt, UserMessage, SystemMessage


async def basic_search_generation():
    """Demonstrate basic search-augmented text generation."""
    print("=== Basic Search-Augmented Generation ===")
    
    # Create provider (uses PERPLEXITY_API_KEY from environment)
    provider = PerplexityProvider()
    model = provider.language_model("sonar-pro")
    
    # Query with current information needs
    result = await generate_text(
        model=model,
        prompt="What are the latest developments in artificial intelligence as of 2024?",
        max_output_tokens=400,
        temperature=0.3
    )
    
    print(f"Generated text: {result.text}")
    print(f"Usage: {result.usage}")
    print(f"Finish reason: {result.finish_reason}")
    
    # Show citations if available
    if result.provider_metadata and "perplexity" in result.provider_metadata:
        perplexity_meta = result.provider_metadata["perplexity"]
        
        if perplexity_meta.get("citations"):
            print("\nCitations:")
            for i, citation in enumerate(perplexity_meta["citations"], 1):
                print(f"  {i}. {citation.get('title', 'Untitled')}")
                print(f"     URL: {citation.get('url', 'No URL')}")
                if citation.get('snippet'):
                    print(f"     Snippet: {citation['snippet'][:100]}...")
        
        if perplexity_meta.get("related_questions"):
            print("\nRelated questions:")
            for i, question in enumerate(perplexity_meta["related_questions"], 1):
                print(f"  {i}. {question}")


async def streaming_with_citations():
    """Demonstrate streaming text generation with real-time citations."""
    print("\n=== Streaming with Real-time Citations ===")
    
    provider = PerplexityProvider()
    model = provider.language_model("sonar-reasoning")
    
    print("Question: What happened in the latest SpaceX launch?")
    print("Streaming response: ", end="", flush=True)
    
    citations = []
    
    async for part in stream_text(
        model=model,
        prompt="What happened in the latest SpaceX launch? Include technical details and outcomes.",
        max_output_tokens=500,
        temperature=0.2
    ):
        if hasattr(part, 'delta') and part.delta:
            print(part.delta, end="", flush=True)
        elif hasattr(part, 'finish_reason'):
            print(f"\n\nStream finished: {part.finish_reason}")
            if part.usage:
                print(f"Usage: {part.usage}")
            
            # Extract citations from metadata
            if part.provider_metadata and "perplexity" in part.provider_metadata:
                perplexity_meta = part.provider_metadata["perplexity"]
                if perplexity_meta.get("citations"):
                    citations = perplexity_meta["citations"]
    
    if citations:
        print("\nSources:")
        for i, citation in enumerate(citations, 1):
            print(f"  {i}. {citation.get('title', 'Untitled')} ({citation.get('domain', 'Unknown source')})")


async def domain_filtered_search():
    """Demonstrate domain-filtered search for academic sources."""
    print("\n=== Domain-Filtered Academic Search ===")
    
    provider = PerplexityProvider()
    model = provider.language_model("sonar-deep-research")
    
    # Create search options for academic sources
    search_options = provider.create_search_options(
        domain_filter=["arxiv.org", "scholar.google.com", "nature.com", "science.org"],
        return_citations=True,
        return_related_questions=True
    )
    
    result = await generate_text(
        model=model,
        prompt="What are the recent breakthroughs in quantum computing error correction?",
        max_output_tokens=600,
        temperature=0.2,
        provider_options=search_options
    )
    
    print(f"Academic research summary:\n{result.text}")
    
    if result.provider_metadata and "perplexity" in result.provider_metadata:
        perplexity_meta = result.provider_metadata["perplexity"]
        
        print("\nAcademic sources found:")
        if perplexity_meta.get("citations"):
            for citation in perplexity_meta["citations"]:
                domain = citation.get('domain', 'Unknown')
                if any(allowed_domain in domain for allowed_domain in search_options.get("search_domain_filter", [])):
                    print(f"  • {citation.get('title', 'Untitled')} ({domain})")


async def recency_filtered_news():
    """Demonstrate recency-filtered search for recent news."""
    print("\n=== Recent News with Time Filtering ===")
    
    provider = PerplexityProvider()
    model = provider.language_model("sonar-pro")
    
    # Search for very recent information
    search_options = provider.create_search_options(
        recency_filter="day",  # Last 24 hours
        return_citations=True,
        return_related_questions=False
    )
    
    result = await generate_text(
        model=model,
        prompt="What are today's most significant technology news and developments?",
        max_output_tokens=500,
        temperature=0.1,
        provider_options=search_options
    )
    
    print(f"Today's tech news:\n{result.text}")
    
    if result.provider_metadata and "perplexity" in result.provider_metadata:
        perplexity_meta = result.provider_metadata["perplexity"]
        
        print("\nSources from the last 24 hours:")
        if perplexity_meta.get("citations"):
            for citation in perplexity_meta["citations"]:
                publish_date = citation.get('publish_date', 'Unknown date')
                print(f"  • {citation.get('title', 'Untitled')} ({publish_date})")


async def research_analysis_task():
    """Demonstrate comprehensive research analysis."""
    print("\n=== Research Analysis Task ===")
    
    provider = PerplexityProvider()
    model = provider.language_model("sonar-reasoning-pro")
    
    # Multi-turn conversation for research
    prompt = ChatPrompt(messages=[
        SystemMessage(
            content="You are a research assistant specializing in technology analysis. Provide comprehensive, well-cited responses with multiple perspectives."
        ),
        UserMessage(
            content="Analyze the current state of autonomous vehicle technology. What are the key challenges, recent breakthroughs, and market predictions for 2025?"
        )
    ])
    
    result = await generate_text(
        model=model,
        prompt=prompt,
        max_output_tokens=800,
        temperature=0.3
    )
    
    print(f"Research Analysis:\n{result.text}")
    
    if result.provider_metadata and "perplexity" in result.provider_metadata:
        perplexity_meta = result.provider_metadata["perplexity"]
        
        if perplexity_meta.get("citations"):
            print(f"\nSources consulted: {len(perplexity_meta['citations'])}")
            
            # Group citations by type/domain
            news_sources = []
            academic_sources = []
            company_sources = []
            
            for citation in perplexity_meta["citations"]:
                domain = citation.get('domain', '').lower()
                title = citation.get('title', 'Untitled')
                
                if any(news in domain for news in ['news', 'reuters', 'bloomberg', 'techcrunch']):
                    news_sources.append(title)
                elif any(academic in domain for academic in ['arxiv', 'scholar', 'ieee', '.edu']):
                    academic_sources.append(title)
                elif any(company in domain for company in ['tesla', 'waymo', 'uber', 'ford']):
                    company_sources.append(title)
            
            if news_sources:
                print(f"  News sources: {len(news_sources)}")
            if academic_sources:
                print(f"  Academic sources: {len(academic_sources)}")
            if company_sources:
                print(f"  Company sources: {len(company_sources)}")


async def json_mode_with_search():
    """Demonstrate JSON mode with search-augmented data."""
    print("\n=== JSON Mode with Search Data ===")
    
    provider = PerplexityProvider()
    model = provider.language_model("sonar-pro")
    
    # Define JSON schema for market analysis
    schema = {
        "type": "object",
        "properties": {
            "market_overview": {
                "type": "string",
                "description": "Brief overview of the market situation"
            },
            "key_players": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of key companies or players"
            },
            "recent_developments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "event": {"type": "string"},
                        "impact": {"type": "string"},
                        "date": {"type": "string"}
                    }
                },
                "description": "Recent significant developments"
            },
            "market_size": {
                "type": "object",
                "properties": {
                    "current_value": {"type": "string"},
                    "projected_value": {"type": "string"},
                    "growth_rate": {"type": "string"}
                }
            },
            "sources_count": {
                "type": "integer",
                "description": "Number of sources used for this analysis"
            }
        },
        "required": ["market_overview", "key_players", "recent_developments"]
    }
    
    result = await generate_text(
        model=model,
        prompt="Analyze the current electric vehicle market, including key players, recent developments, and market size projections.",
        response_format={
            "type": "json",
            "schema": schema
        },
        max_output_tokens=600,
        temperature=0.1
    )
    
    print(f"JSON Response: {result.text}")
    
    try:
        parsed_json = json.loads(result.text)
        print(f"\nParsed Analysis:")
        print(f"Market Overview: {parsed_json.get('market_overview', 'N/A')[:200]}...")
        print(f"Key Players: {', '.join(parsed_json.get('key_players', []))}")
        print(f"Recent Developments: {len(parsed_json.get('recent_developments', []))} events")
        
        if 'market_size' in parsed_json:
            market_size = parsed_json['market_size']
            print(f"Market Size: {market_size.get('current_value')} → {market_size.get('projected_value')}")
        
    except json.JSONDecodeError:
        print("Failed to parse JSON response")


async def comparative_model_analysis():
    """Compare different Perplexity models on the same query."""
    print("\n=== Comparative Model Analysis ===")
    
    provider = PerplexityProvider()
    
    query = "Explain the concept of machine learning interpretability and why it matters."
    models = ["sonar", "sonar-pro", "sonar-reasoning"]
    
    for model_id in models:
        print(f"\n--- {model_id.upper()} ---")
        model = provider.language_model(model_id)
        
        result = await generate_text(
            model=model,
            prompt=query,
            max_output_tokens=200,
            temperature=0.3
        )
        
        print(f"Response: {result.text[:300]}...")
        
        if result.provider_metadata and "perplexity" in result.provider_metadata:
            perplexity_meta = result.provider_metadata["perplexity"]
            citations_count = len(perplexity_meta.get("citations", []))
            print(f"Citations: {citations_count}")
            print(f"Usage: {result.usage.total_tokens if result.usage else 'Unknown'} tokens")


async def error_handling_example():
    """Demonstrate error handling and best practices."""
    print("\n=== Error Handling ===")
    
    try:
        # Invalid API key example
        provider = create_perplexity_provider(api_key="invalid-key")
        model = provider.language_model("sonar-pro")
        
        result = await generate_text(
            model=model,
            prompt="This will fail",
            max_output_tokens=50
        )
        
    except Exception as e:
        print(f"Expected error with invalid API key: {type(e).__name__}: {e}")
    
    try:
        # Invalid search filter example
        provider = PerplexityProvider()
        search_options = provider.create_search_options(
            recency_filter="invalid_period"  # This should raise an error
        )
        
    except Exception as e:
        print(f"Expected error with invalid recency filter: {type(e).__name__}: {e}")


async def provider_info_example():
    """Show provider capabilities and model information."""
    print("\n=== Provider Information ===")
    
    provider = PerplexityProvider()
    
    # Get provider info
    provider_info = provider.get_provider_info()
    print(f"Provider: {provider_info['name']}")
    print(f"Description: {provider_info['description']}")
    print(f"Capabilities: {', '.join(provider_info['capabilities'])}")
    print(f"Search Features: {', '.join(provider_info['search_features'])}")
    
    # Get available models
    models = provider.get_available_models()
    
    print(f"\nAvailable Models:")
    for model_id, info in models["language_models"].items():
        print(f"  {model_id}:")
        print(f"    {info['description']}")
        print(f"    Context: {info.get('context_length', 'Unknown')} tokens")
        print(f"    Use Cases: {', '.join(info.get('use_cases', []))}")
        print(f"    Search: {', '.join(info.get('search_capabilities', []))}")


async def search_options_example():
    """Demonstrate various search configuration options."""
    print("\n=== Search Configuration Options ===")
    
    provider = PerplexityProvider()
    
    # Example 1: Academic research
    academic_options = provider.create_search_options(
        domain_filter=["arxiv.org", "scholar.google.com", "pubmed.ncbi.nlm.nih.gov"],
        return_citations=True,
        return_related_questions=True
    )
    print("Academic research options:")
    print(f"  Domain filter: {academic_options.get('search_domain_filter')}")
    print(f"  Citations: {academic_options.get('return_citations')}")
    print(f"  Related questions: {academic_options.get('return_related_questions')}")
    
    # Example 2: Recent news
    news_options = provider.create_search_options(
        domain_filter=["reuters.com", "bloomberg.com", "apnews.com"],
        recency_filter="hour",
        return_citations=True,
        return_related_questions=False
    )
    print("\nRecent news options:")
    print(f"  Domain filter: {news_options.get('search_domain_filter')}")
    print(f"  Recency filter: {news_options.get('search_recency_filter')}")
    print(f"  Citations: {news_options.get('return_citations')}")
    
    # Example 3: Financial analysis
    financial_options = provider.create_search_options(
        domain_filter=["sec.gov", "yahoo.com", "marketwatch.com", "fool.com"],
        recency_filter="week",
        return_citations=True,
        return_related_questions=True
    )
    print("\nFinancial analysis options:")
    print(f"  Domain filter: {financial_options.get('search_domain_filter')}")
    print(f"  Recency filter: {financial_options.get('search_recency_filter')}")


async def main():
    """Run all examples."""
    print("Perplexity Provider Examples for AI SDK Python")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("WARNING: PERPLEXITY_API_KEY not found. Some examples may fail.")
        print("Set your API key: export PERPLEXITY_API_KEY='your-api-key'")
        print()
    
    try:
        await basic_search_generation()
        await streaming_with_citations()
        await domain_filtered_search()
        await recency_filtered_news()
        await research_analysis_task()
        await json_mode_with_search()
        await comparative_model_analysis()
        await error_handling_example()
        await provider_info_example()
        await search_options_example()
        
        print("\n" + "=" * 60)
        print("All Perplexity examples completed successfully!")
        print("Key takeaways:")
        print("  • Perplexity excels at current information and research tasks")
        print("  • Citations provide transparency and source attribution")
        print("  • Search filtering enables targeted, relevant results")
        print("  • Different models offer varying levels of reasoning capability")
        print("  • JSON mode works well for structured research outputs")
        
    except Exception as e:
        print(f"\nExample failed: {type(e).__name__}: {e}")
        print("Check your API key and internet connection.")


if __name__ == "__main__":
    asyncio.run(main())