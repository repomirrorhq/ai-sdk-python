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


class MessageRole(str, Enum):
    """Message role in a conversation."""
    
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Usage(BaseModel):
    """Usage statistics for a model call."""
    
    prompt_tokens: int = Field(ge=0, description="Number of tokens in the prompt")
    completion_tokens: int = Field(ge=0, description="Number of tokens in the completion")
    total_tokens: int = Field(ge=0, description="Total number of tokens")
    reasoning_tokens: Optional[int] = Field(None, ge=0, description="Number of reasoning tokens used (for o1 models and similar)")
    cached_input_tokens: Optional[int] = Field(None, ge=0, description="Number of cached input tokens")


class ProviderMetadata(BaseModel):
    """Provider-specific metadata that can be included in responses."""
    
    data: Dict[str, Any] = Field(default_factory=dict)


class ProviderSettings(BaseModel):
    """Base settings for AI providers."""
    
    api_key: Optional[str] = Field(default=None, description="API key for the provider")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Additional HTTP headers")


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


class ReasoningContent(BaseModel):
    """Reasoning content extracted from text."""
    
    type: Literal["reasoning"] = "reasoning"
    text: str
    provider_metadata: Optional[ProviderMetadata] = None


# Union of all content types
Content = Union[TextContent, ImageContent, ToolCallContent, ToolResultContent, ReasoningContent]


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


class ReasoningStart(StreamPart):
    """Reasoning start in streaming response."""
    
    type: Literal["reasoning-start"] = "reasoning-start"
    id: str
    provider_metadata: Optional[ProviderMetadata] = None


class ReasoningDelta(StreamPart):
    """Reasoning delta in streaming response."""
    
    type: Literal["reasoning-delta"] = "reasoning-delta"
    id: str
    delta: str


class ReasoningEnd(StreamPart):
    """Reasoning end in streaming response."""
    
    type: Literal["reasoning-end"] = "reasoning-end"
    id: str


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


class TextStreamPart(BaseModel):
    """Text stream part (compatible with AI SDK)."""
    
    text_delta: Optional[str] = None
    type: str = "text-delta"
    
    def __init__(self, text_delta: Optional[str] = None, **kwargs):
        super().__init__(text_delta=text_delta, **kwargs)


class UsageStreamPart(BaseModel):
    """Usage stream part (compatible with AI SDK)."""
    
    usage: Usage
    type: str = "usage"
    
    def __init__(self, usage: Usage, **kwargs):
        super().__init__(usage=usage, **kwargs)


class FinishStreamPart(BaseModel):
    """Finish stream part (compatible with AI SDK)."""
    
    finish_reason: FinishReason
    usage: Usage
    type: str = "finish"
    
    def __init__(self, finish_reason: FinishReason, usage: Usage, **kwargs):
        super().__init__(finish_reason=finish_reason, usage=usage, **kwargs)


class EmbeddingResult(BaseModel):
    """Result from embedding generation."""
    
    embedding: List[float]
    usage: Usage
    provider_metadata: Optional[ProviderMetadata] = None
    
    def __init__(self, embedding: List[float], usage: Usage, **kwargs):
        super().__init__(embedding=embedding, usage=usage, **kwargs)


class GenerateTextResult(BaseModel):
    """Result from text generation."""
    
    text: str
    content: List[Content]
    finish_reason: FinishReason
    usage: Usage
    provider_metadata: Optional[ProviderMetadata] = None
    request_metadata: Optional[Dict[str, Any]] = None
    response_metadata: Optional[Dict[str, Any]] = None
    
    def __init__(
        self,
        text: str,
        content: List[Content],
        finish_reason: FinishReason,
        usage: Usage,
        **kwargs
    ):
        super().__init__(
            text=text,
            content=content,
            finish_reason=finish_reason,
            usage=usage,
            **kwargs
        )


class StreamTextResult:
    """Result from streaming text generation."""
    
    def __init__(self, stream):
        self.stream = stream
    
    def __aiter__(self):
        return self.stream.__aiter__()
    
    async def __anext__(self):
        return await self.stream.__anext__()


class ToolCall(BaseModel):
    """Tool call representation."""
    
    tool_call_id: str
    tool_name: str
    args: Dict[str, Any]
    
    def __init__(self, tool_call_id: str, tool_name: str, args: Dict[str, Any], **kwargs):
        super().__init__(tool_call_id=tool_call_id, tool_name=tool_name, args=args, **kwargs)


class ToolResult(BaseModel):
    """Tool execution result."""
    
    tool_call_id: str
    result: Any
    is_error: bool = False
    
    def __init__(self, tool_call_id: str, result: Any, is_error: bool = False, **kwargs):
        super().__init__(tool_call_id=tool_call_id, result=result, is_error=is_error, **kwargs)


class TranscriptionResult(BaseModel):
    """Result from transcription."""
    
    text: str
    segments: Optional[List[Any]] = None
    provider_metadata: Optional[ProviderMetadata] = None
    
    def __init__(self, text: str, **kwargs):
        super().__init__(text=text, **kwargs)