"""
Perplexity provider types and model definitions.
"""

from typing import Literal, Union, List, Dict, Any, Optional
from pydantic import BaseModel

# Perplexity Model IDs based on https://docs.perplexity.ai/models/model-cards
PerplexityLanguageModelId = Union[
    Literal[
        "sonar-deep-research",    # Deep research with comprehensive analysis
        "sonar-reasoning-pro",    # Advanced reasoning with search
        "sonar-reasoning",        # Standard reasoning with search  
        "sonar-pro",             # Pro model with real-time search
        "sonar",                 # Standard model with real-time search
    ],
    str,  # Allow custom model IDs
]


class PerplexityProviderSettings(BaseModel):
    """Configuration settings for Perplexity provider."""
    
    base_url: str = "https://api.perplexity.ai"
    """Base URL for Perplexity API calls. Defaults to https://api.perplexity.ai"""
    
    api_key: str | None = None
    """API key for Perplexity. If not provided, will try PERPLEXITY_API_KEY environment variable."""
    
    headers: Dict[str, str] | None = None
    """Additional headers to include in requests."""


class PerplexityFinishReason:
    """Perplexity-specific finish reasons."""
    STOP = "stop"
    LENGTH = "length"
    ERROR = "error"
    CANCELLED = "cancelled"


class PerplexityResponseFormat(BaseModel):
    """Perplexity response format configuration."""
    type: Literal["text", "json"]


class PerplexityMessage(BaseModel):
    """Perplexity message format."""
    role: Literal["system", "user", "assistant"]
    content: str


class PerplexityToolCall(BaseModel):
    """Perplexity tool call (search functionality)."""
    type: str
    function: Dict[str, Any]


class PerplexityChatRequest(BaseModel):
    """Perplexity chat API request format."""
    model: str
    messages: List[PerplexityMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stream: bool = False
    response_format: Optional[PerplexityResponseFormat] = None
    
    # Perplexity-specific search parameters
    return_citations: bool = True
    return_related_questions: bool = False
    search_domain_filter: Optional[List[str]] = None
    search_recency_filter: Optional[Literal["month", "week", "day", "hour"]] = None


class PerplexityCitation(BaseModel):
    """Perplexity citation information."""
    text: str
    url: str | None = None
    title: str | None = None 
    domain: str | None = None
    publish_date: str | None = None
    snippet: str | None = None


class PerplexityUsage(BaseModel):
    """Perplexity usage statistics."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class PerplexityStreamDelta(BaseModel):
    """Perplexity streaming response delta."""
    role: Optional[str] = None
    content: Optional[str] = None


class PerplexityStreamChoice(BaseModel):
    """Perplexity streaming response choice."""
    index: int
    delta: PerplexityStreamDelta
    finish_reason: Optional[str] = None


class PerplexityStreamEvent(BaseModel):
    """Perplexity streaming event."""
    id: str
    object: str
    created: int
    model: str
    choices: List[PerplexityStreamChoice]


class PerplexityChoice(BaseModel):
    """Perplexity response choice."""
    index: int
    message: PerplexityMessage
    finish_reason: str


class PerplexityChatResponse(BaseModel):
    """Perplexity chat response format."""
    id: str
    object: str
    created: int
    model: str
    choices: List[PerplexityChoice]
    usage: PerplexityUsage
    
    # Perplexity-specific search results
    citations: Optional[List[PerplexityCitation]] = None
    related_questions: Optional[List[str]] = None