"""STDIO transport implementation for MCP."""

import asyncio
import json
import subprocess
from typing import Optional, Dict, Any, Union, List
from pydantic import BaseModel
from .mcp_transport import MCPTransport
from .json_rpc import JSONRPCMessage

class StdioConfig(BaseModel):
    """Configuration for STDIO MCP transport."""
    command: str
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None

class ReadBuffer:
    """Buffer for reading JSON messages from STDIO."""
    
    def __init__(self):
        self._buffer = bytearray()
    
    def append(self, data: bytes) -> None:
        """Append data to the buffer."""
        self._buffer.extend(data)
    
    def try_read_message(self) -> Optional[str]:
        """Try to read a complete JSON message from buffer."""
        while True:
            try:
                # Look for newline
                newline_index = self._buffer.find(b'\n')
                if newline_index == -1:
                    return None
                
                # Extract line
                line = self._buffer[:newline_index].decode('utf-8').strip()
                self._buffer = self._buffer[newline_index + 1:]
                
                if not line:
                    continue
                    
                return line
                
            except UnicodeDecodeError:
                # Skip invalid UTF-8 data
                if newline_index != -1:
                    self._buffer = self._buffer[newline_index + 1:]
                else:
                    break
        
        return None

class StdioMCPTransport(MCPTransport):
    """STDIO transport for MCP communication."""
    
    def __init__(self, config: StdioConfig):
        super().__init__()
        self._config = config
        self._process: Optional[subprocess.Popen] = None
        self._read_task: Optional[asyncio.Task] = None
        self._read_buffer = ReadBuffer()
        self._stop_event = asyncio.Event()
    
    async def start(self) -> None:
        """Start the STDIO transport."""
        if self._process is not None:
            raise RuntimeError("StdioMCPTransport already started")
        
        try:
            # Build command
            cmd = [self._config.command]
            if self._config.args:
                cmd.extend(self._config.args)
            
            # Start process
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE if self._config.env is None else subprocess.STDOUT,
                env=self._config.env,
                cwd=self._config.cwd,
                text=False  # Binary mode for proper encoding handling
            )
            
            # Start reading task
            self._read_task = asyncio.create_task(self._read_loop())
            
        except Exception as e:
            await self._cleanup()
            if self.onerror:
                self.onerror(e)
            raise
    
    async def stop(self) -> None:
        """Stop the STDIO transport."""
        self._stop_event.set()
        await self._cleanup()
    
    async def send(self, message: JSONRPCMessage) -> None:
        """Send a message through STDIO."""
        if not self._process or not self._process.stdin:
            raise RuntimeError("Transport not connected")
        
        try:
            # Convert message to JSON
            if hasattr(message, 'model_dump'):
                # Pydantic model
                json_data = message.model_dump(by_alias=True)
            else:
                # Regular dict
                json_data = message
            
            json_str = json.dumps(json_data)
            data = (json_str + '\n').encode('utf-8')
            
            # Write to stdin
            self._process.stdin.write(data)
            await asyncio.get_event_loop().run_in_executor(
                None, self._process.stdin.flush
            )
            
        except Exception as e:
            if self.onerror:
                self.onerror(e)
            raise
    
    @property
    def is_connected(self) -> bool:
        """Check if transport is connected."""
        return (
            self._process is not None and 
            self._process.poll() is None
        )
    
    async def _read_loop(self) -> None:
        """Read messages from the process stdout."""
        if not self._process or not self._process.stdout:
            return
        
        try:
            while not self._stop_event.is_set() and self.is_connected:
                # Read data from stdout
                data = await asyncio.get_event_loop().run_in_executor(
                    None, self._process.stdout.read, 4096
                )
                
                if not data:
                    break
                
                # Add to buffer
                self._read_buffer.append(data)
                
                # Process complete messages
                while True:
                    message_str = self._read_buffer.try_read_message()
                    if message_str is None:
                        break
                    
                    try:
                        # Parse JSON message
                        message_data = json.loads(message_str)
                        
                        # Handle message
                        if self.onmessage:
                            self.onmessage(message_data)
                            
                    except json.JSONDecodeError as e:
                        if self.onerror:
                            self.onerror(e)
                        continue
                
        except Exception as e:
            if self.onerror:
                self.onerror(e)
        finally:
            if self.onclose:
                self.onclose()
    
    async def _cleanup(self) -> None:
        """Clean up resources."""
        # Stop read task
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
            self._read_task = None
        
        # Close process
        if self._process:
            if self._process.stdin:
                self._process.stdin.close()
            
            # Try graceful termination first
            try:
                self._process.terminate()
                await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, self._process.wait
                    ),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                # Force kill if graceful termination fails
                self._process.kill()
                await asyncio.get_event_loop().run_in_executor(
                    None, self._process.wait
                )
            
            self._process = None