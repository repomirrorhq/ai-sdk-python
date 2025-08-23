"""
Type definitions for OpenAI-Compatible provider
"""

from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass
from typing_extensions import Literal


@dataclass
class OpenAICompatibleProviderSettings:
    """Settings for OpenAI-Compatible provider"""
    
    # Base URL for the OpenAI-compatible API
    base_url: str
    
    # Provider name for identification
    name: str
    
    # API key for authentication (if required)
    api_key: Optional[str] = None
    
    # Custom headers to include in requests
    headers: Optional[Dict[str, str]] = None
    
    # Custom query parameters for requests
    query_params: Optional[Dict[str, str]] = None
    
    # Custom fetch/HTTP client function
    fetch: Optional[Callable] = None
    
    # Include usage information in streaming responses
    include_usage: bool = False


# Model identifier types
OpenAICompatibleChatModelId = str
OpenAICompatibleCompletionModelId = str 
OpenAICompatibleEmbeddingModelId = str
OpenAICompatibleImageModelId = str


@dataclass
class OpenAICompatibleConfig:
    """Configuration passed to OpenAI-Compatible models"""
    
    provider: str
    base_url: str
    headers: Callable[[], Dict[str, str]]
    fetch: Optional[Callable] = None
    include_usage: bool = False