"""SSE (Server-Sent Events) transport implementation for MCP."""

import asyncio
import json
from typing import Optional, Dict, Any, Callable
from urllib.parse import urljoin, urlparse
import aiohttp
from pydantic import BaseModel

from .mcp_transport import MCPTransport
from .json_rpc import JSONRPCMessage
from ...errors.base import AISDKError


class SSETransportError(AISDKError):
    """Error that occurs during SSE MCP transport operations."""
    pass


class SSEConfig(BaseModel):
    """Configuration for SSE MCP transport."""
    url: str
    headers: Optional[Dict[str, str]] = None


class SSEMCPTransport(MCPTransport):
    """SSE (Server-Sent Events) transport for MCP communication.
    
    This transport connects to MCP servers over HTTP using Server-Sent Events
    for receiving messages and HTTP POST for sending messages.
    """
    
    def __init__(self, config: SSEConfig):
        super().__init__()
        self._config = config
        self._url = config.url
        self._endpoint_url: Optional[str] = None
        self._connected = False
        self._session: Optional[aiohttp.ClientSession] = None
        self._sse_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
    
    async def start(self) -> None:
        """Start the SSE transport."""
        if self._connected:
            return
        
        self._stop_event.clear()
        
        try:
            # Create session with custom headers
            headers = self._config.headers or {}
            headers['Accept'] = 'text/event-stream'
            
            connector = aiohttp.TCPConnector()
            timeout = aiohttp.ClientTimeout(total=None)  # No timeout for SSE connections
            
            self._session = aiohttp.ClientSession(
                headers=headers,
                connector=connector,
                timeout=timeout
            )
            
            # Start SSE connection
            self._sse_task = asyncio.create_task(self._establish_connection())
            
            # Wait for connection to be established (endpoint received)
            await asyncio.wait_for(
                self._wait_for_connection(),
                timeout=30.0  # 30 second timeout for initial connection
            )
            
        except Exception as e:
            await self._cleanup()
            if self.onerror:
                self.onerror(e)
            raise SSETransportError(f"Failed to start SSE transport: {str(e)}") from e
    
    async def stop(self) -> None:
        """Stop the SSE transport."""
        self._stop_event.set()
        await self._cleanup()
    
    async def send(self, message: JSONRPCMessage) -> None:
        """Send a message via HTTP POST to the endpoint."""
        if not self._endpoint_url or not self._connected:
            raise SSETransportError("SSE transport not connected")
        
        if not self._session:
            raise SSETransportError("No active session")
        
        try:
            # Convert message to JSON
            if hasattr(message, 'model_dump'):
                # Pydantic model
                json_data = message.model_dump(by_alias=True)
            else:
                # Regular dict
                json_data = message
            
            headers = {'Content-Type': 'application/json'}
            
            async with self._session.post(
                self._endpoint_url,
                json=json_data,
                headers=headers
            ) as response:
                if not response.ok:
                    error_text = await response.text()
                    error_msg = f"HTTP {response.status}: {error_text}"
                    error = SSETransportError(f"Failed to send message: {error_msg}")
                    if self.onerror:
                        self.onerror(error)
                    raise error
                        
        except Exception as e:
            if self.onerror:
                self.onerror(e)
            raise
    
    @property
    def is_connected(self) -> bool:
        """Check if transport is connected."""
        return self._connected
    
    async def _establish_connection(self) -> None:
        """Establish SSE connection and process events."""
        if not self._session:
            return
        
        try:
            async with self._session.get(self._url) as response:
                if not response.ok:
                    error = SSETransportError(f"SSE connection failed: {response.status} {response.reason}")
                    if self.onerror:
                        self.onerror(error)
                    return
                
                if response.content_type != 'text/event-stream':
                    error = SSETransportError(f"Expected text/event-stream, got {response.content_type}")
                    if self.onerror:
                        self.onerror(error)
                    return
                
                # Process SSE events
                async for line in response.content:
                    if self._stop_event.is_set():
                        break
                    
                    try:
                        line_str = line.decode('utf-8').strip()
                        if not line_str:
                            continue
                        
                        # Parse SSE event
                        event_data = self._parse_sse_line(line_str)
                        if event_data:
                            await self._handle_sse_event(event_data)
                    
                    except Exception as e:
                        if self.onerror:
                            self.onerror(e)
                        continue
        
        except asyncio.CancelledError:
            # Expected when stopping
            pass
        except Exception as e:
            if self.onerror:
                self.onerror(e)
        finally:
            if self._connected:
                self._connected = False
                if self.onclose:
                    self.onclose()
    
    def _parse_sse_line(self, line: str) -> Optional[Dict[str, str]]:
        """Parse a single SSE line."""
        if line.startswith('event:'):
            return {'type': 'event', 'value': line[6:].strip()}
        elif line.startswith('data:'):
            return {'type': 'data', 'value': line[5:].strip()}
        return None
    
    async def _handle_sse_event(self, event_data: Dict[str, str]) -> None:
        """Handle parsed SSE event data."""
        if not hasattr(self, '_current_event'):
            self._current_event = {'event': None, 'data': None}
        
        if event_data['type'] == 'event':
            self._current_event['event'] = event_data['value']
        elif event_data['type'] == 'data':
            self._current_event['data'] = event_data['value']
            
            # Process complete event
            if self._current_event['event'] and self._current_event['data']:
                await self._process_complete_event(
                    self._current_event['event'],
                    self._current_event['data']
                )
                # Reset for next event
                self._current_event = {'event': None, 'data': None}
    
    async def _process_complete_event(self, event: str, data: str) -> None:
        """Process a complete SSE event."""
        try:
            if event == 'endpoint':
                # Validate endpoint URL
                parsed_base = urlparse(self._url)
                endpoint_url = urljoin(self._url, data)
                parsed_endpoint = urlparse(endpoint_url)
                
                if parsed_endpoint.netloc != parsed_base.netloc:
                    error = SSETransportError(
                        f"Endpoint origin does not match connection origin: {parsed_endpoint.netloc}"
                    )
                    if self.onerror:
                        self.onerror(error)
                    return
                
                self._endpoint_url = endpoint_url
                self._connected = True
                
            elif event == 'message':
                # Parse and handle JSON-RPC message
                try:
                    message_data = json.loads(data)
                    if self.onmessage:
                        self.onmessage(message_data)
                except json.JSONDecodeError as e:
                    error = SSETransportError(f"Failed to parse message: {str(e)}")
                    if self.onerror:
                        self.onerror(error)
        
        except Exception as e:
            if self.onerror:
                self.onerror(e)
    
    async def _wait_for_connection(self) -> None:
        """Wait for connection to be established (endpoint received)."""
        while not self._connected and not self._stop_event.is_set():
            await asyncio.sleep(0.1)
        
        if not self._connected:
            raise SSETransportError("Connection was not established")
    
    async def _cleanup(self) -> None:
        """Clean up resources."""
        self._connected = False
        
        # Stop SSE task
        if self._sse_task:
            self._sse_task.cancel()
            try:
                await self._sse_task
            except asyncio.CancelledError:
                pass
            self._sse_task = None
        
        # Close session
        if self._session:
            await self._session.close()
            self._session = None