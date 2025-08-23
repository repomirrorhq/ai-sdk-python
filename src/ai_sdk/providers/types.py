"""Core types for AI SDK providers."""

from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class FinishReason(str, Enum):
    """Reason why the model stopped generating."""
    
    STOP = "stop"
    LENGTH = "length"
    CONTENT_FILTER = "content-filter"
    TOOL_CALLS = "tool-calls"
    ERROR = "error"
    OTHER = "other"
    UNKNOWN = "unknown"


class Usage(BaseModel):
    """Usage statistics for a model call."""
    
    prompt_tokens: int = Field(ge=0, description="Number of tokens in the prompt")
    completion_tokens: int = Field(ge=0, description="Number of tokens in the completion")
    total_tokens: int = Field(ge=0, description="Total number of tokens")


class ProviderMetadata(BaseModel):
    """Provider-specific metadata that can be included in responses."""
    
    data: Dict[str, Any] = Field(default_factory=dict)


class TextContent(BaseModel):
    """Text content in a message."""
    
    type: Literal["text"] = "text"
    text: str


class ImageContent(BaseModel):
    """Image content in a message."""
    
    type: Literal["image"] = "image"
    image: Union[str, bytes]  # URL or base64 encoded image data
    mime_type: Optional[str] = None


class ToolCallContent(BaseModel):
    """Tool call content in a message."""
    
    type: Literal["tool-call"] = "tool-call"
    tool_call_id: str
    tool_name: str
    args: Dict[str, Any]


class ToolResultContent(BaseModel):
    """Tool result content in a message."""
    
    type: Literal["tool-result"] = "tool-result"
    tool_call_id: str
    result: Any
    is_error: bool = False


# Union of all content types
Content = Union[TextContent, ImageContent, ToolCallContent, ToolResultContent]


class Message(BaseModel):
    """A message in a conversation."""
    
    role: Literal["system", "user", "assistant", "tool"]
    content: Union[str, List[Content]]
    name: Optional[str] = None
    tool_call_id: Optional[str] = None


class ToolDefinition(BaseModel):
    """Definition of a tool that can be called by the model."""
    
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON schema for parameters
    

class GenerateOptions(BaseModel):
    """Options for generating text."""
    
    messages: List[Message]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[Union[str, List[str]]] = None
    seed: Optional[int] = None
    tools: Optional[List[ToolDefinition]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    headers: Optional[Dict[str, str]] = None
    extra_body: Optional[Dict[str, Any]] = None


class StreamOptions(GenerateOptions):
    """Options for streaming text generation."""
    pass


class GenerateResult(BaseModel):
    """Result from text generation."""
    
    content: List[Content]
    finish_reason: FinishReason
    usage: Usage
    provider_metadata: Optional[ProviderMetadata] = None
    request_metadata: Optional[Dict[str, Any]] = None
    response_metadata: Optional[Dict[str, Any]] = None


class StreamPart(BaseModel):
    """A part of a streaming response."""
    
    type: str
    

class TextDelta(StreamPart):
    """Text delta in streaming response."""
    
    type: Literal["text-delta"] = "text-delta"
    text_delta: str


class ToolCallDelta(StreamPart):
    """Tool call delta in streaming response."""
    
    type: Literal["tool-call-delta"] = "tool-call-delta"
    tool_call_id: str
    tool_name: Optional[str] = None
    args_delta: Optional[str] = None


class FinishPart(StreamPart):
    """Finish part in streaming response."""
    
    type: Literal["finish"] = "finish"
    finish_reason: FinishReason
    usage: Usage
    provider_metadata: Optional[ProviderMetadata] = None


class StreamResult(BaseModel):
    """Result from streaming text generation."""
    
    # This will be implemented as an async iterator
    pass