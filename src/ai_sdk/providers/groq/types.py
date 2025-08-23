"""
Type definitions for Groq provider
"""

from typing import Dict, Optional, Callable
from dataclasses import dataclass
from typing_extensions import Literal


# Model identifier types
GroqChatModelId = Literal[
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile", 
    "llama-3.1-405b-reasoning",
    "llama-3.2-1b-preview",
    "llama-3.2-3b-preview",
    "llama-3.2-11b-text-preview",
    "llama-3.2-90b-text-preview",
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it",
    "gemma2-9b-it",
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