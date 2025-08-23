"""
Type definitions for Anthropic API.

This module contains Pydantic models for Anthropic API request/response structures.
"""

from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel


class AnthropicMessage(BaseModel):
    """Anthropic message format."""
    role: Literal["user", "assistant"]
    content: Union[str, List[Dict[str, Any]]]


class AnthropicUsage(BaseModel):
    """Token usage information from Anthropic."""
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: Optional[int] = None
    cache_read_input_tokens: Optional[int] = None


class AnthropicContentBlock(BaseModel):
    """Anthropic content block."""
    type: str
    text: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    input: Optional[Dict[str, Any]] = None


class AnthropicResponse(BaseModel):
    """Anthropic API response."""
    id: Optional[str] = None
    type: str = "message"
    role: str = "assistant"
    content: List[AnthropicContentBlock]
    model: Optional[str] = None
    stop_reason: Optional[str] = None
    stop_sequence: Optional[str] = None
    usage: AnthropicUsage


class AnthropicStreamChunk(BaseModel):
    """Anthropic streaming chunk."""
    type: str
    message: Optional[Dict[str, Any]] = None
    index: Optional[int] = None
    content_block: Optional[Dict[str, Any]] = None
    delta: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, Any]] = None


class AnthropicPrompt(BaseModel):
    """Converted prompt for Anthropic API."""
    system: Optional[str] = None
    messages: List[AnthropicMessage]