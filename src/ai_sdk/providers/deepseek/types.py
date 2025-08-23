"""
DeepSeek provider types and model definitions.
"""

from typing import Literal, Union, Dict, Any, Optional
from pydantic import BaseModel

# DeepSeek Model IDs based on https://api-docs.deepseek.com/quick_start/pricing  
DeepSeekChatModelId = Union[
    Literal[
        "deepseek-chat",           # Standard chat model
        "deepseek-reasoner",       # Advanced reasoning model
        "deepseek-v3",            # DeepSeek V3 model
        "deepseek-v3.1",          # DeepSeek V3.1 model  
        "deepseek-v3.1-base",     # DeepSeek V3.1 base model
        "deepseek-v3.1-thinking", # DeepSeek V3.1 thinking model
        "deepseek-r1",            # DeepSeek R1 reasoning model
        "deepseek-r1-distill-llama-70b", # DeepSeek R1 distilled model
    ],
    str,  # Allow custom model IDs
]


class DeepSeekProviderSettings(BaseModel):
    """Configuration settings for DeepSeek provider."""
    
    base_url: str = "https://api.deepseek.com/v1"
    """Base URL for DeepSeek API calls. Defaults to https://api.deepseek.com/v1"""
    
    api_key: str | None = None
    """API key for DeepSeek. If not provided, will try DEEPSEEK_API_KEY environment variable."""
    
    headers: Dict[str, str] | None = None
    """Additional headers to include in requests."""


class DeepSeekUsage(BaseModel):
    """DeepSeek-specific usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    # DeepSeek-specific cache metrics
    prompt_cache_hit_tokens: Optional[int] = None
    prompt_cache_miss_tokens: Optional[int] = None


class DeepSeekChoice(BaseModel):
    """DeepSeek response choice."""
    index: int
    message: Dict[str, Any]
    finish_reason: Optional[str] = None


class DeepSeekResponse(BaseModel):
    """DeepSeek API response format."""
    id: str
    object: str
    created: int
    model: str
    choices: list[DeepSeekChoice]
    usage: DeepSeekUsage


class DeepSeekStreamChoice(BaseModel):
    """DeepSeek streaming response choice."""
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class DeepSeekStreamChunk(BaseModel):
    """DeepSeek streaming response chunk."""
    id: str
    object: str
    created: int
    model: str
    choices: list[DeepSeekStreamChoice]
    usage: Optional[DeepSeekUsage] = None


class DeepSeekFinishReason:
    """DeepSeek-specific finish reasons."""
    STOP = "stop"
    LENGTH = "length"
    TOOL_CALLS = "tool_calls"
    CONTENT_FILTER = "content_filter"


# DeepSeek-specific metadata keys
class DeepSeekMetadataKeys:
    """Keys for DeepSeek-specific metadata."""
    PROMPT_CACHE_HIT_TOKENS = "prompt_cache_hit_tokens"
    PROMPT_CACHE_MISS_TOKENS = "prompt_cache_miss_tokens"
    REASONING_CONTENT = "reasoning_content"
    THINKING_TOKENS = "thinking_tokens"