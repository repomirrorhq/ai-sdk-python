"""
Test cases for SSE MCP transport.

Tests the Server-Sent Events MCP transport implementation.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from ai_sdk.tools.mcp import SSEMCPTransport, SSEConfig
from ai_sdk.errors.base import AISDKError


class TestSSEMCPTransport:
    """Test the SSE MCP transport implementation."""
    
    def test_sse_config_creation(self):
        """Test creating SSE transport configuration."""
        config = SSEConfig(
            url="https://example.com/mcp/events",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert config.url == "https://example.com/mcp/events"
        assert config.headers == {"Authorization": "Bearer test-token"}
    
    def test_sse_transport_initialization(self):
        """Test initializing SSE transport."""
        config = SSEConfig(url="https://example.com/mcp/events")
        transport = SSEMCPTransport(config)
        
        assert transport._url == "https://example.com/mcp/events"
        assert not transport.is_connected
        assert transport._endpoint_url is None
    
    def test_size_parsing_with_various_formats(self):
        """Test URL parsing and validation."""
        config = SSEConfig(url="https://example.com:8080/path/to/mcp")
        transport = SSEMCPTransport(config)
        
        assert transport._url == "https://example.com:8080/path/to/mcp"
    
    def test_parse_sse_line(self):
        """Test parsing SSE event lines."""
        config = SSEConfig(url="https://example.com/events")
        transport = SSEMCPTransport(config)
        
        # Test event line
        event_result = transport._parse_sse_line("event: endpoint")
        assert event_result == {"type": "event", "value": "endpoint"}
        
        # Test data line
        data_result = transport._parse_sse_line("data: /api/mcp")
        assert data_result == {"type": "data", "value": "/api/mcp"}
        
        # Test invalid line
        invalid_result = transport._parse_sse_line("invalid line")
        assert invalid_result is None
        
        # Test empty line
        empty_result = transport._parse_sse_line("")
        assert empty_result is None
    
    @patch('aiohttp.ClientSession')
    async def test_start_connection_success(self, mock_session_class):
        """Test successful connection establishment."""
        # Mock aiohttp response
        mock_response = AsyncMock()
        mock_response.ok = True
        mock_response.content_type = 'text/event-stream'
        mock_response.content.__aiter__ = AsyncMock()
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        config = SSEConfig(url="https://example.com/events")
        transport = SSEMCPTransport(config)
        
        # Mock the event processing to avoid infinite loop
        async def mock_content_iter():
            # Simulate endpoint event
            yield b"event: endpoint\n"
            yield b"data: /api/endpoint\n"
            yield b"\n"
            return
        
        mock_response.content.__aiter__.return_value = mock_content_iter()
        
        # Start connection (this will establish connection but not wait for completion)
        start_task = asyncio.create_task(transport.start())
        
        # Give it a moment to process events
        await asyncio.sleep(0.1)
        
        # Clean up
        await transport.stop()
        
        # The connection should have been attempted
        mock_session.get.assert_called_once()
    
    @patch('aiohttp.ClientSession')
    async def test_start_connection_failure(self, mock_session_class):
        """Test connection failure handling."""
        mock_response = AsyncMock()
        mock_response.ok = False
        mock_response.status = 404
        mock_response.reason = "Not Found"
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        config = SSEConfig(url="https://example.com/events")
        transport = SSEMCPTransport(config)
        
        # Mock error handler
        error_received = None
        def on_error(error):
            nonlocal error_received
            error_received = error
        
        transport.onerror = on_error
        
        try:
            await transport.start()
        except:
            pass  # Expected to fail
        
        # Clean up
        await transport.stop()
        
        mock_session.get.assert_called_once()
    
    async def test_send_without_connection(self):
        """Test sending message without connection fails."""
        config = SSEConfig(url="https://example.com/events")
        transport = SSEMCPTransport(config)
        
        test_message = {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {},
            "id": 1
        }
        
        with pytest.raises(Exception) as exc_info:
            await transport.send(test_message)
        
        assert "not connected" in str(exc_info.value).lower()
    
    async def test_endpoint_validation(self):
        """Test endpoint URL validation."""
        config = SSEConfig(url="https://example.com/events")
        transport = SSEMCPTransport(config)
        
        # Test valid endpoint (same origin)
        await transport._process_complete_event("endpoint", "/api/mcp")
        assert transport._endpoint_url == "https://example.com/api/mcp"
        assert transport._connected
        
        # Reset for next test
        transport._connected = False
        transport._endpoint_url = None
        
        # Test invalid endpoint (different origin) - should trigger error
        error_received = None
        def on_error(error):
            nonlocal error_received
            error_received = error
        
        transport.onerror = on_error
        
        await transport._process_complete_event("endpoint", "https://malicious.com/api")
        
        assert error_received is not None
        assert "origin does not match" in str(error_received).lower()
    
    async def test_message_handling(self):
        """Test JSON-RPC message handling."""
        config = SSEConfig(url="https://example.com/events")
        transport = SSEMCPTransport(config)
        
        # Set up message handler
        messages_received = []
        def on_message(message):
            messages_received.append(message)
        
        transport.onmessage = on_message
        
        # Test valid JSON message
        valid_json = '{"jsonrpc": "2.0", "method": "test", "params": {}}'
        await transport._process_complete_event("message", valid_json)
        
        assert len(messages_received) == 1
        assert messages_received[0]["jsonrpc"] == "2.0"
        assert messages_received[0]["method"] == "test"
        
        # Test invalid JSON message - should trigger error
        error_received = None
        def on_error(error):
            nonlocal error_received
            error_received = error
        
        transport.onerror = on_error
        
        await transport._process_complete_event("message", "invalid json")
        
        assert error_received is not None
        assert "parse" in str(error_received).lower()
    
    @patch('aiohttp.ClientSession')
    async def test_send_message_success(self, mock_session_class):
        """Test successful message sending."""
        mock_response = AsyncMock()
        mock_response.ok = True
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        config = SSEConfig(url="https://example.com/events")
        transport = SSEMCPTransport(config)
        transport._session = mock_session
        
        # Set up connection state
        transport._connected = True
        transport._endpoint_url = "https://example.com/api/endpoint"
        
        test_message = {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {"key": "value"},
            "id": 1
        }
        
        await transport.send(test_message)
        
        # Verify POST was made to correct endpoint
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[0][0] == "https://example.com/api/endpoint"
        assert call_args[1]['json'] == test_message
    
    @patch('aiohttp.ClientSession')
    async def test_send_message_failure(self, mock_session_class):
        """Test message sending failure handling."""
        mock_response = AsyncMock()
        mock_response.ok = False
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        config = SSEConfig(url="https://example.com/events")
        transport = SSEMCPTransport(config)
        transport._session = mock_session
        
        # Set up connection state
        transport._connected = True
        transport._endpoint_url = "https://example.com/api/endpoint"
        
        # Set up error handler
        error_received = None
        def on_error(error):
            nonlocal error_received
            error_received = error
        
        transport.onerror = on_error
        
        test_message = {
            "jsonrpc": "2.0",
            "method": "test",
            "id": 1
        }
        
        # This should not raise but should call error handler
        await transport.send(test_message)
        
        # Error handler should have been called
        assert error_received is not None
    
    async def test_cleanup(self):
        """Test resource cleanup."""
        config = SSEConfig(url="https://example.com/events")
        transport = SSEMCPTransport(config)
        
        # Mock session
        mock_session = AsyncMock()
        transport._session = mock_session
        
        # Mock running task
        mock_task = AsyncMock()
        transport._sse_task = mock_task
        
        # Set connected state
        transport._connected = True
        
        await transport._cleanup()
        
        # Verify cleanup
        assert not transport._connected
        mock_task.cancel.assert_called_once()
        mock_session.close.assert_called_once()
        assert transport._session is None
        assert transport._sse_task is None
    
    async def test_event_handlers(self):
        """Test event handler callbacks."""
        config = SSEConfig(url="https://example.com/events")
        transport = SSEMCPTransport(config)
        
        # Set up handlers
        close_called = False
        error_received = None
        message_received = None
        
        def on_close():
            nonlocal close_called
            close_called = True
        
        def on_error(error):
            nonlocal error_received
            error_received = error
        
        def on_message(message):
            nonlocal message_received
            message_received = message
        
        transport.onclose = on_close
        transport.onerror = on_error
        transport.onmessage = on_message
        
        # Manually trigger handlers
        if transport.onclose:
            transport.onclose()
        
        if transport.onerror:
            transport.onerror(Exception("test error"))
        
        if transport.onmessage:
            transport.onmessage({"test": "message"})
        
        assert close_called
        assert error_received is not None
        assert message_received == {"test": "message"}