"""
LlamaIndex Adapter for AI SDK

This module provides utilities to integrate AI SDK with LlamaIndex components,
allowing seamless conversion between LlamaIndex streams and AI SDK formats.
"""

from typing import Any, Dict, AsyncGenerator, Optional, Callable
from .langchain import StreamCallbacks, UIMessageChunk


class EngineResponse:
    """LlamaIndex Engine Response"""
    def __init__(self, delta: str):
        self.delta = delta


class LlamaIndexAdapter:
    """
    Adapter for converting LlamaIndex streams to AI SDK format.
    
    This adapter supports:
    - LlamaIndex Engine Response streams
    - LlamaIndex chat engine streams
    - LlamaIndex query engine streams
    """
    
    @staticmethod
    async def to_ui_message_stream(
        stream: AsyncGenerator[EngineResponse, None],
        callbacks: Optional[StreamCallbacks] = None
    ) -> AsyncGenerator[UIMessageChunk, None]:
        """
        Convert LlamaIndex engine streams to AI SDK UI Message Stream.
        
        Args:
            stream: LlamaIndex engine stream
            callbacks: Optional callbacks for stream processing
            
        Yields:
            UIMessageChunk: AI SDK compatible message chunks
        """
        is_stream_start = True
        
        try:
            # Signal stream start
            if callbacks and callbacks.on_start:
                callbacks.on_start()
            
            yield UIMessageChunk("text-start", "", "1")
            
            async for response in stream:
                try:
                    # Extract delta text from response
                    if hasattr(response, 'delta'):
                        delta_text = response.delta
                    elif isinstance(response, dict) and 'delta' in response:
                        delta_text = response['delta']
                    elif isinstance(response, str):
                        delta_text = response
                    else:
                        # Try to extract text from various LlamaIndex formats
                        delta_text = LlamaIndexAdapter._extract_text_from_response(response)
                    
                    # Trim whitespace at the start of stream
                    if is_stream_start and delta_text:
                        delta_text = delta_text.lstrip()
                        if delta_text:
                            is_stream_start = False
                    
                    if delta_text:
                        if callbacks and callbacks.on_text:
                            callbacks.on_text(delta_text)
                        yield UIMessageChunk("text-delta", delta_text, "1")
                        
                except Exception as chunk_error:
                    if callbacks and callbacks.on_error:
                        callbacks.on_error(chunk_error)
                    # Continue processing other chunks
                    continue
            
            yield UIMessageChunk("text-end", "", "1")
            
            if callbacks and callbacks.on_end:
                callbacks.on_end()
                
        except Exception as stream_error:
            if callbacks and callbacks.on_error:
                callbacks.on_error(stream_error)
            yield UIMessageChunk("error", str(stream_error), "1")
    
    @staticmethod
    def _extract_text_from_response(response: Any) -> str:
        """Extract text from various LlamaIndex response formats"""
        
        # Try common LlamaIndex response attributes
        if hasattr(response, 'response'):
            return str(response.response)
        elif hasattr(response, 'text'):
            return str(response.text)
        elif hasattr(response, 'content'):
            return str(response.content)
        elif hasattr(response, 'message'):
            return str(response.message)
        elif hasattr(response, 'delta'):
            return str(response.delta)
        
        # Try dictionary access
        if isinstance(response, dict):
            for key in ['response', 'text', 'content', 'message', 'delta']:
                if key in response:
                    return str(response[key])
        
        # Fallback to string representation
        return str(response) if response else ""
    
    @staticmethod
    async def from_chat_engine(
        chat_stream: AsyncGenerator[Any, None],
        callbacks: Optional[StreamCallbacks] = None
    ) -> AsyncGenerator[UIMessageChunk, None]:
        """
        Convert a LlamaIndex ChatEngine stream to AI SDK format.
        
        Args:
            chat_stream: LlamaIndex ChatEngine stream
            callbacks: Optional callbacks for stream processing
            
        Yields:
            UIMessageChunk: AI SDK compatible message chunks
        """
        async for chunk in LlamaIndexAdapter.to_ui_message_stream(chat_stream, callbacks):
            yield chunk
    
    @staticmethod
    async def from_query_engine(
        query_stream: AsyncGenerator[Any, None],
        callbacks: Optional[StreamCallbacks] = None
    ) -> AsyncGenerator[UIMessageChunk, None]:
        """
        Convert a LlamaIndex QueryEngine stream to AI SDK format.
        
        Args:
            query_stream: LlamaIndex QueryEngine stream
            callbacks: Optional callbacks for stream processing
            
        Yields:
            UIMessageChunk: AI SDK compatible message chunks
        """
        async for chunk in LlamaIndexAdapter.to_ui_message_stream(query_stream, callbacks):
            yield chunk
    
    @staticmethod
    async def from_llm_predictor(
        llm_stream: AsyncGenerator[Any, None],
        callbacks: Optional[StreamCallbacks] = None
    ) -> AsyncGenerator[UIMessageChunk, None]:
        """
        Convert a LlamaIndex LLMPredictor stream to AI SDK format.
        
        Args:
            llm_stream: LlamaIndex LLMPredictor stream
            callbacks: Optional callbacks for stream processing
            
        Yields:
            UIMessageChunk: AI SDK compatible message chunks
        """
        async for chunk in LlamaIndexAdapter.to_ui_message_stream(llm_stream, callbacks):
            yield chunk


# Convenience functions
async def to_ui_message_stream(
    stream: AsyncGenerator[EngineResponse, None],
    callbacks: Optional[StreamCallbacks] = None
) -> AsyncGenerator[UIMessageChunk, None]:
    """
    Convert LlamaIndex engine streams to AI SDK UI Message Stream.
    
    This is a convenience function that wraps LlamaIndexAdapter.to_ui_message_stream.
    
    Args:
        stream: LlamaIndex engine stream
        callbacks: Optional callbacks for stream processing
        
    Yields:
        UIMessageChunk: AI SDK compatible message chunks
    """
    async for chunk in LlamaIndexAdapter.to_ui_message_stream(stream, callbacks):
        yield chunk


def trim_start_of_stream():
    """
    Create a function that trims whitespace from the start of a stream.
    
    Returns:
        A function that trims leading whitespace until non-whitespace content is found
    """
    is_stream_start = True
    
    def trim_function(text: str) -> str:
        nonlocal is_stream_start
        if is_stream_start:
            text = text.lstrip()
            if text:
                is_stream_start = False
        return text
    
    return trim_function


# Create module-level adapter instance  
llamaindex_adapter = LlamaIndexAdapter()