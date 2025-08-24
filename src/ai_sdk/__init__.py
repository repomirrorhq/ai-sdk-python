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

# Static imports that don't cause circular dependencies
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
from .registry import ProviderRegistry, register_provider, get_provider

# Middleware system
from .middleware import (
    LanguageModelMiddleware, 
    default_settings_middleware, 
    extract_reasoning_middleware, 
    simulate_streaming_middleware,
    wrap_language_model
)

# Testing utilities
from .testing import (
    MockLanguageModel, MockProvider, MockStreamPart,
    create_mock_response, create_stream_response, create_test_messages
)

# Provider types (safe imports - no circular dependencies)
from .providers.types import Usage, Message, FinishReason

# Core functionality - lazy imports to avoid circular dependencies
def __getattr__(name: str):
    """Lazy import of core functions to avoid circular dependencies."""
    if name == 'generate_text':
        from .core.generate_text import generate_text
        return generate_text
    elif name == 'stream_text':
        from .core.generate_text import stream_text
        return stream_text
    elif name == 'generate_object':
        from .core.generate_object import generate_object
        return generate_object
    elif name == 'stream_object':
        from .core.generate_object import stream_object
        return stream_object
    elif name == 'Provider':
        from .providers.base import Provider
        return Provider
    elif name == 'LanguageModel':
        from .providers.base import LanguageModel  
        return LanguageModel
    elif name == 'EmbeddingModel':
        from .providers.base import EmbeddingModel
        return EmbeddingModel
    elif name == 'ImageModel':
        from .providers.base import ImageModel
        return ImageModel
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# All available imports
__all__ = [
    # Core functions (lazy loaded)
    'generate_text',
    'stream_text',
    'generate_object', 
    'stream_object',
    
    # Provider base classes
    'Provider',
    'LanguageModel',
    'EmbeddingModel',
    'ImageModel',
    
    # Core types
    'Usage',
    'Message',
    'FinishReason',
    
    # Tools
    'Tool',
    'ToolCall',
    'ToolResult',
    'tool',
    'simple_tool',
    'ToolRegistry',
    
    # MCP
    'MCPClient',
    'MCPClientConfig',
    'create_mcp_client',
    'StdioMCPTransport',
    'StdioConfig',
    'SSEMCPTransport',
    'SSEConfig',
    
    # Schema validation
    'BaseSchema',
    'ValidationResult', 
    'SchemaValidationError',
    'PydanticSchema',
    'pydantic_schema',
    'JSONSchemaValidator',
    'jsonschema_schema',
    'MarshmallowSchema',
    'marshmallow_schema',
    'CerberusSchema',
    'cerberus_schema',
    
    # Agent system
    'Agent',
    'AgentSettings',
    
    # Registry
    'ProviderRegistry',
    'register_provider',
    'get_provider',
    
    # Middleware
    'LanguageModelMiddleware',
    'default_settings_middleware',
    'extract_reasoning_middleware',
    'simulate_streaming_middleware', 
    'wrap_language_model',
    
    # Testing
    'MockLanguageModel',
    'MockProvider', 
    'MockStreamPart',
    'create_mock_response',
    'create_stream_response',
    'create_test_messages',
    
    # Reasoning
    'extract_reasoning_text',
    'add_usage',
    'has_reasoning_tokens',
    'get_reasoning_token_ratio',
    'ReasoningExtractor'
]