"""UI Message Stream implementation for AI SDK Python.

This module provides streaming functionality for UI messages, including
stream creation, response handling, and SSE (Server-Sent Events) transformation.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, AsyncIterator, Awaitable, Callable, Dict, List, Optional, Protocol, Union
from abc import ABC, abstractmethod

from .ui_messages import UIMessage
from ..utils.id_generator import generate_id

# Type aliases
UIMessageStreamOnFinishCallback = Callable[[UIMessage], Union[None, Awaitable[None]]]

class UIMessageChunk(Protocol):
    """Protocol for UI message chunks."""
    type: str

class ErrorChunk:
    """Error chunk for UI message streams."""
    
    def __init__(self, error_text: str):
        self.type = "error"
        self.error_text = error_text

class UIMessageStreamWriter(Protocol):
    """Writer interface for UI message streams."""
    
    def write(self, chunk: UIMessageChunk) -> None:
        """Write a chunk to the stream."""
        ...
    
    def merge(self, stream: AsyncIterator[UIMessageChunk]) -> None:
        """Merge another stream into this writer."""
        ...
    
    def on_error(self, error: Exception) -> str:
        """Handle errors and return error text."""
        ...

class UIMessageStream:
    """UI Message Stream for handling streaming UI messages."""
    
    def __init__(
        self,
        execute: Callable[[UIMessageStreamWriter], Union[None, Awaitable[None]]],
        on_error: Optional[Callable[[Exception], str]] = None,
        original_messages: Optional[List[UIMessage]] = None,
        on_finish: Optional[UIMessageStreamOnFinishCallback] = None,
        generate_id_func: Optional[Callable[[], str]] = None,
    ):
        self.execute = execute
        self.on_error = on_error or (lambda e: str(e))
        self.original_messages = original_messages or []
        self.on_finish = on_finish
        self.generate_id_func = generate_id_func or generate_id
        self._message_id = self.generate_id_func()
        self._chunks: List[UIMessageChunk] = []
        self._controller: Optional[AsyncIterator[UIMessageChunk]] = None
        
    async def __aiter__(self) -> AsyncIterator[UIMessageChunk]:
        """Async iterator for the stream."""
        ongoing_promises: List[asyncio.Task] = []
        
        # Create a queue for chunks
        chunk_queue: asyncio.Queue[Optional[UIMessageChunk]] = asyncio.Queue()
        
        def safe_enqueue(chunk: UIMessageChunk) -> None:
            """Safely enqueue a chunk."""
            try:
                chunk_queue.put_nowait(chunk)
            except asyncio.QueueFull:
                # Handle queue full scenario
                pass
        
        class Writer:
            """Writer implementation for the execute function."""
            
            def write(self, chunk: UIMessageChunk) -> None:
                safe_enqueue(chunk)
            
            def merge(self, stream: AsyncIterator[UIMessageChunk]) -> None:
                async def merge_task():
                    try:
                        async for chunk in stream:
                            safe_enqueue(chunk)
                    except Exception as e:
                        safe_enqueue(ErrorChunk(self.on_error(e)))
                
                task = asyncio.create_task(merge_task())
                ongoing_promises.append(task)
            
            def on_error(self, error: Exception) -> str:
                return self.on_error(error)
        
        writer = Writer()
        
        # Execute the main function
        try:
            result = self.execute(writer)
            if asyncio.iscoroutine(result):
                async def execute_task():
                    try:
                        await result
                    except Exception as e:
                        safe_enqueue(ErrorChunk(self.on_error(e)))
                    finally:
                        # Signal completion
                        chunk_queue.put_nowait(None)
                
                task = asyncio.create_task(execute_task())
                ongoing_promises.append(task)
            else:
                # Signal completion for sync execution
                chunk_queue.put_nowait(None)
        except Exception as e:
            safe_enqueue(ErrorChunk(self.on_error(e)))
            chunk_queue.put_nowait(None)
        
        # Wait for all ongoing tasks and yield chunks
        completion_signaled = False
        while not completion_signaled or ongoing_promises:
            try:
                # Wait for either a chunk or task completion
                done_tasks = []
                if ongoing_promises:
                    done, pending = await asyncio.wait(
                        ongoing_promises + [asyncio.create_task(chunk_queue.get())],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    # Process completed tasks
                    for task in done:
                        if task in ongoing_promises:
                            ongoing_promises.remove(task)
                            done_tasks.append(task)
                        else:
                            # This is the chunk queue get task
                            chunk = await task
                            if chunk is None:
                                completion_signaled = True
                            else:
                                yield chunk
                    
                    # Cancel pending chunk queue task if we have other work
                    for task in pending:
                        if task not in ongoing_promises:
                            task.cancel()
                else:
                    # No ongoing tasks, just wait for chunks
                    chunk = await chunk_queue.get()
                    if chunk is None:
                        completion_signaled = True
                    else:
                        yield chunk
                        
            except asyncio.CancelledError:
                break
        
        # Call finish callback if provided
        if self.on_finish:
            # Create a final message from all chunks
            final_message = self._create_final_message()
            try:
                callback_result = self.on_finish(final_message)
                if asyncio.iscoroutine(callback_result):
                    await callback_result
            except Exception:
                # Suppress callback errors
                pass
    
    def _create_final_message(self) -> UIMessage:
        """Create a final UI message from collected chunks."""
        # This is a simplified implementation
        # In practice, you'd need to reconstruct the message from chunks
        return UIMessage(
            id=self._message_id,
            role="assistant",
            parts=[]
        )

def create_ui_message_stream(
    execute: Callable[[UIMessageStreamWriter], Union[None, Awaitable[None]]],
    on_error: Optional[Callable[[Exception], str]] = None,
    original_messages: Optional[List[UIMessage]] = None,
    on_finish: Optional[UIMessageStreamOnFinishCallback] = None,
    generate_id_func: Optional[Callable[[], str]] = None,
) -> UIMessageStream:
    """Create a UI message stream.
    
    Args:
        execute: Function that executes the streaming logic
        on_error: Error handler function
        original_messages: Original messages for persistence mode
        on_finish: Callback when stream finishes
        generate_id_func: Function to generate message IDs
        
    Returns:
        UIMessageStream instance
    """
    return UIMessageStream(
        execute=execute,
        on_error=on_error,
        original_messages=original_messages,
        on_finish=on_finish,
        generate_id_func=generate_id_func,
    )

async def create_ui_message_stream_response(
    stream: UIMessageStream,
    headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Create a response from a UI message stream.
    
    Args:
        stream: The UI message stream
        headers: Optional HTTP headers
        
    Returns:
        Response dictionary with stream data
    """
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)
    
    response_headers = {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        **UI_MESSAGE_STREAM_HEADERS,
        **(headers or {})
    }
    
    return {
        "chunks": chunks,
        "headers": response_headers,
    }

async def pipe_ui_message_stream_to_response(
    stream: UIMessageStream,
    response_writer: Any,  # Framework-specific response writer
) -> None:
    """Pipe a UI message stream to a response.
    
    Args:
        stream: The UI message stream
        response_writer: Framework-specific response writer
    """
    async for chunk in stream:
        # Write chunk to response (implementation depends on framework)
        if hasattr(response_writer, 'write'):
            response_writer.write(json.dumps(chunk.__dict__) + '\n')
        elif hasattr(response_writer, 'send'):
            await response_writer.send(json.dumps(chunk.__dict__) + '\n')

async def read_ui_message_stream(
    stream: UIMessageStream
) -> List[UIMessageChunk]:
    """Read all chunks from a UI message stream.
    
    Args:
        stream: The UI message stream
        
    Returns:
        List of all chunks from the stream
    """
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)
    return chunks

class JsonToSseTransformStream:
    """Transform JSON chunks to Server-Sent Events format."""
    
    def __init__(self):
        pass
    
    async def transform(
        self,
        stream: AsyncIterator[UIMessageChunk]
    ) -> AsyncIterator[str]:
        """Transform UI message chunks to SSE format.
        
        Args:
            stream: Stream of UI message chunks
            
        Yields:
            SSE-formatted strings
        """
        async for chunk in stream:
            chunk_json = json.dumps(chunk.__dict__)
            yield f"data: {chunk_json}\n\n"

# Headers for UI message streams
UI_MESSAGE_STREAM_HEADERS = {
    "X-AI-SDK-UI-Message-Stream": "true",
    "X-AI-SDK-Version": "4.0.0",  # Update version as needed
}