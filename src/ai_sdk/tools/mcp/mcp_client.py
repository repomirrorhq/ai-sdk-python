"""MCP client implementation."""

import asyncio
import uuid
from typing import Any, Dict, Optional, Callable, Union
from pydantic import BaseModel

from ...errors.base import AISDKError
from ...tools.core import Tool
from .mcp_transport import MCPTransport, MCPTransportConfig, create_mcp_transport, is_custom_mcp_transport
from .json_rpc import JSONRPCRequest, JSONRPCResponse, JSONRPCError, JSONRPCMessage
from .types import (
    ToolSchemas,
    McpToolSet,
    InitializeResult,
    ListToolsResult,
    CallToolResult,
    Configuration,
    ServerCapabilities,
    LATEST_PROTOCOL_VERSION,
)

CLIENT_VERSION = "1.0.0"

class MCPClientError(AISDKError):
    """MCP client specific error."""
    pass

class MCPClientConfig(BaseModel):
    """Configuration for MCP client."""
    transport: Union[MCPTransportConfig, MCPTransport]
    on_uncaught_error: Optional[Callable[[Exception], None]] = None
    name: str = "ai-sdk-mcp-client"

class MCPClient:
    """MCP client interface."""
    
    async def tools(self, schemas: Optional[ToolSchemas] = "automatic") -> McpToolSet:
        """Get tools from the MCP server."""
        raise NotImplementedError
    
    async def close(self) -> None:
        """Close the MCP client connection."""
        raise NotImplementedError

class DefaultMCPClient(MCPClient):
    """Default MCP client implementation.
    
    A lightweight MCP Client implementation focused on tool conversion between MCP and AI SDK.
    The primary purpose is to fetch and convert MCP tools for use in AI SDK workflows.
    
    Features:
    - Automatic tool schema inference from server JSON schemas
    - Tool parameter validation and conversion
    - Connection management with MCP servers
    
    Not supported:
    - Client options (sampling, roots) - not needed for tool conversion
    - Accepting notifications from server
    - Session management
    - Resumable streams
    """
    
    def __init__(self, config: MCPClientConfig):
        self._transport: MCPTransport
        self._on_uncaught_error = config.on_uncaught_error
        self._client_info = Configuration(name=config.name, version=CLIENT_VERSION)
        self._request_message_id = 0
        self._response_handlers: Dict[Union[str, int], Callable[[Union[JSONRPCResponse, Exception]], None]] = {}
        self._server_capabilities: ServerCapabilities = ServerCapabilities()
        self._is_closed = True
        
        # Setup transport
        if is_custom_mcp_transport(config.transport):
            self._transport = config.transport
        else:
            self._transport = create_mcp_transport(config.transport)
        
        # Setup transport callbacks
        self._transport.onclose = self._on_close
        self._transport.onerror = self._on_error
        self._transport.onmessage = self._on_message
    
    async def init(self) -> "DefaultMCPClient":
        """Initialize the MCP client."""
        try:
            await self._transport.start()
            self._is_closed = False
            
            # Send initialize request
            result = await self._request(
                method="initialize",
                params={
                    "protocolVersion": LATEST_PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": self._client_info.model_dump(),
                }
            )
            
            # Validate and store result
            init_result = InitializeResult(**result)
            self._server_capabilities = init_result.capabilities
            
            # Send initialized notification
            await self._notify("notifications/initialized")
            
            return self
            
        except Exception as e:
            await self.close()
            raise MCPClientError(f"Failed to initialize MCP client: {e}")
    
    async def tools(self, schemas: Optional[ToolSchemas] = "automatic") -> McpToolSet:
        """Get tools from the MCP server."""
        if self._is_closed:
            raise MCPClientError("MCP client is closed")
        
        try:
            # List tools from server
            result = await self._request("tools/list")
            tools_result = ListToolsResult(**result)
            
            # Convert MCP tools to AI SDK tools
            converted_tools = {}
            for mcp_tool in tools_result.tools:
                ai_tool = self._convert_mcp_tool_to_ai_tool(mcp_tool)
                converted_tools[mcp_tool.name] = ai_tool
            
            return converted_tools
            
        except Exception as e:
            raise MCPClientError(f"Failed to get tools: {e}")
    
    async def close(self) -> None:
        """Close the MCP client connection."""
        if not self._is_closed:
            self._is_closed = True
            await self._transport.stop()
    
    def _convert_mcp_tool_to_ai_tool(self, mcp_tool) -> Tool:
        """Convert an MCP tool to an AI SDK tool."""
        async def execute_tool(**kwargs) -> Any:
            """Execute the MCP tool."""
            try:
                result = await self._request(
                    method="tools/call",
                    params={
                        "name": mcp_tool.name,
                        "arguments": kwargs
                    }
                )
                
                call_result = CallToolResult(**result)
                
                # Return content if available, otherwise tool_result
                if call_result.content:
                    # Convert content to string representation
                    content_str = ""
                    for item in call_result.content:
                        if hasattr(item, 'text'):
                            content_str += item.text + "\n"
                        elif hasattr(item, 'data'):
                            content_str += f"[Image: {item.mime_type}]\n"
                        elif hasattr(item, 'resource'):
                            content_str += f"[Resource: {item.resource.uri}]\n"
                    return content_str.strip()
                
                return call_result.tool_result
                
            except Exception as e:
                raise MCPClientError(f"Failed to execute MCP tool '{mcp_tool.name}': {e}")
        
        # Create AI SDK tool
        return Tool(
            name=mcp_tool.name,
            description=mcp_tool.description or f"MCP tool: {mcp_tool.name}",
            parameters=mcp_tool.input_schema,
            execute=execute_tool,
        )
    
    async def _request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Send a request and wait for response."""
        request_id = self._get_next_message_id()
        
        # Create response future
        future = asyncio.Future()
        self._response_handlers[request_id] = future.set_result
        
        # Create and send request
        request = JSONRPCRequest(
            id=request_id,
            method=method,
            params=params or {}
        )
        
        try:
            await self._transport.send(request)
            
            # Wait for response with timeout
            return await asyncio.wait_for(future, timeout=30.0)
            
        except asyncio.TimeoutError:
            self._response_handlers.pop(request_id, None)
            raise MCPClientError(f"Request timeout for method '{method}'")
        except Exception as e:
            self._response_handlers.pop(request_id, None)
            raise MCPClientError(f"Request failed for method '{method}': {e}")
    
    async def _notify(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Send a notification (no response expected)."""
        from .json_rpc import JSONRPCNotification
        
        notification = JSONRPCNotification(
            method=method,
            params=params or {}
        )
        
        await self._transport.send(notification)
    
    def _get_next_message_id(self) -> int:
        """Get the next message ID."""
        self._request_message_id += 1
        return self._request_message_id
    
    def _on_message(self, message: JSONRPCMessage) -> None:
        """Handle incoming messages."""
        if isinstance(message, dict):
            # Handle dict message
            if "method" in message:
                # This is a request or notification from server
                # This lightweight client doesn't support server requests
                self._on_error(MCPClientError("Unsupported message type from server"))
                return
            
            # This should be a response
            self._on_response(message)
        else:
            # Handle Pydantic model message
            if hasattr(message, "method"):
                self._on_error(MCPClientError("Unsupported message type from server"))
                return
            
            self._on_response(message)
    
    def _on_response(self, response: Union[JSONRPCResponse, JSONRPCError, Dict[str, Any]]) -> None:
        """Handle response messages."""
        try:
            # Extract response data
            if isinstance(response, dict):
                response_id = response.get("id")
                error = response.get("error")
                result = response.get("result")
            else:
                response_id = response.id
                error = getattr(response, "error", None)
                result = getattr(response, "result", None)
            
            # Get response handler
            handler = self._response_handlers.pop(response_id, None)
            if not handler:
                # Orphaned response
                return
            
            # Handle error responses
            if error:
                error_msg = error.get("message") if isinstance(error, dict) else str(error)
                handler(MCPClientError(f"Server error: {error_msg}"))
                return
            
            # Handle success response
            handler(result)
            
        except Exception as e:
            self._on_error(e)
    
    def _on_close(self) -> None:
        """Handle transport close."""
        self._is_closed = True
        # Cancel pending requests
        for handler in self._response_handlers.values():
            if callable(handler):
                handler(MCPClientError("Connection closed"))
        self._response_handlers.clear()
    
    def _on_error(self, error: Exception) -> None:
        """Handle transport errors."""
        if self._on_uncaught_error:
            self._on_uncaught_error(error)
        # Could also log error here

async def create_mcp_client(config: MCPClientConfig) -> MCPClient:
    """Create and initialize an MCP client."""
    client = DefaultMCPClient(config)
    return await client.init()