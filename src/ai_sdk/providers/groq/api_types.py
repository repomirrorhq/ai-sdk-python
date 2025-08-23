"""
Groq API Types

Pydantic models for Groq API request and response structures.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field


class GroqMessage(BaseModel):
    """Groq chat message format."""
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class GroqTool(BaseModel):
    """Groq tool definition."""
    type: Literal["function"]
    function: Dict[str, Any]


class GroqChatCompletionRequest(BaseModel):
    """Groq chat completion request."""
    model: str
    messages: List[GroqMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    tools: Optional[List[GroqTool]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None
    seed: Optional[int] = None
    user: Optional[str] = None
    
    # Groq-specific parameters
    reasoning_format: Optional[Literal["parsed", "raw", "hidden"]] = None
    reasoning_effort: Optional[str] = None
    parallel_tool_calls: Optional[bool] = None
    structured_outputs: Optional[bool] = None
    service_tier: Optional[Literal["on_demand", "flex", "auto"]] = None


class GroqUsage(BaseModel):
    """Usage statistics from Groq API."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_time: Optional[float] = None
    completion_time: Optional[float] = None
    total_time: Optional[float] = None


class GroqChoice(BaseModel):
    """Choice from Groq completion response."""
    index: int
    message: GroqMessage
    finish_reason: Optional[str] = None
    logprobs: Optional[Dict[str, Any]] = None


class GroqChatCompletionResponse(BaseModel):
    """Groq chat completion response."""
    id: str
    object: Literal["chat.completion"]
    created: int
    model: str
    choices: List[GroqChoice]
    usage: Optional[GroqUsage] = None
    system_fingerprint: Optional[str] = None


class GroqStreamChoice(BaseModel):
    """Choice from Groq streaming response."""
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None
    logprobs: Optional[Dict[str, Any]] = None


class GroqChatCompletionStreamResponse(BaseModel):
    """Groq streaming chat completion response."""
    id: str
    object: Literal["chat.completion.chunk"]
    created: int
    model: str
    choices: List[GroqStreamChoice]
    usage: Optional[GroqUsage] = None
    system_fingerprint: Optional[str] = None


class GroqError(BaseModel):
    """Groq API error structure."""
    message: str
    type: str
    param: Optional[str] = None
    code: Optional[str] = None


class GroqErrorResponse(BaseModel):
    """Groq error response."""
    error: GroqError