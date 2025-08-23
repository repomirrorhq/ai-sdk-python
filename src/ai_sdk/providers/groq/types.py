"""
Type definitions for Groq provider
"""

from typing import Dict, Optional, Callable
from dataclasses import dataclass
from typing_extensions import Literal
from pydantic import BaseModel


# Model identifier types based on https://console.groq.com/docs/models
GroqChatModelId = Literal[
    # Production models
    "gemma2-9b-it",
    "llama-3.1-8b-instant", 
    "llama-3.3-70b-versatile",
    "meta-llama/llama-guard-4-12b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    # Preview models (selection)
    "deepseek-r1-distill-llama-70b",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "meta-llama/llama-4-scout-17b-16e-instruct", 
    "meta-llama/llama-prompt-guard-2-22m",
    "meta-llama/llama-prompt-guard-2-86m",
    "mistral-saba-24b",
    "moonshotai/kimi-k2-instruct",
    "qwen/qwen3-32b",
    "llama-guard-3-8b",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "qwen-qwq-32b",
    "qwen-2.5-32b",
    "deepseek-r1-distill-qwen-32b",
    # Legacy models for backward compatibility
    "llama-3.1-70b-versatile", 
    "llama-3.1-405b-reasoning",
    "llama-3.2-1b-preview",
    "llama-3.2-3b-preview", 
    "llama-3.2-11b-text-preview",
    "llama-3.2-90b-text-preview",
    "gemma-7b-it",
]

GroqTranscriptionModelId = Literal[
    "whisper-large-v3",
    "whisper-large-v3-turbo",
]


@dataclass
class GroqConfig:
    """Configuration for Groq models"""
    
    provider: str
    api_key: Optional[str]
    base_url: str
    max_retries: int
    timeout: float
    extra_headers: Optional[Dict[str, str]]


class GroqProviderOptions(BaseModel):
    """Provider-specific options for Groq language models."""
    
    # Reasoning options (for supported models)
    reasoning_format: Optional[Literal["parsed", "raw", "hidden"]] = None
    reasoning_effort: Optional[str] = None
    
    # Advanced options
    parallel_tool_calls: Optional[bool] = None
    structured_outputs: Optional[bool] = None
    user: Optional[str] = None
    
    # Service tier for request prioritization
    service_tier: Optional[Literal["on_demand", "flex", "auto"]] = None