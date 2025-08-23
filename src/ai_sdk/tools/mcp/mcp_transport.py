"""MCP transport interface and implementations."""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Callable, Union, Dict, Any
from .json_rpc import JSONRPCMessage

class MCPTransport(ABC):
    """Abstract base class for MCP transports."""
    
    def __init__(self):
        self.onclose: Optional[Callable[[], None]] = None
        self.onerror: Optional[Callable[[Exception], None]] = None
        self.onmessage: Optional[Callable[[JSONRPCMessage], None]] = None
    
    @abstractmethod
    async def start(self) -> None:
        """Start the transport connection."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the transport connection."""
        pass
    
    @abstractmethod
    async def send(self, message: JSONRPCMessage) -> None:
        """Send a message through the transport."""
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the transport is connected."""
        pass

MCPTransportConfig = Union[Dict[str, Any], MCPTransport]

def create_mcp_transport(config: MCPTransportConfig) -> MCPTransport:
    """Create an MCP transport from configuration."""
    if isinstance(config, MCPTransport):
        return config
    
    # For now, only support STDIO transport config
    if config.get("type") == "stdio":
        from .stdio_transport import StdioMCPTransport, StdioConfig
        return StdioMCPTransport(StdioConfig(**config))
    
    raise ValueError(f"Unsupported transport configuration: {config}")

def is_custom_mcp_transport(transport: MCPTransportConfig) -> bool:
    """Check if transport config is a custom transport instance."""
    return isinstance(transport, MCPTransport)