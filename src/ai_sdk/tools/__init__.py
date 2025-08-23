"""Tool system for AI SDK Python."""

from .core import (
    Tool,
    ToolCall,
    ToolResult,
    ToolCallOptions,
    ToolExecuteFunction,
    tool,
    dynamic_tool,
)
from .execution import (
    execute_tools,
    execute_tool_call,
)
from .schema import (
    create_tool_schema,
    validate_tool_input,
)
from .enhanced import (
    EnhancedTool,
    StreamingCallbacks,
    enhanced_tool,
    pydantic_tool,
    provider_defined_tool,
    dynamic_enhanced_tool,
)
from .schema_enhanced import (
    FlexibleSchema,
    normalize_schema,
    validate_schema_input,
    create_pydantic_tool_schema,
)
from .mcp import (
    MCPClient,
    MCPClientConfig,
    create_mcp_client,
    StdioMCPTransport,
    StdioConfig,
    MCPTransport,
)

__all__ = [
    # Core tool types and functions
    "Tool",
    "ToolCall",
    "ToolResult", 
    "ToolCallOptions",
    "ToolExecuteFunction",
    "tool",
    "dynamic_tool",
    
    # Enhanced tool system
    "EnhancedTool",
    "StreamingCallbacks",
    "enhanced_tool",
    "pydantic_tool",
    "provider_defined_tool",
    "dynamic_enhanced_tool",
    
    # Tool execution
    "execute_tools",
    "execute_tool_call",
    
    # Schema utilities
    "create_tool_schema",
    "validate_tool_input",
    "FlexibleSchema",
    "normalize_schema",
    "validate_schema_input",
    "create_pydantic_tool_schema",
    
    # MCP (Model Context Protocol)
    "MCPClient",
    "MCPClientConfig",
    "create_mcp_client",
    "StdioMCPTransport", 
    "StdioConfig",
    "MCPTransport",
]