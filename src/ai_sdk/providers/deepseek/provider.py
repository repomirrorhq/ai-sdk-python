"""
DeepSeek Provider implementation.
"""

from typing import Any, Dict
from ai_sdk.core.types import Provider, LanguageModel
from ai_sdk.errors.base import AISDKError
from .types import DeepSeekChatModelId, DeepSeekProviderSettings
from .language_model import DeepSeekLanguageModel


class DeepSeekProvider(Provider):
    """
    DeepSeek AI provider for advanced reasoning and text generation.
    
    Features:
    - OpenAI-compatible API with DeepSeek enhancements
    - Advanced reasoning capabilities (deepseek-reasoner)
    - Prompt caching with detailed hit/miss metrics
    - Tool calling support
    - Streaming responses
    - Cost-effective high-quality models
    """
    
    def __init__(self, settings: DeepSeekProviderSettings | None = None):
        """
        Initialize DeepSeek provider.
        
        Args:
            settings: Configuration settings for the provider.
                     If None, will use default settings with environment variables.
        """
        self.settings = settings or DeepSeekProviderSettings()
        self._provider_name = "deepseek"
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    def language_model(self, model_id: DeepSeekChatModelId) -> LanguageModel:
        """
        Create a DeepSeek language model for text generation.
        
        Args:
            model_id: The DeepSeek model identifier (e.g., "deepseek-chat", "deepseek-reasoner")
            
        Returns:
            DeepSeekLanguageModel instance
            
        Example:
            >>> provider = DeepSeekProvider()
            >>> model = provider.language_model("deepseek-reasoner")
            >>> result = await model.generate_text(prompt)
            >>> print(result.provider_metadata["deepseek"]["reasoning_content"])
        """
        return DeepSeekLanguageModel(model_id, self.settings)
    
    def chat(self, model_id: DeepSeekChatModelId) -> LanguageModel:
        """
        Alias for language_model() for consistency with DeepSeek API naming.
        
        Args:
            model_id: The DeepSeek model identifier
            
        Returns:
            DeepSeekLanguageModel instance
        """
        return self.language_model(model_id)
    
    def embedding_model(self, model_id: str):
        """
        DeepSeek does not currently provide embedding models.
        Use other providers like OpenAI, Cohere, or Google for embeddings.
        """
        raise AISDKError(f"DeepSeek does not support embedding models. Model '{model_id}' is not available.")
    
    def __call__(self, model_id: DeepSeekChatModelId) -> LanguageModel:
        """
        Convenient method to create a language model.
        
        Args:
            model_id: The DeepSeek language model identifier
            
        Returns:
            DeepSeekLanguageModel instance
        """
        return self.language_model(model_id)
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get information about available DeepSeek models."""
        return {
            "language_models": {
                "deepseek-chat": {
                    "description": "High-performance chat model optimized for conversations and general tasks",
                    "context_length": 32768,
                    "supports_streaming": True,
                    "supports_tools": True,
                    "supports_json_mode": True,
                    "supports_caching": True,
                    "pricing": "cost_effective",
                    "use_cases": [
                        "general_chat",
                        "content_generation", 
                        "question_answering",
                        "code_generation",
                        "analysis"
                    ],
                    "capabilities": [
                        "multilingual",
                        "tool_calling",
                        "prompt_caching",
                        "openai_compatible"
                    ]
                },
                "deepseek-reasoner": {
                    "description": "Advanced reasoning model with enhanced logical and analytical capabilities",
                    "context_length": 65536,
                    "supports_streaming": True,
                    "supports_tools": True,
                    "supports_json_mode": True,
                    "supports_caching": True,
                    "supports_reasoning": True,
                    "pricing": "premium_reasoning",
                    "use_cases": [
                        "complex_reasoning",
                        "mathematical_problems",
                        "logical_analysis",
                        "research_tasks",
                        "multi_step_planning",
                        "academic_writing"
                    ],
                    "capabilities": [
                        "advanced_reasoning",
                        "step_by_step_thinking",
                        "reasoning_transparency",
                        "complex_problem_solving",
                        "multilingual",
                        "tool_calling",
                        "prompt_caching"
                    ]
                }
            }
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": "deepseek",
            "description": "DeepSeek AI provider for advanced reasoning and cost-effective text generation",
            "capabilities": [
                "text_generation",
                "streaming",
                "tool_calling", 
                "json_mode",
                "advanced_reasoning",
                "prompt_caching",
                "openai_compatibility"
            ],
            "supported_modalities": {
                "input": ["text"],
                "output": ["text", "reasoning"]
            },
            "special_features": [
                "Advanced reasoning with deepseek-reasoner",
                "Cost-effective high-quality models",
                "Prompt caching with detailed metrics",
                "OpenAI API compatibility",
                "Reasoning transparency",
                "Multi-step logical thinking"
            ],
            "base_url": self.settings.base_url,
            "api_version": "v1",
            "pricing": "competitive"
        }
    
    def create_reasoning_options(
        self,
        enable_reasoning_output: bool = True,
        max_reasoning_tokens: int | None = None,
        reasoning_effort: str = "medium"
    ) -> dict:
        """
        Create options optimized for reasoning tasks with deepseek-reasoner.
        
        Args:
            enable_reasoning_output: Whether to include reasoning steps in output
            max_reasoning_tokens: Maximum tokens to use for reasoning (model-dependent)
            reasoning_effort: Reasoning effort level ("low", "medium", "high")
            
        Returns:
            Dictionary of options to pass as provider_options
            
        Example:
            >>> provider = DeepSeekProvider()
            >>> reasoning_opts = provider.create_reasoning_options(
            ...     enable_reasoning_output=True,
            ...     reasoning_effort="high"
            ... )
            >>> model = provider.language_model("deepseek-reasoner")
            >>> result = await generate_text(
            ...     model=model,
            ...     prompt="Solve this complex math problem step by step...",
            ...     provider_options=reasoning_opts
            ... )
        """
        options = {}
        
        if enable_reasoning_output:
            options["include_reasoning"] = True
        
        if max_reasoning_tokens is not None:
            options["max_reasoning_tokens"] = max_reasoning_tokens
            
        if reasoning_effort in ["low", "medium", "high"]:
            options["reasoning_effort"] = reasoning_effort
        else:
            raise AISDKError(f"Invalid reasoning effort: {reasoning_effort}. Must be one of: low, medium, high")
        
        return options
    
    def get_cache_metrics(self, result) -> Dict[str, Any] | None:
        """
        Extract prompt caching metrics from a generation result.
        
        Args:
            result: GenerateTextResult or FinishPart with provider metadata
            
        Returns:
            Dictionary with cache hit/miss information or None if not available
            
        Example:
            >>> result = await generate_text(model=model, prompt=prompt)
            >>> cache_info = provider.get_cache_metrics(result)
            >>> if cache_info:
            ...     print(f"Cache hits: {cache_info['hits']}, misses: {cache_info['misses']}")
        """
        if not result.provider_metadata or "deepseek" not in result.provider_metadata:
            return None
        
        deepseek_meta = result.provider_metadata["deepseek"]
        
        cache_info = {}
        
        if "prompt_cache_hit_tokens" in deepseek_meta:
            cache_info["hit_tokens"] = deepseek_meta["prompt_cache_hit_tokens"]
        if "prompt_cache_miss_tokens" in deepseek_meta:
            cache_info["miss_tokens"] = deepseek_meta["prompt_cache_miss_tokens"]
        
        # Calculate cache efficiency
        if "hit_tokens" in cache_info and "miss_tokens" in cache_info:
            total_tokens = cache_info["hit_tokens"] + cache_info["miss_tokens"]
            if total_tokens > 0:
                cache_info["hit_rate"] = cache_info["hit_tokens"] / total_tokens
                cache_info["efficiency"] = "high" if cache_info["hit_rate"] > 0.7 else "medium" if cache_info["hit_rate"] > 0.3 else "low"
        
        return cache_info if cache_info else None


def create_deepseek_provider(
    api_key: str | None = None,
    base_url: str | None = None,
    headers: Dict[str, str] | None = None,
) -> DeepSeekProvider:
    """
    Create a DeepSeek provider with custom settings.
    
    Args:
        api_key: DeepSeek API key. If None, uses DEEPSEEK_API_KEY environment variable.
        base_url: Custom base URL for API calls. Defaults to https://api.deepseek.com/v1
        headers: Additional headers to include in requests.
        
    Returns:
        DeepSeekProvider instance
        
    Example:
        >>> provider = create_deepseek_provider(api_key="your-api-key")
        >>> model = provider.language_model("deepseek-reasoner")
    """
    settings = DeepSeekProviderSettings()
    
    if api_key is not None:
        settings.api_key = api_key
    if base_url is not None:
        settings.base_url = base_url
    if headers is not None:
        settings.headers = headers
    
    return DeepSeekProvider(settings)


# Default provider instance
deepseek_provider = DeepSeekProvider()