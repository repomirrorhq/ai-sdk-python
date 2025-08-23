"""
LangChain Adapter for AI SDK

This module provides utilities to integrate AI SDK with LangChain components,
allowing seamless conversion between LangChain streams and AI SDK formats.
"""

from typing import Any, Dict, List, Union, AsyncGenerator, Optional, Callable
import asyncio
from enum import Enum


class LangChainImageDetail(str, Enum):
    """LangChain image detail levels"""
    AUTO = "auto"
    LOW = "low"
    HIGH = "high"


class LangChainMessageContentText:
    """LangChain text content"""
    def __init__(self, text: str):
        self.type = "text"
        self.text = text


class LangChainMessageContentImageUrl:
    """LangChain image URL content"""
    def __init__(self, image_url: Union[str, Dict[str, Any]]):
        self.type = "image_url"
        self.image_url = image_url


LangChainMessageContentComplex = Union[
    LangChainMessageContentText,
    LangChainMessageContentImageUrl,
    Dict[str, Any]
]

LangChainMessageContent = Union[str, List[LangChainMessageContentComplex]]


class LangChainAIMessageChunk:
    """LangChain AI Message Chunk"""
    def __init__(self, content: LangChainMessageContent):
        self.content = content


class LangChainStreamEvent:
    """LangChain Stream Event v2"""
    def __init__(self, event: str, data: Any):
        self.event = event
        self.data = data


class StreamCallbacks:
    """Callbacks for stream processing"""
    def __init__(
        self,
        on_start: Optional[Callable[[], None]] = None,
        on_text: Optional[Callable[[str], None]] = None,
        on_end: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        self.on_start = on_start
        self.on_text = on_text
        self.on_end = on_end
        self.on_error = on_error


class UIMessageChunk:
    """UI Message Chunk for streaming responses"""
    def __init__(self, chunk_type: str, content: Any, message_id: str = "1"):
        self.type = chunk_type
        self.content = content
        self.id = message_id
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "content": self.content,
            "id": self.id
        }


class LangChainAdapter:
    """
    Adapter for converting LangChain streams to AI SDK format.
    
    This adapter supports:
    - LangChainAIMessageChunk streams (from LangChain model.stream output)
    - String streams (from LangChain StringOutputParser output)
    - LangChain Stream Events v2
    """
    
    @staticmethod
    async def to_ui_message_stream(
        stream: AsyncGenerator[Union[LangChainStreamEvent, LangChainAIMessageChunk, str], None],
        callbacks: Optional[StreamCallbacks] = None
    ) -> AsyncGenerator[UIMessageChunk, None]:
        """
        Convert LangChain output streams to AI SDK UI Message Stream.
        
        Args:
            stream: LangChain stream (message chunks, strings, or events)
            callbacks: Optional callbacks for stream processing
            
        Yields:
            UIMessageChunk: AI SDK compatible message chunks
        """
        try:
            # Signal stream start
            if callbacks and callbacks.on_start:
                callbacks.on_start()
            
            yield UIMessageChunk("text-start", "", "1")
            
            async for value in stream:
                try:
                    # Handle string streams (e.g., from StringOutputParser)
                    if isinstance(value, str):
                        if callbacks and callbacks.on_text:
                            callbacks.on_text(value)
                        yield UIMessageChunk("text-delta", value, "1")
                        continue
                    
                    # Handle LangChain Stream Events v2
                    if isinstance(value, LangChainStreamEvent):
                        if value.event == "on_chat_model_stream":
                            chunk = value.data.get("chunk") if value.data else None
                            if chunk:
                                text_content = LangChainAdapter._extract_text_from_chunk(chunk)
                                if text_content:
                                    if callbacks and callbacks.on_text:
                                        callbacks.on_text(text_content)
                                    yield UIMessageChunk("text-delta", text_content, "1")
                        continue
                    
                    # Handle AI Message Chunks
                    if isinstance(value, LangChainAIMessageChunk):
                        text_content = LangChainAdapter._extract_text_from_chunk(value)
                        if text_content:
                            if callbacks and callbacks.on_text:
                                callbacks.on_text(text_content)
                            yield UIMessageChunk("text-delta", text_content, "1")
                        continue
                    
                    # Handle dictionary-like objects (fallback)
                    if isinstance(value, dict):
                        # Try to extract content from various LangChain formats
                        if "content" in value:
                            text_content = LangChainAdapter._extract_text_from_content(value["content"])
                            if text_content:
                                if callbacks and callbacks.on_text:
                                    callbacks.on_text(text_content)
                                yield UIMessageChunk("text-delta", text_content, "1")
                        elif "text" in value:
                            if callbacks and callbacks.on_text:
                                callbacks.on_text(value["text"])
                            yield UIMessageChunk("text-delta", value["text"], "1")
                        elif "delta" in value:
                            if callbacks and callbacks.on_text:
                                callbacks.on_text(value["delta"])
                            yield UIMessageChunk("text-delta", value["delta"], "1")
                            
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
    def _extract_text_from_chunk(chunk: Union[LangChainAIMessageChunk, Dict[str, Any]]) -> str:
        """Extract text content from a LangChain message chunk"""
        if hasattr(chunk, 'content'):
            content = chunk.content
        elif isinstance(chunk, dict) and 'content' in chunk:
            content = chunk['content']
        else:
            return ""
        
        return LangChainAdapter._extract_text_from_content(content)
    
    @staticmethod
    def _extract_text_from_content(content: LangChainMessageContent) -> str:
        """Extract text from LangChain message content"""
        if isinstance(content, str):
            return content
        
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text" and "text" in item:
                        text_parts.append(item["text"])
                elif hasattr(item, 'type') and item.type == "text" and hasattr(item, 'text'):
                    text_parts.append(item.text)
            return "".join(text_parts)
        
        return ""
    
    @staticmethod
    async def from_langchain_llm(
        llm_stream: AsyncGenerator[Any, None],
        callbacks: Optional[StreamCallbacks] = None
    ) -> AsyncGenerator[UIMessageChunk, None]:
        """
        Convert a LangChain LLM stream to AI SDK format.
        
        This is a convenience method for LangChain LLM streams that may not
        follow the standard message chunk format.
        
        Args:
            llm_stream: LangChain LLM stream
            callbacks: Optional callbacks for stream processing
            
        Yields:
            UIMessageChunk: AI SDK compatible message chunks
        """
        async for chunk in LangChainAdapter.to_ui_message_stream(llm_stream, callbacks):
            yield chunk
    
    @staticmethod
    async def from_langchain_runnable(
        runnable_stream: AsyncGenerator[Any, None],
        callbacks: Optional[StreamCallbacks] = None
    ) -> AsyncGenerator[UIMessageChunk, None]:
        """
        Convert a LangChain Runnable stream to AI SDK format.
        
        Args:
            runnable_stream: LangChain Runnable stream
            callbacks: Optional callbacks for stream processing
            
        Yields:
            UIMessageChunk: AI SDK compatible message chunks
        """
        async for chunk in LangChainAdapter.to_ui_message_stream(runnable_stream, callbacks):
            yield chunk


# Convenience functions
async def to_ui_message_stream(
    stream: AsyncGenerator[Union[LangChainStreamEvent, LangChainAIMessageChunk, str], None],
    callbacks: Optional[StreamCallbacks] = None
) -> AsyncGenerator[UIMessageChunk, None]:
    """
    Convert LangChain output streams to AI SDK UI Message Stream.
    
    This is a convenience function that wraps LangChainAdapter.to_ui_message_stream.
    
    Args:
        stream: LangChain stream (message chunks, strings, or events)
        callbacks: Optional callbacks for stream processing
        
    Yields:
        UIMessageChunk: AI SDK compatible message chunks
    """
    async for chunk in LangChainAdapter.to_ui_message_stream(stream, callbacks):
        yield chunk


def create_stream_callbacks(
    on_start: Optional[Callable[[], None]] = None,
    on_text: Optional[Callable[[str], None]] = None,
    on_end: Optional[Callable[[], None]] = None,
    on_error: Optional[Callable[[Exception], None]] = None,
) -> StreamCallbacks:
    """
    Create StreamCallbacks instance.
    
    Args:
        on_start: Called when stream starts
        on_text: Called for each text chunk
        on_end: Called when stream ends
        on_error: Called if an error occurs
        
    Returns:
        StreamCallbacks instance
    """
    return StreamCallbacks(
        on_start=on_start,
        on_text=on_text,
        on_end=on_end,
        on_error=on_error
    )


# Create module-level adapter instance
langchain_adapter = LangChainAdapter()