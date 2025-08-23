"""UI Message types for AI SDK Python.

This module defines the message types used for UI-focused streaming
and communication between frontend and backend components.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union, TypeVar, Generic
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod

from ..providers.types import ProviderMetadata
from ..tools import Tool

# Type variables
T = TypeVar('T')
METADATA = TypeVar('METADATA')
DATA_PARTS = TypeVar('DATA_PARTS', bound='UIDataTypes')
TOOLS = TypeVar('TOOLS', bound='UITools')

# Type aliases
UIDataTypes = Dict[str, Any]

class UITool(BaseModel):
    """Tool definition for UI messages."""
    input: Any
    output: Optional[Any] = None

UITools = Dict[str, UITool]

class TextUIPart(BaseModel):
    """Text part of a UI message."""
    type: Literal["text"] = "text"
    text: str
    state: Optional[Literal["streaming", "done"]] = None
    provider_metadata: Optional[ProviderMetadata] = Field(None, alias="providerMetadata")

    class Config:
        allow_population_by_field_name = True

class ReasoningUIPart(BaseModel):
    """Reasoning part of a UI message."""
    type: Literal["reasoning"] = "reasoning"
    text: str
    state: Optional[Literal["streaming", "done"]] = None
    provider_metadata: Optional[ProviderMetadata] = Field(None, alias="providerMetadata")

    class Config:
        allow_population_by_field_name = True

class SourceUrlUIPart(BaseModel):
    """Source URL part of a UI message."""
    type: Literal["source-url"] = "source-url"
    source_id: str = Field(alias="sourceId")
    url: str
    title: Optional[str] = None
    provider_metadata: Optional[ProviderMetadata] = Field(None, alias="providerMetadata")

    class Config:
        allow_population_by_field_name = True

class SourceDocumentUIPart(BaseModel):
    """Source document part of a UI message."""
    type: Literal["source-document"] = "source-document"
    source_id: str = Field(alias="sourceId")
    media_type: str = Field(alias="mediaType")
    title: str
    filename: Optional[str] = None
    provider_metadata: Optional[ProviderMetadata] = Field(None, alias="providerMetadata")

    class Config:
        allow_population_by_field_name = True

class FileUIPart(BaseModel):
    """File part of a UI message."""
    type: Literal["file"] = "file"
    media_type: str = Field(alias="mediaType", description="IANA media type of the file")
    filename: Optional[str] = None
    url: str = Field(description="URL of the file or Data URL")
    provider_metadata: Optional[ProviderMetadata] = Field(None, alias="providerMetadata")

    class Config:
        allow_population_by_field_name = True

class StepStartUIPart(BaseModel):
    """Step boundary part of a UI message."""
    type: Literal["step-start"] = "step-start"

class DataUIPart(BaseModel):
    """Data part of a UI message."""
    type: str  # Will be like 'data-{NAME}'
    id: Optional[str] = None
    data: Any

class ToolUIPart(BaseModel):
    """Tool invocation part of a UI message."""
    type: str  # Will be like 'tool-{NAME}'
    tool_call_id: str = Field(alias="toolCallId")
    
    # State-dependent fields
    state: Literal["input-streaming", "input-available", "output-available", "output-error"]
    input: Optional[Any] = None
    output: Optional[Any] = None
    error_text: Optional[str] = Field(None, alias="errorText")
    provider_executed: Optional[bool] = Field(None, alias="providerExecuted")
    call_provider_metadata: Optional[ProviderMetadata] = Field(None, alias="callProviderMetadata")
    preliminary: Optional[bool] = None
    raw_input: Optional[Any] = Field(None, alias="rawInput")

    class Config:
        allow_population_by_field_name = True

class DynamicToolUIPart(BaseModel):
    """Dynamic tool invocation part of a UI message."""
    type: Literal["dynamic-tool"] = "dynamic-tool"
    tool_name: str = Field(alias="toolName")
    tool_call_id: str = Field(alias="toolCallId")
    
    # State-dependent fields  
    state: Literal["input-streaming", "input-available", "output-available", "output-error"]
    input: Optional[Any] = None
    output: Optional[Any] = None
    error_text: Optional[str] = Field(None, alias="errorText")
    call_provider_metadata: Optional[ProviderMetadata] = Field(None, alias="callProviderMetadata")
    preliminary: Optional[bool] = None

    class Config:
        allow_population_by_field_name = True

# Union of all UI message parts
UIMessagePart = Union[
    TextUIPart,
    ReasoningUIPart, 
    ToolUIPart,
    DynamicToolUIPart,
    SourceUrlUIPart,
    SourceDocumentUIPart,
    FileUIPart,
    DataUIPart,
    StepStartUIPart,
]

class UIMessage(BaseModel, Generic[METADATA, DATA_PARTS, TOOLS]):
    """AI SDK UI Message.
    
    Used in the client and to communicate between frontend and API routes.
    """
    id: str = Field(description="Unique identifier for the message")
    role: Literal["system", "user", "assistant"] = Field(description="Role of the message")
    metadata: Optional[METADATA] = Field(None, description="Message metadata")
    parts: List[UIMessagePart] = Field(description="Parts of the message for rendering")

    class Config:
        arbitrary_types_allowed = True

def is_tool_ui_part(part: UIMessagePart) -> bool:
    """Check if a UI part is a tool part."""
    return part.type.startswith('tool-')

def get_tool_name(part: ToolUIPart) -> str:
    """Extract tool name from a tool UI part."""
    return '-'.join(part.type.split('-')[1:])