"""Type definitions for xAI provider."""

from enum import Enum
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


class XAIChatModelId(str, Enum):
    """xAI chat model identifiers."""
    
    # Grok 4 models
    GROK_4 = "grok-4"
    GROK_4_0709 = "grok-4-0709"
    GROK_4_LATEST = "grok-4-latest"
    
    # Grok 3 models
    GROK_3 = "grok-3"
    GROK_3_LATEST = "grok-3-latest"
    GROK_3_FAST = "grok-3-fast"
    GROK_3_FAST_LATEST = "grok-3-fast-latest"
    
    # Grok 3 Mini models
    GROK_3_MINI = "grok-3-mini"
    GROK_3_MINI_LATEST = "grok-3-mini-latest"
    GROK_3_MINI_FAST = "grok-3-mini-fast"
    GROK_3_MINI_FAST_LATEST = "grok-3-mini-fast-latest"
    
    # Grok 2 Vision models
    GROK_2_VISION_1212 = "grok-2-vision-1212"
    GROK_2_VISION = "grok-2-vision"
    GROK_2_VISION_LATEST = "grok-2-vision-latest"
    
    # Grok 2 Image models
    GROK_2_IMAGE_1212 = "grok-2-image-1212"
    GROK_2_IMAGE = "grok-2-image"
    GROK_2_IMAGE_LATEST = "grok-2-image-latest"
    
    # Grok 2 models
    GROK_2_1212 = "grok-2-1212"
    GROK_2 = "grok-2"
    GROK_2_LATEST = "grok-2-latest"
    
    # Beta models
    GROK_VISION_BETA = "grok-vision-beta"
    GROK_BETA = "grok-beta"


class XAIImageModelId(str, Enum):
    """xAI image model identifiers."""
    
    GROK_2_IMAGE = "grok-2-image"
    GROK_2_IMAGE_1212 = "grok-2-image-1212"
    GROK_2_IMAGE_LATEST = "grok-2-image-latest"


class SearchMode(str, Enum):
    """Search mode for xAI search parameters."""
    
    OFF = "off"      # Disables search completely
    AUTO = "auto"    # Model decides whether to search (default)
    ON = "on"        # Always enables search


class ReasoningEffort(str, Enum):
    """Reasoning effort levels for reasoning models."""
    
    LOW = "low"
    HIGH = "high"


class WebSource(BaseModel):
    """Web search source configuration."""
    
    type: Literal["web"] = "web"
    country: Optional[str] = Field(None, min_length=2, max_length=2, description="2-letter country code")
    excluded_websites: Optional[List[str]] = Field(None, max_items=5, description="Up to 5 websites to exclude")
    allowed_websites: Optional[List[str]] = Field(None, max_items=5, description="Up to 5 websites to allow")
    safe_search: Optional[bool] = None


class XSource(BaseModel):
    """X (Twitter) search source configuration."""
    
    type: Literal["x"] = "x"
    x_handles: Optional[List[str]] = None


class NewsSource(BaseModel):
    """News search source configuration."""
    
    type: Literal["news"] = "news"
    country: Optional[str] = Field(None, min_length=2, max_length=2, description="2-letter country code")
    excluded_websites: Optional[List[str]] = Field(None, max_items=5, description="Up to 5 websites to exclude")
    safe_search: Optional[bool] = None


class RSSSource(BaseModel):
    """RSS search source configuration."""
    
    type: Literal["rss"] = "rss"
    links: List[str] = Field(max_items=1, description="Currently only supports one RSS link")


SearchSource = Union[WebSource, XSource, NewsSource, RSSSource]


class SearchParameters(BaseModel):
    """Search parameters for xAI models."""
    
    mode: SearchMode = SearchMode.AUTO
    return_citations: Optional[bool] = Field(True, description="Whether to return citations in the response")
    from_date: Optional[str] = Field(None, description="Start date for search data (YYYY-MM-DD)")
    to_date: Optional[str] = Field(None, description="End date for search data (YYYY-MM-DD)")
    max_search_results: Optional[int] = Field(20, ge=1, le=50, description="Maximum number of search results")
    sources: Optional[List[SearchSource]] = Field(None, description="Data sources to search from")


class XAIProviderOptions(BaseModel):
    """Provider-specific options for xAI."""
    
    reasoning_effort: Optional[ReasoningEffort] = Field(
        None, 
        description="Reasoning effort for reasoning models (grok-3-mini and grok-3-mini-fast only)"
    )
    search_parameters: Optional[SearchParameters] = None


# API Response Types
class XAIUsage(BaseModel):
    """Token usage information from xAI API."""
    
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    completion_tokens_details: Optional[dict] = None


class XAIToolCall(BaseModel):
    """Tool call from xAI API."""
    
    id: str
    type: Literal["function"] = "function"
    function: dict


class XAIMessage(BaseModel):
    """Message from xAI API."""
    
    role: Literal["assistant"] = "assistant"
    content: Optional[str] = None
    reasoning_content: Optional[str] = None
    tool_calls: Optional[List[XAIToolCall]] = None


class XAIChoice(BaseModel):
    """Choice from xAI API response."""
    
    message: XAIMessage
    index: int
    finish_reason: Optional[str] = None


class XAIChatResponse(BaseModel):
    """Complete response from xAI chat completion API."""
    
    id: Optional[str] = None
    created: Optional[int] = None
    model: Optional[str] = None
    choices: List[XAIChoice]
    object: Literal["chat.completion"] = "chat.completion"
    usage: XAIUsage
    citations: Optional[List[str]] = None


class XAIDelta(BaseModel):
    """Delta for streaming responses."""
    
    role: Optional[Literal["assistant"]] = None
    content: Optional[str] = None
    reasoning_content: Optional[str] = None
    tool_calls: Optional[List[XAIToolCall]] = None


class XAIStreamChoice(BaseModel):
    """Streaming choice from xAI API."""
    
    delta: XAIDelta
    finish_reason: Optional[str] = None
    index: int


class XAIStreamChunk(BaseModel):
    """Streaming chunk from xAI API."""
    
    id: Optional[str] = None
    created: Optional[int] = None
    model: Optional[str] = None
    choices: List[XAIStreamChoice]
    usage: Optional[XAIUsage] = None
    citations: Optional[List[str]] = None


class XAIError(BaseModel):
    """xAI API error structure."""
    
    error: dict