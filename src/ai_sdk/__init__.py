"""AI SDK for Python - The AI Toolkit for Python.

This is a Python port of the AI SDK, providing a unified interface for working
with various AI providers including OpenAI, Anthropic, Google, Azure OpenAI, and many more.

Key features:
- Text generation with `generate_text()` and `stream_text()`
- Structured object generation with `generate_object()` and `stream_object()`
- Tool calling and function calling support
- Embeddings with `embed()` and `embed_many()`
- Multiple AI provider support
- Async/await native support
- Type safety with Pydantic models
"""

__version__ = "0.2.0"

# Core functionality
from .core.generate_text import generate_text, stream_text
from .core.generate_text_enhanced import generate_text_enhanced, EnhancedGenerateTextResult
from .core.step import StepResult, GeneratedFile, StopCondition, step_count_is, has_tool_call, PrepareStepFunction, PrepareStepResult, PrepareStepArgs
from .core.generate_object import generate_object, stream_object, GenerateObjectResult, StreamObjectResult
from .core.generate_object_enhanced import generate_object_enhanced, EnhancedGenerateObjectResult
from .core.object_repair import TextRepairFunction, create_default_repair_function, create_custom_repair_function
from .core.generate_image import generate_image, generate_image_sync, GenerateImageResult, NoImageGeneratedError
from .core.generate_speech import generate_speech, generate_speech_sync, GenerateSpeechResult, NoSpeechGeneratedError
from .core.transcribe import transcribe, transcribe_sync, TranscriptionResult, NoTranscriptGeneratedError
from .core.embed import embed, embed_many, EmbedResult, EmbedManyResult, EmbeddingUsage, cosine_similarity
from .core.reasoning import (
    extract_reasoning_text, add_usage, has_reasoning_tokens, 
    get_reasoning_token_ratio, ReasoningExtractor
)

# Tools
from .tools import Tool, ToolCall, ToolResult, tool, simple_tool, ToolRegistry
from .tools import MCPClient, MCPClientConfig, create_mcp_client, StdioMCPTransport, StdioConfig, SSEMCPTransport, SSEConfig

# Schema validation system
from .schemas import (
    BaseSchema, ValidationResult, SchemaValidationError,
    PydanticSchema, pydantic_schema,
    JSONSchemaValidator, jsonschema_schema,
    MarshmallowSchema, marshmallow_schema,
    CerberusSchema, cerberus_schema
)

# Agent system
from .agent import Agent, AgentSettings

# Registry system
from .registry import create_provider_registry, ProviderRegistry, custom_provider

# Middleware
from .middleware import (
    wrap_language_model,
    LanguageModelMiddleware, 
    logging_middleware,
    caching_middleware,
    default_settings_middleware,
    telemetry_middleware,
    extract_reasoning_middleware,
    simulate_streaming_middleware,
)

# Streaming utilities
from .streaming import smooth_stream, ChunkDetector

# Framework Adapters
from .adapters import langchain_adapter, llamaindex_adapter
from .adapters.langchain import to_ui_message_stream as langchain_to_ui_stream
from .adapters.llamaindex import to_ui_message_stream as llamaindex_to_ui_stream

# UI Message Streaming
from .ui import (
    UIMessage, UIMessagePart, TextUIPart, ReasoningUIPart, ToolUIPart, DynamicToolUIPart,
    SourceUrlUIPart, SourceDocumentUIPart, FileUIPart, DataUIPart, StepStartUIPart,
    UITools, UITool, UIDataTypes, is_tool_ui_part, get_tool_name,
    UIMessageStream, UIMessageStreamWriter, UIMessageChunk, UIMessageStreamOnFinishCallback,
    create_ui_message_stream, create_ui_message_stream_response, pipe_ui_message_stream_to_response,
    read_ui_message_stream, JsonToSseTransformStream, UI_MESSAGE_STREAM_HEADERS
)

# Framework Integrations
from .integrations import (
    fastapi_ai_middleware, AIFastAPI, streaming_chat_endpoint, websocket_chat_endpoint,
    AIFlask, ai_blueprint, streaming_response_wrapper
)

# Testing utilities (for development and testing)
from .testing import (
    MockProvider,
    MockLanguageModel,
    MockEmbeddingModel,
    MockImageModel,
    MockSpeechModel, 
    MockTranscriptionModel,
    simulate_readable_stream,
    create_test_messages,
    assert_generation_result,
    ResponseBuilder,
)

# Provider interfaces
from .providers.base import Provider, LanguageModel, EmbeddingModel, ImageModel, SpeechModel, TranscriptionModel
from .providers.types import Message, Content, FinishReason

# Providers
from .providers.openai import create_openai
from .providers.anthropic import create_anthropic
from .providers.google import create_google
from .providers.google_vertex import create_vertex
from .providers.azure import create_azure
from .providers.groq import create_groq
from .providers.togetherai import create_together
from .providers.bedrock import create_bedrock
from .providers.mistral import create_mistral
from .providers.cohere import create_cohere_provider as create_cohere
from .providers.xai import XAIProvider as create_xai
from .providers.perplexity import create_perplexity_provider as create_perplexity
from .providers.deepseek import create_deepseek_provider as create_deepseek
from .providers.cerebras import create_cerebras_provider as create_cerebras
from .providers.fireworks import create_fireworks_provider as create_fireworks
from .providers.replicate import create_replicate_provider as create_replicate
from .providers.elevenlabs import create_elevenlabs
from .providers.deepgram import create_deepgram
from .providers.assemblyai import create_assemblyai
from .providers.fal import create_fal
from .providers.hume import create_hume
from .providers.lmnt import create_lmnt
from .providers.revai import create_revai
from .providers.deepinfra import create_deepinfra_provider as create_deepinfra
from .providers.gateway import create_gateway_provider as create_gateway
from .providers.gladia import create_gladia_provider as create_gladia
from .providers.luma import create_luma_provider as create_luma
from .providers.openai_compatible import create_openai_compatible
from .providers.vercel import create_vercel_provider as create_vercel

# Errors
from .errors import AISDKError, APIError, InvalidArgumentError

# For now, export implemented functionality
__all__ = [
    "__version__",
    # Core functions
    "generate_text",
    "stream_text",
    "generate_text_enhanced",
    "EnhancedGenerateTextResult",
    "StepResult",
    "GeneratedFile", 
    "StopCondition",
    "step_count_is",
    "has_tool_call",
    "PrepareStepFunction",
    "PrepareStepResult", 
    "PrepareStepArgs",
    "generate_object", 
    "stream_object",
    "GenerateObjectResult",
    "StreamObjectResult",
    "generate_object_enhanced",
    "EnhancedGenerateObjectResult",
    "TextRepairFunction",
    "create_default_repair_function",
    "create_custom_repair_function",
    "generate_image",
    "generate_image_sync",
    "GenerateImageResult",
    "NoImageGeneratedError",
    "generate_speech",
    "generate_speech_sync",
    "GenerateSpeechResult",
    "NoSpeechGeneratedError",
    "transcribe",
    "transcribe_sync",
    "TranscriptionResult", 
    "NoTranscriptGeneratedError",
    "embed",
    "embed_many",
    "EmbedResult",
    "EmbedManyResult", 
    "EmbeddingUsage",
    "cosine_similarity",
    # Tools
    "Tool",
    "ToolCall", 
    "ToolResult",
    "tool",
    "simple_tool",
    "ToolRegistry",
    # MCP (Model Context Protocol)
    "MCPClient",
    "MCPClientConfig",
    "create_mcp_client",
    "StdioMCPTransport",
    "StdioConfig",
    "SSEMCPTransport",
    "SSEConfig",
    # Schema validation system
    "BaseSchema",
    "ValidationResult", 
    "SchemaValidationError",
    "PydanticSchema",
    "pydantic_schema",
    "JSONSchemaValidator",
    "jsonschema_schema", 
    "MarshmallowSchema",
    "marshmallow_schema",
    "CerberusSchema",
    "cerberus_schema",
    # Agent system
    "Agent",
    "AgentSettings",
    # Registry system
    "create_provider_registry",
    "ProviderRegistry",
    "custom_provider",
    # Middleware
    "wrap_language_model",
    "LanguageModelMiddleware",
    "logging_middleware", 
    "caching_middleware",
    "default_settings_middleware",
    "telemetry_middleware",
    "extract_reasoning_middleware",
    "simulate_streaming_middleware",
    # Streaming utilities
    "smooth_stream",
    "ChunkDetector",
    # Framework Adapters
    "langchain_adapter",
    "llamaindex_adapter", 
    "langchain_to_ui_stream",
    "llamaindex_to_ui_stream",
    # UI Message Streaming
    "UIMessage", "UIMessagePart", "TextUIPart", "ReasoningUIPart", "ToolUIPart", "DynamicToolUIPart",
    "SourceUrlUIPart", "SourceDocumentUIPart", "FileUIPart", "DataUIPart", "StepStartUIPart",
    "UITools", "UITool", "UIDataTypes", "is_tool_ui_part", "get_tool_name",
    "UIMessageStream", "UIMessageStreamWriter", "UIMessageChunk", "UIMessageStreamOnFinishCallback",
    "create_ui_message_stream", "create_ui_message_stream_response", "pipe_ui_message_stream_to_response",
    "read_ui_message_stream", "JsonToSseTransformStream", "UI_MESSAGE_STREAM_HEADERS",
    # Framework Integrations
    "fastapi_ai_middleware",
    "AIFastAPI",
    "streaming_chat_endpoint",
    "websocket_chat_endpoint",
    "AIFlask",
    "ai_blueprint",
    "streaming_response_wrapper",
    # Testing utilities
    "MockProvider",
    "MockLanguageModel",
    "MockEmbeddingModel", 
    "MockImageModel",
    "MockSpeechModel",
    "MockTranscriptionModel",
    "simulate_readable_stream",
    "create_test_messages",
    "assert_generation_result",
    "ResponseBuilder",
    # Provider interfaces  
    "Provider",
    "LanguageModel", 
    "EmbeddingModel",
    "ImageModel",
    "SpeechModel",
    "TranscriptionModel",
    "Message",
    "Content",
    "FinishReason",
    # Providers
    "create_openai",
    "create_anthropic",
    "create_google",
    "create_vertex",
    "create_azure",
    "create_groq",
    "create_together",
    "create_bedrock",
    "create_mistral",
    "create_cohere",
    "create_xai",
    "create_perplexity",
    "create_deepseek",
    "create_cerebras",
    "create_fireworks",
    "create_replicate",
    "create_elevenlabs",
    "create_deepgram",
    "create_assemblyai",
    "create_fal",
    "create_hume",
    "create_lmnt",
    "create_revai",
    "create_deepinfra",
    "create_gateway",
    "create_gladia",
    "create_luma",
    "create_openai_compatible",
    "create_vercel",
    # Errors
    "AISDKError",
    "APIError", 
    "InvalidArgumentError",
]