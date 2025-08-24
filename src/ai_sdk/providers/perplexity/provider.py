"""
Perplexity Provider implementation.
"""

from typing import Any, Dict
from ai_sdk.core.types import Provider, LanguageModel
from ai_sdk.errors.base import AISDKError
from .types import PerplexityLanguageModelId, PerplexityProviderSettings
from .language_model import PerplexityLanguageModel


class PerplexityProvider(Provider):
    """
    Perplexity AI provider for search-augmented text generation.
    
    Features:
    - Real-time search capabilities
    - Web citations and source attribution
    - Current information access
    - Domain and recency filtering
    - Related question suggestions
    - High-quality reasoning models
    """
    
    def __init__(self, settings: PerplexityProviderSettings | None = None):
        """
        Initialize Perplexity provider.
        
        Args:
            settings: Configuration settings for the provider.
                     If None, will use default settings with environment variables.
        """
        self.settings = settings or PerplexityProviderSettings()
        self._provider_name = "perplexity"
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return self._provider_name
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    def language_model(self, model_id: PerplexityLanguageModelId) -> LanguageModel:
        """
        Create a Perplexity language model for search-augmented text generation.
        
        Args:
            model_id: The Perplexity model identifier (e.g., "sonar-pro", "sonar-reasoning")
            
        Returns:
            PerplexityLanguageModel instance
            
        Example:
            >>> provider = PerplexityProvider()
            >>> model = provider.language_model("sonar-pro")
            >>> result = await model.generate_text(prompt)
            >>> print(result.provider_metadata["perplexity"]["citations"])
        """
        return PerplexityLanguageModel(model_id, self.settings)
    
    def embedding_model(self, model_id: str):
        """
        Perplexity does not provide embedding models.
        Use other providers like OpenAI, Cohere, or Google for embeddings.
        """
        raise AISDKError(f"Perplexity does not support embedding models. Model '{model_id}' is not available.")
    
    def __call__(self, model_id: PerplexityLanguageModelId) -> LanguageModel:
        """
        Convenient method to create a language model.
        
        Args:
            model_id: The Perplexity language model identifier
            
        Returns:
            PerplexityLanguageModel instance
        """
        return self.language_model(model_id)
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get information about available Perplexity models."""
        return {
            "language_models": {
                "sonar-deep-research": {
                    "description": "Advanced research model with comprehensive analysis capabilities",
                    "context_length": 127072,
                    "supports_streaming": True,
                    "supports_search": True,
                    "supports_citations": True,
                    "use_cases": ["research", "analysis", "comprehensive_answers"],
                    "search_capabilities": ["deep_research", "multi_source", "academic"]
                },
                "sonar-reasoning-pro": {
                    "description": "Pro reasoning model with enhanced logical capabilities",
                    "context_length": 127072,
                    "supports_streaming": True,
                    "supports_search": True,
                    "supports_citations": True,
                    "use_cases": ["complex_reasoning", "problem_solving", "analysis"],
                    "search_capabilities": ["reasoning", "logic", "problem_solving"]
                },
                "sonar-reasoning": {
                    "description": "Standard reasoning model with search integration",
                    "context_length": 127072,
                    "supports_streaming": True,
                    "supports_search": True,
                    "supports_citations": True,
                    "use_cases": ["reasoning", "explanations", "logical_tasks"],
                    "search_capabilities": ["basic_reasoning", "explanatory"]
                },
                "sonar-pro": {
                    "description": "Pro model with real-time search and advanced capabilities",
                    "context_length": 127072,
                    "supports_streaming": True,
                    "supports_search": True,
                    "supports_citations": True,
                    "use_cases": ["general_purpose", "current_events", "research"],
                    "search_capabilities": ["real_time", "comprehensive", "multi_domain"]
                },
                "sonar": {
                    "description": "Standard model with real-time search capabilities",
                    "context_length": 127072,
                    "supports_streaming": True,
                    "supports_search": True,
                    "supports_citations": True,
                    "use_cases": ["general_questions", "current_information", "basic_research"],
                    "search_capabilities": ["real_time", "web_search", "current_events"]
                }
            }
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": "perplexity",
            "description": "Perplexity AI provider for search-augmented text generation with real-time information",
            "capabilities": [
                "text_generation",
                "streaming",
                "real_time_search",
                "web_citations",
                "current_information",
                "domain_filtering",
                "recency_filtering",
                "related_questions",
                "json_mode"
            ],
            "supported_modalities": {
                "input": ["text"],
                "output": ["text", "citations", "search_results"]
            },
            "search_features": [
                "Real-time web search",
                "Academic and news sources",
                "Citation tracking", 
                "Domain filtering",
                "Recency filtering",
                "Related question suggestions",
                "Source attribution"
            ],
            "base_url": self.settings.base_url,
            "api_version": "v1"
        }
    
    def create_search_options(
        self,
        domain_filter: list[str] | None = None,
        recency_filter: str | None = None,
        return_related_questions: bool = False,
        return_citations: bool = True
    ) -> dict:
        """
        Create search options for Perplexity models.
        
        Args:
            domain_filter: List of domains to limit search to (e.g., ["wikipedia.org", "arxiv.org"])
            recency_filter: Time period for search results ("month", "week", "day", "hour")  
            return_related_questions: Whether to return related questions
            return_citations: Whether to return source citations
            
        Returns:
            Dictionary of search options to pass as provider_options
            
        Example:
            >>> provider = PerplexityProvider()
            >>> search_opts = provider.create_search_options(
            ...     domain_filter=["wikipedia.org", "arxiv.org"],
            ...     recency_filter="week",
            ...     return_related_questions=True
            ... )
            >>> model = provider.language_model("sonar-pro")
            >>> result = await generate_text(
            ...     model=model,
            ...     prompt="What's new in AI research?",
            ...     provider_options=search_opts
            ... )
        """
        options = {}
        
        if domain_filter is not None:
            options["search_domain_filter"] = domain_filter
        
        if recency_filter is not None:
            if recency_filter not in ["month", "week", "day", "hour"]:
                raise AISDKError(f"Invalid recency filter: {recency_filter}. Must be one of: month, week, day, hour")
            options["search_recency_filter"] = recency_filter
        
        options["return_related_questions"] = return_related_questions
        options["return_citations"] = return_citations
        
        return options


def create_perplexity_provider(
    api_key: str | None = None,
    base_url: str | None = None,
    headers: Dict[str, str] | None = None,
) -> PerplexityProvider:
    """
    Create a Perplexity provider with custom settings.
    
    Args:
        api_key: Perplexity API key. If None, uses PERPLEXITY_API_KEY environment variable.
        base_url: Custom base URL for API calls. Defaults to https://api.perplexity.ai
        headers: Additional headers to include in requests.
        
    Returns:
        PerplexityProvider instance
        
    Example:
        >>> provider = create_perplexity_provider(api_key="your-api-key")
        >>> model = provider.language_model("sonar-pro")
    """
    settings = PerplexityProviderSettings()
    
    if api_key is not None:
        settings.api_key = api_key
    if base_url is not None:
        settings.base_url = base_url
    if headers is not None:
        settings.headers = headers
    
    return PerplexityProvider(settings)


# Default provider instance
perplexity_provider = PerplexityProvider()