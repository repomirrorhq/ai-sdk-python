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

# All imports are now lazy to prevent circular dependencies

# Core functionality - lazy imports to avoid circular dependencies
def __getattr__(name: str):
    """Lazy import of core functions to avoid circular dependencies."""
    # Core functions
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
    
    # Provider base classes
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
    
    # Provider types
    elif name == 'Usage':
        from .providers.types import Usage
        return Usage
    elif name == 'Message':
        from .providers.types import Message
        return Message
    elif name == 'FinishReason':
        from .providers.types import FinishReason
        return FinishReason
    
    # Reasoning utilities
    elif name == 'extract_reasoning_text':
        from .core.reasoning import extract_reasoning_text
        return extract_reasoning_text
    elif name == 'add_usage':
        from .core.reasoning import add_usage
        return add_usage
    elif name == 'has_reasoning_tokens':
        from .core.reasoning import has_reasoning_tokens
        return has_reasoning_tokens
    elif name == 'get_reasoning_token_ratio':
        from .core.reasoning import get_reasoning_token_ratio
        return get_reasoning_token_ratio
    elif name == 'ReasoningExtractor':
        from .core.reasoning import ReasoningExtractor
        return ReasoningExtractor
        
    # Tools
    elif name == 'Tool':
        from .tools import Tool
        return Tool
    elif name == 'ToolCall':
        from .tools import ToolCall
        return ToolCall
    elif name == 'ToolResult':
        from .tools import ToolResult
        return ToolResult
    elif name == 'tool':
        from .tools import tool
        return tool
    elif name == 'simple_tool':
        from .tools import simple_tool
        return simple_tool
    elif name == 'ToolRegistry':
        from .tools import ToolRegistry
        return ToolRegistry
        
    # MCP
    elif name == 'MCPClient':
        from .tools import MCPClient
        return MCPClient
    elif name == 'MCPClientConfig':
        from .tools import MCPClientConfig
        return MCPClientConfig
    elif name == 'create_mcp_client':
        from .tools import create_mcp_client
        return create_mcp_client
    elif name == 'StdioMCPTransport':
        from .tools import StdioMCPTransport
        return StdioMCPTransport
    elif name == 'StdioConfig':
        from .tools import StdioConfig
        return StdioConfig
    elif name == 'SSEMCPTransport':
        from .tools import SSEMCPTransport
        return SSEMCPTransport
    elif name == 'SSEConfig':
        from .tools import SSEConfig
        return SSEConfig
        
    # Schema validation
    elif name == 'BaseSchema':
        from .schemas import BaseSchema
        return BaseSchema
    elif name == 'ValidationResult':
        from .schemas import ValidationResult
        return ValidationResult
    elif name == 'SchemaValidationError':
        from .schemas import SchemaValidationError
        return SchemaValidationError
    elif name == 'PydanticSchema':
        from .schemas import PydanticSchema
        return PydanticSchema
    elif name == 'pydantic_schema':
        from .schemas import pydantic_schema
        return pydantic_schema
    elif name == 'JSONSchemaValidator':
        from .schemas import JSONSchemaValidator
        return JSONSchemaValidator
    elif name == 'jsonschema_schema':
        from .schemas import jsonschema_schema
        return jsonschema_schema
    elif name == 'MarshmallowSchema':
        from .schemas import MarshmallowSchema
        return MarshmallowSchema
    elif name == 'marshmallow_schema':
        from .schemas import marshmallow_schema
        return marshmallow_schema
    elif name == 'CerberusSchema':
        from .schemas import CerberusSchema
        return CerberusSchema
    elif name == 'cerberus_schema':
        from .schemas import cerberus_schema
        return cerberus_schema
        
    # Agent system
    elif name == 'Agent':
        from .agent import Agent
        return Agent
    elif name == 'AgentSettings':
        from .agent import AgentSettings
        return AgentSettings
        
    # Registry
    elif name == 'ProviderRegistry':
        from .registry import ProviderRegistry
        return ProviderRegistry
    elif name == 'register_provider':
        from .registry import register_provider
        return register_provider
    elif name == 'get_provider':
        from .registry import get_provider
        return get_provider
        
    # Middleware
    elif name == 'LanguageModelMiddleware':
        from .middleware import LanguageModelMiddleware
        return LanguageModelMiddleware
    elif name == 'default_settings_middleware':
        from .middleware import default_settings_middleware
        return default_settings_middleware
    elif name == 'extract_reasoning_middleware':
        from .middleware import extract_reasoning_middleware
        return extract_reasoning_middleware
    elif name == 'simulate_streaming_middleware':
        from .middleware import simulate_streaming_middleware
        return simulate_streaming_middleware
    elif name == 'wrap_language_model':
        from .middleware import wrap_language_model
        return wrap_language_model
        
    # Testing utilities
    elif name == 'MockLanguageModel':
        from .testing import MockLanguageModel
        return MockLanguageModel
    elif name == 'MockProvider':
        from .testing import MockProvider
        return MockProvider
    elif name == 'MockStreamPart':
        from .testing import MockStreamPart
        return MockStreamPart
    elif name == 'create_mock_response':
        from .testing import create_mock_response
        return create_mock_response
    elif name == 'create_stream_response':
        from .testing import create_stream_response
        return create_stream_response
    elif name == 'create_test_messages':
        from .testing import create_test_messages
        return create_test_messages
        
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