"""Tests for MCP (Model Context Protocol) implementation."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai_sdk.tools.mcp import (
    MCPClient,
    MCPClientConfig,
    DefaultMCPClient,
    create_mcp_client,
    StdioMCPTransport,
    StdioConfig,
    MCPTransport,
    JSONRPCRequest,
    JSONRPCResponse,
    MCPClientError,
)
from ai_sdk.tools.mcp.types import InitializeResult, ListToolsResult, MCPTool, ServerCapabilities

class MockMCPTransport(MCPTransport):
    """Mock MCP transport for testing."""
    
    def __init__(self):
        super().__init__()
        self.messages_sent = []
        self.is_started = False
        self._connected = False
    
    async def start(self) -> None:
        self.is_started = True
        self._connected = True
    
    async def stop(self) -> None:
        self.is_started = False
        self._connected = False
        if self.onclose:
            self.onclose()
    
    async def send(self, message) -> None:
        self.messages_sent.append(message)
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    def simulate_message(self, message):
        """Simulate receiving a message."""
        if self.onmessage:
            self.onmessage(message)
    
    def simulate_error(self, error):
        """Simulate an error."""
        if self.onerror:
            self.onerror(error)

@pytest.fixture
def mock_transport():
    """Create a mock MCP transport."""
    return MockMCPTransport()

@pytest.fixture  
def mcp_config(mock_transport):
    """Create MCP client config with mock transport."""
    return MCPClientConfig(transport=mock_transport)

class TestMCPTransport:
    """Test MCP transport functionality."""
    
    def test_stdio_config_creation(self):
        """Test StdioConfig creation."""
        config = StdioConfig(
            command="test-server",
            args=["--port", "3000"],
            env={"TEST_VAR": "value"}
        )
        
        assert config.command == "test-server"
        assert config.args == ["--port", "3000"]
        assert config.env == {"TEST_VAR": "value"}

class TestMCPClient:
    """Test MCP client functionality."""
    
    def test_client_config_creation(self, mock_transport):
        """Test MCP client config creation."""
        config = MCPClientConfig(
            transport=mock_transport,
            name="test-client"
        )
        
        assert config.transport == mock_transport
        assert config.name == "test-client"
    
    def test_client_creation(self, mcp_config):
        """Test MCP client creation."""
        client = DefaultMCPClient(mcp_config)
        assert client is not None
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, mock_transport):
        """Test MCP client initialization."""
        config = MCPClientConfig(transport=mock_transport)
        client = DefaultMCPClient(config)
        
        # Mock the initialization response
        init_response = {
            "id": 1,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "serverInfo": {"name": "test-server", "version": "1.0.0"}
            }
        }
        
        # Start initialization
        init_task = asyncio.create_task(client.init())
        
        # Give a moment for the request to be sent
        await asyncio.sleep(0.01)
        
        # Simulate server response
        mock_transport.simulate_message(init_response)
        
        # Wait for initialization to complete
        initialized_client = await init_task
        
        assert initialized_client is not None
        assert not client._is_closed
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_client_tools_listing(self, mock_transport):
        """Test listing tools from MCP server."""
        config = MCPClientConfig(transport=mock_transport)
        client = DefaultMCPClient(config)
        
        # Mock initialization
        init_response = {
            "id": 1,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "test-server", "version": "1.0.0"}
            }
        }
        
        # Initialize client
        init_task = asyncio.create_task(client.init())
        await asyncio.sleep(0.01)
        mock_transport.simulate_message(init_response)
        await init_task
        
        # Mock tools listing response
        tools_response = {
            "id": 2,
            "result": {
                "tools": [
                    {
                        "name": "read_file",
                        "description": "Read a file from disk",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "File path"}
                            },
                            "required": ["path"]
                        }
                    }
                ]
            }
        }
        
        # Request tools
        tools_task = asyncio.create_task(client.tools())
        await asyncio.sleep(0.01)
        mock_transport.simulate_message(tools_response)
        
        tools = await tools_task
        
        assert len(tools) == 1
        assert "read_file" in tools
        assert tools["read_file"].name == "read_file"
        assert tools["read_file"].description == "Read a file from disk"
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_client_tool_execution(self, mock_transport):
        """Test executing MCP tools."""
        config = MCPClientConfig(transport=mock_transport)
        client = DefaultMCPClient(config)
        
        # Mock initialization
        init_response = {
            "id": 1,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "test-server", "version": "1.0.0"}
            }
        }
        
        # Initialize client
        init_task = asyncio.create_task(client.init())
        await asyncio.sleep(0.01)
        mock_transport.simulate_message(init_response)
        await init_task
        
        # Mock tools listing
        tools_response = {
            "id": 2,
            "result": {
                "tools": [
                    {
                        "name": "echo",
                        "description": "Echo input text",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"}
                            },
                            "required": ["text"]
                        }
                    }
                ]
            }
        }
        
        # Get tools
        tools_task = asyncio.create_task(client.tools())
        await asyncio.sleep(0.01)
        mock_transport.simulate_message(tools_response)
        tools = await tools_task
        
        # Mock tool execution response
        exec_response = {
            "id": 3,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Hello, World!"
                    }
                ]
            }
        }
        
        # Execute tool
        echo_tool = tools["echo"]
        exec_task = asyncio.create_task(echo_tool.execute(text="Hello, World!"))
        await asyncio.sleep(0.01)
        mock_transport.simulate_message(exec_response)
        
        result = await exec_task
        assert result == "Hello, World!"
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_client_error_handling(self, mock_transport):
        """Test MCP client error handling."""
        config = MCPClientConfig(transport=mock_transport)
        client = DefaultMCPClient(config)
        
        # Test connection error
        with pytest.raises(MCPClientError):
            await client.tools()  # Should fail because client is not initialized
    
    @pytest.mark.asyncio
    async def test_client_close(self, mock_transport):
        """Test MCP client close."""
        config = MCPClientConfig(transport=mock_transport)
        client = DefaultMCPClient(config)
        
        await client.close()
        assert client._is_closed

class TestMCPIntegration:
    """Test MCP integration with AI SDK."""
    
    @pytest.mark.asyncio
    async def test_create_mcp_client_function(self, mock_transport):
        """Test the create_mcp_client helper function."""
        config = MCPClientConfig(transport=mock_transport)
        
        # Mock initialization response
        init_response = {
            "id": 1,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "serverInfo": {"name": "test-server", "version": "1.0.0"}
            }
        }
        
        # Create client using helper function
        client_task = asyncio.create_task(create_mcp_client(config))
        await asyncio.sleep(0.01)
        mock_transport.simulate_message(init_response)
        
        client = await client_task
        assert isinstance(client, DefaultMCPClient)
        
        await client.close()

if __name__ == "__main__":
    pytest.main([__file__])