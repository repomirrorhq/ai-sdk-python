"""Model Context Protocol (MCP) implementation for AI SDK Python.

This module provides MCP client functionality for connecting to MCP servers
and using their tools dynamically within the AI SDK.

MCP (Model Context Protocol) is a standard for AI tool integration that allows
language models to connect to external tool servers and use their capabilities.
"""

from .mcp_client import MCPClient, MCPClientConfig
from .mcp_transport import MCPTransport
from .stdio_transport import StdioMCPTransport, StdioConfig
from .sse_transport import SSEMCPTransport, SSEConfig
from .types import (
    MCPTool,
    CallToolResult,
    InitializeResult,
    ListToolsResult,
    ServerCapabilities,
    ToolSchemas,
    McpToolSet,
    LATEST_PROTOCOL_VERSION,
    SUPPORTED_PROTOCOL_VERSIONS,
)
from .json_rpc import (
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    JSONRPCNotification,
    JSONRPCMessage,
)

__all__ = [
    # Client
    "MCPClient",
    "MCPClientConfig",
    # Transport
    "MCPTransport",
    "StdioMCPTransport",
    "StdioConfig",
    "SSEMCPTransport",
    "SSEConfig",
    # Types
    "MCPTool",
    "CallToolResult",
    "InitializeResult",
    "ListToolsResult",
    "ServerCapabilities",
    "ToolSchemas",
    "McpToolSet",
    "LATEST_PROTOCOL_VERSION",
    "SUPPORTED_PROTOCOL_VERSIONS",
    # JSON-RPC
    "JSONRPCRequest",
    "JSONRPCResponse", 
    "JSONRPCError",
    "JSONRPCNotification",
    "JSONRPCMessage",
]