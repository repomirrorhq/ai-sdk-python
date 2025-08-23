"""FastAPI integration for AI SDK Python.

This module provides FastAPI-specific utilities for building AI-powered APIs
with streaming responses, WebSocket support, and middleware integration.
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, AsyncGenerator, Union, Callable
from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI, Request, Response, WebSocket, HTTPException
    from fastapi.responses import StreamingResponse
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.types import ASGIApp
    FASTAPI_AVAILABLE = True
except ImportError:
    FastAPI = object
    Request = object
    Response = object
    WebSocket = object
    HTTPException = Exception
    StreamingResponse = object
    BaseHTTPMiddleware = object
    ASGIApp = object
    FASTAPI_AVAILABLE = False

from ..providers.base import LanguageModel
from ..providers.types import Message
from ..core.generate_text import stream_text, generate_text
from ..core.generate_object import generate_object, stream_object
from ..schemas import BaseSchema


class AIFastAPIMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for AI SDK integration.
    
    Adds common AI functionality like request logging, error handling,
    and provider management.
    """
    
    def __init__(self, app: ASGIApp, default_provider: Optional[LanguageModel] = None):
        if not FASTAPI_AVAILABLE:
            raise ImportError(
                "FastAPI is required for AIFastAPIMiddleware. "
                "Install it with: pip install fastapi"
            )
        
        super().__init__(app)
        self.default_provider = default_provider
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with AI middleware."""
        # Add provider to request state
        if self.default_provider:
            request.state.ai_provider = self.default_provider
        
        # Add AI SDK utilities to request state
        request.state.ai_sdk = {
            'generate_text': generate_text,
            'stream_text': stream_text,
            'generate_object': generate_object,
            'stream_object': stream_object,
        }
        
        response = await call_next(request)
        
        # Add AI SDK headers
        response.headers["x-ai-sdk"] = "python"
        
        return response


class AIFastAPI:
    """Enhanced FastAPI application with AI SDK integration.
    
    Provides convenient methods for creating AI-powered endpoints
    with built-in streaming and WebSocket support.
    """
    
    def __init__(self, app: Optional[FastAPI] = None, default_provider: Optional[LanguageModel] = None):
        if not FASTAPI_AVAILABLE:
            raise ImportError(
                "FastAPI is required for AIFastAPI. "
                "Install it with: pip install fastapi"
            )
        
        self.app = app or FastAPI(title="AI SDK FastAPI App")
        self.default_provider = default_provider
        
        # Add AI middleware
        if default_provider:
            self.app.add_middleware(AIFastAPIMiddleware, default_provider=default_provider)
    
    def chat_endpoint(
        self,
        path: str = "/chat",
        provider: Optional[LanguageModel] = None,
        system_prompt: Optional[str] = None,
        methods: List[str] = ["POST"]
    ):
        """Decorator to create a chat endpoint.
        
        Args:
            path: API endpoint path
            provider: Language model provider (uses default if None)
            system_prompt: Default system prompt
            methods: HTTP methods to support
            
        Example:
            @ai_app.chat_endpoint("/chat")
            async def chat(messages: List[Message]) -> str:
                return await generate_text(
                    model=ai_app.default_provider,
                    messages=messages
                )
        """
        def decorator(func):
            async def wrapper(request: Request):
                try:
                    data = await request.json()
                    messages = data.get("messages", [])
                    
                    # Add system prompt if provided
                    if system_prompt and not any(msg.get("role") == "system" for msg in messages):
                        messages.insert(0, {"role": "system", "content": system_prompt})
                    
                    # Use provided provider or default
                    model = provider or self.default_provider
                    if not model:
                        raise HTTPException(status_code=500, detail="No AI provider configured")
                    
                    # Call the user's function
                    result = await func(model, messages)
                    return {"response": result}
                    
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            
            self.app.add_api_route(path, wrapper, methods=methods)
            return func
        return decorator
    
    def streaming_chat_endpoint(
        self,
        path: str = "/chat/stream", 
        provider: Optional[LanguageModel] = None,
        system_prompt: Optional[str] = None
    ):
        """Decorator to create a streaming chat endpoint.
        
        Args:
            path: API endpoint path
            provider: Language model provider
            system_prompt: Default system prompt
            
        Example:
            @ai_app.streaming_chat_endpoint("/stream")
            async def stream_chat(model, messages):
                async for chunk in stream_text(model=model, messages=messages):
                    yield chunk.text_delta
        """
        def decorator(func):
            async def wrapper(request: Request):
                try:
                    data = await request.json()
                    messages = data.get("messages", [])
                    
                    # Add system prompt if provided
                    if system_prompt and not any(msg.get("role") == "system" for msg in messages):
                        messages.insert(0, {"role": "system", "content": system_prompt})
                    
                    # Use provided provider or default
                    model = provider or self.default_provider
                    if not model:
                        raise HTTPException(status_code=500, detail="No AI provider configured")
                    
                    # Create streaming generator
                    async def generate():
                        async for chunk in func(model, messages):
                            # Format as Server-Sent Events
                            if chunk:
                                yield f"data: {json.dumps({'text': chunk})}\n\n"
                        yield "data: [DONE]\n\n"
                    
                    return StreamingResponse(
                        generate(),
                        media_type="text/event-stream",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                        }
                    )
                    
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            
            self.app.add_api_route(path, wrapper, methods=["POST"])
            return func
        return decorator
    
    def object_endpoint(
        self,
        path: str,
        schema: BaseSchema,
        provider: Optional[LanguageModel] = None,
        methods: List[str] = ["POST"]
    ):
        """Decorator to create a structured object generation endpoint.
        
        Args:
            path: API endpoint path
            schema: Schema for object validation
            provider: Language model provider
            methods: HTTP methods to support
        """
        def decorator(func):
            async def wrapper(request: Request):
                try:
                    data = await request.json()
                    prompt = data.get("prompt", "")
                    
                    if not prompt:
                        raise HTTPException(status_code=400, detail="Prompt is required")
                    
                    model = provider or self.default_provider
                    if not model:
                        raise HTTPException(status_code=500, detail="No AI provider configured")
                    
                    result = await func(model, prompt, schema)
                    return {"object": result}
                    
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            
            self.app.add_api_route(path, wrapper, methods=methods)
            return func
        return decorator
    
    def websocket_chat(self, path: str = "/ws/chat"):
        """Decorator to create a WebSocket chat endpoint.
        
        Args:
            path: WebSocket endpoint path
        """
        def decorator(func):
            async def wrapper(websocket: WebSocket):
                await websocket.accept()
                
                try:
                    while True:
                        # Receive message from client
                        data = await websocket.receive_json()
                        messages = data.get("messages", [])
                        
                        model = self.default_provider
                        if not model:
                            await websocket.send_json({"error": "No AI provider configured"})
                            continue
                        
                        # Stream response back to client
                        await func(websocket, model, messages)
                        
                except Exception as e:
                    await websocket.send_json({"error": str(e)})
                finally:
                    await websocket.close()
            
            self.app.add_websocket_route(path, wrapper)
            return func
        return decorator


# Standalone functions for use without AIFastAPI class
def fastapi_ai_middleware(app: FastAPI, default_provider: Optional[LanguageModel] = None):
    """Add AI SDK middleware to an existing FastAPI app.
    
    Args:
        app: FastAPI application instance
        default_provider: Default AI provider for requests
    """
    app.add_middleware(AIFastAPIMiddleware, default_provider=default_provider)


async def streaming_chat_endpoint(
    messages: List[Message],
    model: LanguageModel,
    system_prompt: Optional[str] = None
) -> StreamingResponse:
    """Create a streaming response for chat messages.
    
    Args:
        messages: List of chat messages
        model: Language model to use
        system_prompt: Optional system prompt
        
    Returns:
        StreamingResponse with Server-Sent Events
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI is required for streaming_chat_endpoint")
    
    # Add system prompt if provided
    if system_prompt and not any(msg.get("role") == "system" for msg in messages):
        messages.insert(0, {"role": "system", "content": system_prompt})
    
    async def generate():
        try:
            async for chunk in stream_text(model=model, messages=messages):
                if chunk.text_delta:
                    yield f"data: {json.dumps({'text': chunk.text_delta})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


async def websocket_chat_endpoint(
    websocket: WebSocket,
    model: LanguageModel,
    messages: List[Message]
):
    """Handle WebSocket chat communication.
    
    Args:
        websocket: WebSocket connection
        model: Language model to use
        messages: List of chat messages
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI is required for websocket_chat_endpoint")
    
    try:
        async for chunk in stream_text(model=model, messages=messages):
            if chunk.text_delta:
                await websocket.send_json({
                    "type": "text_delta",
                    "text": chunk.text_delta
                })
        
        await websocket.send_json({"type": "done"})
        
    except Exception as e:
        await websocket.send_json({
            "type": "error", 
            "error": str(e)
        })