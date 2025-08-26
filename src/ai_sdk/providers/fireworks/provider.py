"""
Fireworks Provider implementation.
"""

from typing import Any, Dict
from ai_sdk.core.types import Provider, LanguageModel, EmbeddingModel
from ai_sdk.errors.base import AISDKError
from .types import (
    FireworksChatModelId, 
    FireworksEmbeddingModelId, 
    FireworksProviderSettings,
    is_embedding_model,
    is_vision_model,
    FIREWORKS_MODEL_INFO
)
from .language_model import FireworksLanguageModel
from .embedding_model import FireworksEmbeddingModel


class FireworksProvider(Provider):
    """
    Fireworks AI provider for high-performance model hosting.
    
    Features:
    - High-performance optimized inference infrastructure
    - Wide variety of open-source models (Llama, Mixtral, Qwen, DeepSeek)
    - Chat models with tool calling and JSON mode support
    - Embedding models for semantic search and similarity
    - Multimodal models for vision tasks
    - Competitive pricing with fast response times
    - Enterprise-grade reliability and scaling
    """
    
    def __init__(self, settings: FireworksProviderSettings | None = None):
        """
        Initialize Fireworks provider.
        
        Args:
            settings: Configuration settings for the provider.
                     If None, will use default settings with environment variables.
        """
        self.settings = settings or FireworksProviderSettings()
        self._provider_name = "fireworks"
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return self._provider_name
    
    def language_model(self, model_id: FireworksChatModelId) -> LanguageModel:
        """
        Create a Fireworks language model for text generation.
        
        Args:
            model_id: The Fireworks model identifier (e.g., "accounts/fireworks/models/llama-v3p3-70b-instruct")
            
        Returns:
            FireworksLanguageModel instance
            
        Example:
            >>> provider = FireworksProvider()
            >>> model = provider.language_model("accounts/fireworks/models/llama-v3p3-70b-instruct")
            >>> result = await model.generate_text(prompt)
            >>> print(f"Generated with {result.provider_metadata['fireworks']['model']}")
        """
        if is_embedding_model(model_id):
            raise AISDKError(f"Model '{model_id}' is an embedding model. Use embedding_model() method instead.")
        
        return FireworksLanguageModel(model_id, self.settings)
    
    def chat_model(self, model_id: FireworksChatModelId) -> LanguageModel:
        """
        Alias for language_model() for consistency with OpenAI-style APIs.
        
        Args:
            model_id: The Fireworks chat model identifier
            
        Returns:
            FireworksLanguageModel instance
        """
        return self.language_model(model_id)
    
    def embedding_model(self, model_id: FireworksEmbeddingModelId) -> EmbeddingModel:
        """
        Create a Fireworks embedding model for text embeddings.
        
        Args:
            model_id: The Fireworks embedding model identifier (e.g., "nomic-ai/nomic-embed-text-v1.5")
            
        Returns:
            FireworksEmbeddingModel instance
            
        Example:
            >>> provider = FireworksProvider()
            >>> model = provider.embedding_model("nomic-ai/nomic-embed-text-v1.5")
            >>> result = await model.embed(["Hello world", "How are you?"])
        """
        return FireworksEmbeddingModel(model_id, self.settings)
    
    def __call__(self, model_id: FireworksChatModelId) -> LanguageModel:
        """
        Convenient method to create a language model.
        
        Args:
            model_id: The Fireworks language model identifier
            
        Returns:
            FireworksLanguageModel instance
        """
        return self.language_model(model_id)
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get information about available Fireworks models."""
        
        # Separate models by type
        chat_models = {}
        embedding_models = {}
        
        for model_id, info in FIREWORKS_MODEL_INFO.items():
            model_type = info.get("model_type", "chat")
            
            if model_type == "embedding":
                embedding_models[model_id] = {
                    **info,
                    "provider_optimization": "fireworks_optimized",
                    "inference_speed": "fast",
                    "pricing": "competitive"
                }
            else:
                chat_models[model_id] = {
                    **info,
                    "provider_optimization": "fireworks_optimized", 
                    "inference_speed": "fast",
                    "pricing": "competitive"
                }
        
        return {
            "language_models": chat_models,
            "embedding_models": embedding_models,
            "total_models": len(FIREWORKS_MODEL_INFO),
            "model_categories": {
                "frontier_models": [
                    "accounts/fireworks/models/llama-v3p1-405b-instruct",
                    "accounts/fireworks/models/deepseek-v3"
                ],
                "efficient_models": [
                    "accounts/fireworks/models/llama-v3p2-3b-instruct",
                    "accounts/fireworks/models/mixtral-8x7b-instruct"
                ],
                "coding_models": [
                    "accounts/fireworks/models/qwen2p5-coder-32b-instruct"
                ],
                "vision_models": [
                    "accounts/fireworks/models/qwen2-vl-72b-instruct",
                    "accounts/fireworks/models/llama-v3p2-11b-vision-instruct"
                ],
                "embedding_models": [
                    "nomic-ai/nomic-embed-text-v1.5"
                ]
            }
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": "fireworks",
            "description": "Fireworks AI provider for high-performance model hosting with optimized inference",
            "capabilities": [
                "text_generation",
                "streaming",
                "tool_calling",
                "json_mode",
                "text_embeddings",
                "multimodal_vision",
                "high_performance_inference",
                "openai_compatibility"
            ],
            "supported_modalities": {
                "input": ["text", "images"],
                "output": ["text", "embeddings"]
            },
            "special_features": [
                "High-performance optimized inference",
                "Wide variety of open-source models",
                "Enterprise-grade reliability and scaling",
                "Competitive pricing with fast response times",
                "Multimodal vision capabilities",
                "Advanced coding and reasoning models",
                "OpenAI-compatible API"
            ],
            "model_families": [
                "Llama (3.1, 3.2, 3.3)", 
                "Mixtral (8x7B, 8x22B)",
                "Qwen (2.5, VL)",
                "DeepSeek (V3)",
                "Yi Large",
                "Nomic Embeddings"
            ],
            "infrastructure": {
                "optimization": "High-performance GPU clusters",
                "scaling": "Auto-scaling infrastructure", 
                "reliability": "Enterprise-grade uptime",
                "global": "Multi-region deployment"
            },
            "base_url": self.settings.base_url,
            "api_version": "v1",
            "pricing": "competitive"
        }
    
    def get_model_recommendations(self, use_case: str) -> Dict[str, Any]:
        """
        Get model recommendations based on use case.
        
        Args:
            use_case: The intended use case (e.g., "general_chat", "coding", "analysis", "embeddings")
            
        Returns:
            Dictionary with recommended models and reasoning
            
        Example:
            >>> provider = FireworksProvider()
            >>> recommendations = provider.get_model_recommendations("coding")
            >>> print(recommendations["primary_recommendation"])
        """
        
        recommendations = {
            "general_chat": {
                "primary": "accounts/fireworks/models/llama-v3p3-70b-instruct",
                "alternatives": [
                    "accounts/fireworks/models/mixtral-8x7b-instruct",
                    "accounts/fireworks/models/llama-v3p2-3b-instruct"
                ],
                "reasoning": "Llama 3.3 70B provides excellent general purpose capabilities with good performance"
            },
            "coding": {
                "primary": "accounts/fireworks/models/qwen2p5-coder-32b-instruct", 
                "alternatives": [
                    "accounts/fireworks/models/deepseek-v3",
                    "accounts/fireworks/models/llama-v3p3-70b-instruct"
                ],
                "reasoning": "Qwen 2.5 Coder is specifically optimized for programming tasks"
            },
            "analysis": {
                "primary": "accounts/fireworks/models/deepseek-v3",
                "alternatives": [
                    "accounts/fireworks/models/llama-v3p1-405b-instruct",
                    "accounts/fireworks/models/llama-v3p3-70b-instruct"
                ],
                "reasoning": "DeepSeek V3 excels at complex reasoning and analytical tasks"
            },
            "cost_effective": {
                "primary": "accounts/fireworks/models/llama-v3p2-3b-instruct",
                "alternatives": [
                    "accounts/fireworks/models/mixtral-8x7b-instruct"
                ],
                "reasoning": "Llama 3.2 3B provides good performance at lower cost"
            },
            "frontier_capabilities": {
                "primary": "accounts/fireworks/models/llama-v3p1-405b-instruct",
                "alternatives": [
                    "accounts/fireworks/models/deepseek-v3"
                ],
                "reasoning": "Llama 3.1 405B is the largest model with frontier capabilities"
            },
            "vision": {
                "primary": "accounts/fireworks/models/qwen2-vl-72b-instruct",
                "alternatives": [
                    "accounts/fireworks/models/llama-v3p2-11b-vision-instruct"
                ],
                "reasoning": "Qwen 2 VL 72B provides excellent vision-language understanding"
            },
            "embeddings": {
                "primary": "nomic-ai/nomic-embed-text-v1.5",
                "alternatives": [],
                "reasoning": "High-quality text embeddings optimized for search and similarity"
            }
        }
        
        return recommendations.get(use_case.lower(), {
            "primary": "accounts/fireworks/models/llama-v3p3-70b-instruct",
            "alternatives": [
                "accounts/fireworks/models/mixtral-8x7b-instruct"
            ],
            "reasoning": "Default recommendation for general use cases"
        })
    
    def create_performance_options(
        self,
        optimize_for: str = "balanced",  # "speed", "quality", "cost", "balanced"
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> dict:
        """
        Create options optimized for different performance characteristics.
        
        Args:
            optimize_for: Optimization target ("speed", "quality", "cost", "balanced")
            max_tokens: Maximum tokens for response length
            temperature: Sampling temperature
            
        Returns:
            Dictionary of options to pass as provider_options
            
        Example:
            >>> provider = FireworksProvider()
            >>> speed_opts = provider.create_performance_options(
            ...     optimize_for="speed",
            ...     max_tokens=512
            ... )
            >>> model = provider.language_model("accounts/fireworks/models/llama-v3p2-3b-instruct")
            >>> result = await generate_text(
            ...     model=model,
            ...     prompt="Quick response needed:",
            ...     provider_options=speed_opts
            ... )
        """
        
        base_options = {
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if optimize_for == "speed":
            base_options.update({
                "top_p": 0.9,
                "frequency_penalty": 0,
                "presence_penalty": 0
            })
        elif optimize_for == "quality":
            base_options.update({
                "top_p": 0.95,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            })
        elif optimize_for == "cost":
            base_options.update({
                "max_tokens": min(max_tokens, 512),  # Limit tokens for cost
                "top_p": 0.9
            })
        else:  # balanced
            base_options.update({
                "top_p": 0.95,
                "frequency_penalty": 0.05,
                "presence_penalty": 0.05
            })
        
        return base_options


def create_fireworks_provider(
    api_key: str | None = None,
    base_url: str | None = None,
    headers: Dict[str, str] | None = None,
) -> FireworksProvider:
    """
    Create a Fireworks provider with custom settings.
    
    Args:
        api_key: Fireworks API key. If None, uses FIREWORKS_API_KEY environment variable.
        base_url: Custom base URL for API calls. Defaults to https://api.fireworks.ai/inference/v1
        headers: Additional headers to include in requests.
        
    Returns:
        FireworksProvider instance
        
    Example:
        >>> provider = create_fireworks_provider(api_key="your-api-key")
        >>> model = provider.language_model("accounts/fireworks/models/llama-v3p3-70b-instruct")
        >>> # Access to high-performance inference with wide model selection
    """
    settings = FireworksProviderSettings()
    
    if api_key is not None:
        settings.api_key = api_key
    if base_url is not None:
        settings.base_url = base_url
    if headers is not None:
        settings.headers = headers
    
    return FireworksProvider(settings)


# Default provider instance
fireworks_provider = FireworksProvider()