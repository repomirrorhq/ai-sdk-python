"""
Cerebras Provider implementation.
"""

from typing import Any, Dict
from ai_sdk.core.types import Provider, LanguageModel
from ai_sdk.errors.base import AISDKError
from .types import CerebrasChatModelId, CerebrasProviderSettings
from .language_model import CerebrasLanguageModel


class CerebrasProvider(Provider):
    """
    Cerebras AI provider for ultra-fast inference.
    
    Features:
    - Ultra-fast inference with Cerebras Wafer-Scale Engine
    - Optimized Llama models (3.1-8B, 3.1-70B, 3.3-70B)
    - OpenAI-compatible API with 10x+ speed improvements
    - Streaming support for real-time responses
    - Tool calling capabilities
    - JSON mode support
    - Competitive pricing with speed focus
    """
    
    def __init__(self, settings: CerebrasProviderSettings | None = None):
        """
        Initialize Cerebras provider.
        
        Args:
            settings: Configuration settings for the provider.
                     If None, will use default settings with environment variables.
        """
        self.settings = settings or CerebrasProviderSettings()
        self._provider_name = "cerebras"
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return self._provider_name
    
    def language_model(self, model_id: CerebrasChatModelId) -> LanguageModel:
        """
        Create a Cerebras language model for ultra-fast text generation.
        
        Args:
            model_id: The Cerebras model identifier (e.g., "llama3.1-8b", "llama3.1-70b")
            
        Returns:
            CerebrasLanguageModel instance
            
        Example:
            >>> provider = CerebrasProvider()
            >>> model = provider.language_model("llama3.1-8b")
            >>> result = await model.generate_text(prompt)
            >>> print(f"Ultra-fast response in {result.timing['total_time']}ms")
        """
        return CerebrasLanguageModel(model_id, self.settings)
    
    def chat(self, model_id: CerebrasChatModelId) -> LanguageModel:
        """
        Alias for language_model() for consistency with OpenAI-style APIs.
        
        Args:
            model_id: The Cerebras chat model identifier
            
        Returns:
            CerebrasLanguageModel instance
        """
        return self.language_model(model_id)
    
    def embedding_model(self, model_id: str):
        """
        Cerebras does not currently provide embedding models.
        Use other providers like OpenAI, Cohere, or Google for embeddings.
        """
        raise AISDKError(f"Cerebras does not support embedding models. Model '{model_id}' is not available. Use providers like OpenAI, Cohere, or Google for embeddings.")
    
    def __call__(self, model_id: CerebrasChatModelId) -> LanguageModel:
        """
        Convenient method to create a language model.
        
        Args:
            model_id: The Cerebras language model identifier
            
        Returns:
            CerebrasLanguageModel instance
        """
        return self.language_model(model_id)
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get information about available Cerebras models."""
        return {
            "language_models": {
                "llama3.1-8b": {
                    "description": "Llama 3.1 8B optimized for ultra-fast inference on Cerebras hardware",
                    "context_length": 128000,
                    "supports_streaming": True,
                    "supports_tools": True,
                    "supports_json_mode": True,
                    "speed": "ultra_fast",
                    "parameters": "8B",
                    "inference_speed": "~10x faster than traditional GPUs",
                    "use_cases": [
                        "real_time_chat",
                        "content_generation", 
                        "quick_responses",
                        "interactive_applications",
                        "rapid_prototyping"
                    ],
                    "pricing": "cost_effective",
                    "hardware_optimization": "cerebras_wse"
                },
                "llama3.1-70b": {
                    "description": "Llama 3.1 70B optimized for high-performance inference on Cerebras hardware",
                    "context_length": 128000,
                    "supports_streaming": True,
                    "supports_tools": True,
                    "supports_json_mode": True,
                    "speed": "very_fast",
                    "parameters": "70B",
                    "inference_speed": "~5x faster than traditional GPUs", 
                    "use_cases": [
                        "complex_reasoning",
                        "advanced_chat",
                        "content_creation",
                        "analytical_tasks",
                        "code_generation",
                        "research_assistance"
                    ],
                    "pricing": "premium_fast",
                    "hardware_optimization": "cerebras_wse"
                },
                "llama-3.3-70b": {
                    "description": "Latest Llama 3.3 70B model optimized for Cerebras ultra-fast inference",
                    "context_length": 128000,
                    "supports_streaming": True,
                    "supports_tools": True,
                    "supports_json_mode": True,
                    "speed": "very_fast",
                    "parameters": "70B",
                    "inference_speed": "~5x faster than traditional GPUs",
                    "use_cases": [
                        "latest_capabilities",
                        "complex_reasoning",
                        "advanced_applications", 
                        "research_tasks",
                        "sophisticated_analysis",
                        "cutting_edge_features"
                    ],
                    "pricing": "premium_latest",
                    "hardware_optimization": "cerebras_wse",
                    "model_version": "latest"
                }
            }
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": "cerebras",
            "description": "Cerebras AI provider for ultra-fast inference using specialized Wafer-Scale Engine hardware",
            "capabilities": [
                "text_generation",
                "streaming",
                "tool_calling",
                "json_mode",
                "ultra_fast_inference",
                "openai_compatibility"
            ],
            "supported_modalities": {
                "input": ["text"],
                "output": ["text"]
            },
            "special_features": [
                "Cerebras Wafer-Scale Engine hardware",
                "10x+ faster inference than traditional GPUs", 
                "Optimized Llama model variants",
                "Ultra-low latency responses",
                "Cost-effective high-speed inference",
                "OpenAI-compatible API"
            ],
            "hardware": {
                "type": "Cerebras Wafer-Scale Engine", 
                "advantage": "Massive parallel processing",
                "speed_improvement": "5-10x faster inference",
                "memory": "Unified on-chip memory"
            },
            "base_url": self.settings.base_url,
            "api_version": "v1",
            "pricing": "competitive_fast"
        }
    
    def create_speed_optimized_options(
        self,
        prioritize_latency: bool = True,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> dict:
        """
        Create options optimized for Cerebras' ultra-fast inference.
        
        Args:
            prioritize_latency: Whether to prioritize low latency over other factors
            max_tokens: Maximum tokens for faster responses (lower = faster)
            temperature: Sampling temperature (lower = more deterministic and faster)
            
        Returns:
            Dictionary of options to pass as provider_options
            
        Example:
            >>> provider = CerebrasProvider()
            >>> speed_opts = provider.create_speed_optimized_options(
            ...     prioritize_latency=True,
            ...     max_tokens=512,
            ...     temperature=0.5
            ... )
            >>> model = provider.language_model("llama3.1-8b") 
            >>> result = await generate_text(
            ...     model=model,
            ...     prompt="Quick response needed:",
            ...     provider_options=speed_opts
            ... )
        """
        options = {
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if prioritize_latency:
            # Settings optimized for minimum latency on Cerebras hardware
            options.update({
                "top_p": 0.9,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "stream": True  # Streaming typically reduces perceived latency
            })
        
        return options
    
    def get_speed_comparison(self, model_id: str) -> Dict[str, str]:
        """
        Get speed comparison information for a Cerebras model.
        
        Args:
            model_id: The model identifier
            
        Returns:
            Dictionary with speed comparison data
        """
        speed_data = {
            "llama3.1-8b": {
                "cerebras_speed": "~100ms average response time",
                "traditional_gpu_speed": "~1000ms average response time", 
                "speedup": "~10x faster",
                "hardware_advantage": "Cerebras WSE parallel processing"
            },
            "llama3.1-70b": {
                "cerebras_speed": "~200ms average response time",
                "traditional_gpu_speed": "~1000ms average response time",
                "speedup": "~5x faster", 
                "hardware_advantage": "Cerebras WSE unified memory"
            },
            "llama-3.3-70b": {
                "cerebras_speed": "~250ms average response time",
                "traditional_gpu_speed": "~1250ms average response time",
                "speedup": "~5x faster",
                "hardware_advantage": "Latest WSE optimization"
            }
        }
        
        return speed_data.get(model_id, {
            "speedup": "~5x faster",
            "hardware_advantage": "Cerebras WSE acceleration"
        })


def create_cerebras_provider(
    api_key: str | None = None,
    base_url: str | None = None,
    headers: Dict[str, str] | None = None,
) -> CerebrasProvider:
    """
    Create a Cerebras provider with custom settings.
    
    Args:
        api_key: Cerebras API key. If None, uses CEREBRAS_API_KEY environment variable.
        base_url: Custom base URL for API calls. Defaults to https://api.cerebras.ai/v1
        headers: Additional headers to include in requests.
        
    Returns:
        CerebrasProvider instance
        
    Example:
        >>> provider = create_cerebras_provider(api_key="your-api-key")
        >>> model = provider.language_model("llama3.1-8b")
        >>> # Experience 10x+ faster inference compared to traditional GPUs
    """
    settings = CerebrasProviderSettings()
    
    if api_key is not None:
        settings.api_key = api_key
    if base_url is not None:
        settings.base_url = base_url
    if headers is not None:
        settings.headers = headers
    
    return CerebrasProvider(settings)


# Default provider instance
cerebras_provider = CerebrasProvider()