"""
Groq AI provider implementation

This module provides integration with Groq's high-speed inference platform,
supporting various open-source models with extremely fast generation speeds.

Key features:
- Ultra-fast inference with LPU (Language Processing Unit) technology
- Support for popular open-source models (LLaMA, Mixtral, Gemma, etc.)
- Real-time streaming capabilities
- Function calling support
- Audio transcription with Whisper models
- Latest models including Llama 4, DeepSeek R1, Qwen 3, and more

Example usage:
    ```python
    from ai_sdk import create_groq
    from ai_sdk.core import generate_text
    
    # Create provider
    groq = create_groq(api_key="your-api-key")
    
    # Use with generate_text
    result = await generate_text(
        model=groq("llama-3.1-8b-instant"),
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(result.content)
    ```
"""

from .provider import GroqProvider, create_groq, groq
from .language_model import GroqChatLanguageModel
from .transcription_model import GroqTranscriptionModel
from .types import GroqChatModelId, GroqTranscriptionModelId
from .api_types import (
    GroqChatCompletionRequest,
    GroqChatCompletionResponse,
    GroqMessage,
    GroqTool,
    GroqUsage,
)
from .message_converter import convert_to_groq_messages, convert_from_groq_response

__all__ = [
    "GroqProvider",
    "create_groq",
    "groq",
    "GroqChatLanguageModel", 
    "GroqTranscriptionModel",
    "GroqChatModelId",
    "GroqTranscriptionModelId",
    "GroqChatCompletionRequest",
    "GroqChatCompletionResponse", 
    "GroqMessage",
    "GroqTool",
    "GroqUsage",
    "convert_to_groq_messages",
    "convert_from_groq_response",
]