"""Flask integration for AI SDK Python.

This module provides Flask-specific utilities for building AI-powered web applications
with streaming responses and blueprint integration.
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, Generator, Union, Callable
from functools import wraps

try:
    from flask import Flask, request, Response, Blueprint, jsonify, g
    from werkzeug.exceptions import BadRequest, InternalServerError
    FLASK_AVAILABLE = True
except ImportError:
    Flask = object
    request = object
    Response = object
    Blueprint = object
    jsonify = object
    g = object
    BadRequest = Exception
    InternalServerError = Exception
    FLASK_AVAILABLE = False

from ..providers.base import LanguageModel
from ..providers.types import Message
from ..core.generate_text import stream_text, generate_text
from ..core.generate_object import generate_object, stream_object
from ..schemas import BaseSchema


class AIFlask:
    """Enhanced Flask application with AI SDK integration.
    
    Provides convenient methods for creating AI-powered Flask applications
    with built-in streaming support and middleware integration.
    """
    
    def __init__(self, app: Optional[Flask] = None, default_provider: Optional[LanguageModel] = None):
        if not FLASK_AVAILABLE:
            raise ImportError(
                "Flask is required for AIFlask. "
                "Install it with: pip install flask"
            )
        
        self.app = app or Flask(__name__)
        self.default_provider = default_provider
        
        # Register AI SDK context
        self.app.before_request(self._before_request)
        self.app.after_request(self._after_request)
    
    def _before_request(self):
        """Set up AI SDK context for each request."""
        g.ai_provider = self.default_provider
        g.ai_sdk = {
            'generate_text': generate_text,
            'stream_text': stream_text,
            'generate_object': generate_object,
            'stream_object': stream_object,
        }
    
    def _after_request(self, response):
        """Add AI SDK headers to response."""
        response.headers["x-ai-sdk"] = "python"
        return response
    
    def chat_route(
        self,
        rule: str,
        provider: Optional[LanguageModel] = None,
        system_prompt: Optional[str] = None,
        methods: List[str] = ["POST"]
    ):
        """Decorator to create a chat route.
        
        Args:
            rule: URL rule for the route
            provider: Language model provider (uses default if None)
            system_prompt: Default system prompt
            methods: HTTP methods to support
            
        Example:
            @ai_app.chat_route("/chat")
            def chat():
                data = request.get_json()
                messages = data.get("messages", [])
                
                result = asyncio.run(generate_text(
                    model=g.ai_provider,
                    messages=messages
                ))
                return {"response": result.text}
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    # Set provider context
                    original_provider = g.get('ai_provider')
                    if provider:
                        g.ai_provider = provider
                    elif not g.get('ai_provider'):
                        g.ai_provider = self.default_provider
                    
                    if not g.ai_provider:
                        return jsonify({"error": "No AI provider configured"}), 500
                    
                    # Add system prompt handling
                    if system_prompt and request.is_json:
                        data = request.get_json()
                        messages = data.get("messages", [])
                        if not any(msg.get("role") == "system" for msg in messages):
                            messages.insert(0, {"role": "system", "content": system_prompt})
                            data["messages"] = messages
                    
                    result = func(*args, **kwargs)
                    
                    # Restore original provider
                    g.ai_provider = original_provider
                    
                    return result
                    
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
            
            self.app.add_url_rule(rule, func.__name__, wrapper, methods=methods)
            return func
        return decorator
    
    def streaming_route(
        self,
        rule: str,
        provider: Optional[LanguageModel] = None,
        system_prompt: Optional[str] = None,
        methods: List[str] = ["POST"]
    ):
        """Decorator to create a streaming route.
        
        Args:
            rule: URL rule for the route
            provider: Language model provider
            system_prompt: Default system prompt
            methods: HTTP methods to support
            
        Example:
            @ai_app.streaming_route("/stream")
            def stream_chat():
                data = request.get_json()
                messages = data.get("messages", [])
                
                async def generate():
                    async for chunk in stream_text(model=g.ai_provider, messages=messages):
                        yield chunk.text_delta
                
                return streaming_response_wrapper(generate())
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    # Set provider context
                    model = provider or self.default_provider
                    if not model:
                        return jsonify({"error": "No AI provider configured"}), 500
                    
                    g.ai_provider = model
                    
                    # Add system prompt handling
                    if system_prompt and request.is_json:
                        data = request.get_json()
                        messages = data.get("messages", [])
                        if not any(msg.get("role") == "system" for msg in messages):
                            messages.insert(0, {"role": "system", "content": system_prompt})
                    
                    result = func(*args, **kwargs)
                    return result
                    
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
            
            self.app.add_url_rule(rule, func.__name__, wrapper, methods=methods)
            return func
        return decorator
    
    def object_route(
        self,
        rule: str,
        schema: BaseSchema,
        provider: Optional[LanguageModel] = None,
        methods: List[str] = ["POST"]
    ):
        """Decorator to create a structured object generation route.
        
        Args:
            rule: URL rule for the route
            schema: Schema for object validation
            provider: Language model provider
            methods: HTTP methods to support
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    data = request.get_json()
                    if not data or "prompt" not in data:
                        return jsonify({"error": "Prompt is required"}), 400
                    
                    model = provider or self.default_provider
                    if not model:
                        return jsonify({"error": "No AI provider configured"}), 500
                    
                    g.ai_provider = model
                    g.ai_schema = schema
                    
                    result = func(*args, **kwargs)
                    return result
                    
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
            
            self.app.add_url_rule(rule, func.__name__, wrapper, methods=methods)
            return func
        return decorator


def ai_blueprint(
    name: str,
    import_name: str,
    default_provider: Optional[LanguageModel] = None,
    **kwargs
) -> Blueprint:
    """Create a Flask blueprint with AI SDK integration.
    
    Args:
        name: Blueprint name
        import_name: Blueprint import name
        default_provider: Default AI provider for blueprint routes
        **kwargs: Additional Blueprint arguments
        
    Returns:
        Flask Blueprint with AI SDK integration
        
    Example:
        bp = ai_blueprint("ai", __name__, default_provider=openai_provider)
        
        @bp.route("/chat", methods=["POST"])
        def chat():
            data = request.get_json()
            messages = data["messages"]
            
            result = asyncio.run(generate_text(
                model=g.ai_provider,
                messages=messages
            ))
            return {"response": result.text}
    """
    if not FLASK_AVAILABLE:
        raise ImportError("Flask is required for ai_blueprint")
    
    bp = Blueprint(name, import_name, **kwargs)
    
    @bp.before_request
    def before_request():
        """Set up AI context for blueprint requests."""
        g.ai_provider = default_provider
        g.ai_sdk = {
            'generate_text': generate_text,
            'stream_text': stream_text,
            'generate_object': generate_object,
            'stream_object': stream_object,
        }
    
    return bp


def streaming_response_wrapper(generator: Union[Generator, Callable]) -> Response:
    """Wrap an async generator for Flask streaming response.
    
    Args:
        generator: Async generator or callable that returns one
        
    Returns:
        Flask streaming response
        
    Example:
        async def generate():
            async for chunk in stream_text(model=model, messages=messages):
                yield f"data: {json.dumps({'text': chunk.text_delta})}\\n\\n"
        
        return streaming_response_wrapper(generate())
    """
    if not FLASK_AVAILABLE:
        raise ImportError("Flask is required for streaming_response_wrapper")
    
    def sync_generator():
        """Convert async generator to sync for Flask."""
        if asyncio.iscoroutinefunction(generator):
            # If generator is a coroutine function, run it
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                async_gen = generator()
                while True:
                    try:
                        chunk = loop.run_until_complete(async_gen.__anext__())
                        yield f"data: {json.dumps({'text': chunk})}\n\n"
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()
        else:
            # Assume it's already a sync generator
            for chunk in generator:
                if isinstance(chunk, str):
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
                else:
                    yield chunk
        
        yield "data: [DONE]\n\n"
    
    return Response(
        sync_generator(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


def async_route(func: Callable) -> Callable:
    """Decorator to handle async functions in Flask routes.
    
    Args:
        func: Async function to wrap
        
    Returns:
        Wrapped synchronous function
        
    Example:
        @app.route("/chat", methods=["POST"])
        @async_route
        async def chat():
            result = await generate_text(model=model, messages=messages)
            return {"response": result.text}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(func(*args, **kwargs))
            finally:
                loop.close()
        else:
            return func(*args, **kwargs)
    return wrapper


# Example utility functions
def create_chat_app(provider: LanguageModel, system_prompt: Optional[str] = None) -> Flask:
    """Create a simple Flask chat application.
    
    Args:
        provider: AI provider to use
        system_prompt: Optional system prompt
        
    Returns:
        Configured Flask application
    """
    if not FLASK_AVAILABLE:
        raise ImportError("Flask is required for create_chat_app")
    
    ai_app = AIFlask(default_provider=provider)
    
    @ai_app.chat_route("/chat", system_prompt=system_prompt)
    def chat():
        data = request.get_json()
        messages = data.get("messages", [])
        
        result = asyncio.run(generate_text(
            model=g.ai_provider,
            messages=messages
        ))
        
        return {"response": result.text}
    
    @ai_app.streaming_route("/chat/stream", system_prompt=system_prompt)  
    def stream_chat():
        data = request.get_json()
        messages = data.get("messages", [])
        
        async def generate():
            async for chunk in stream_text(model=g.ai_provider, messages=messages):
                if chunk.text_delta:
                    yield chunk.text_delta
        
        return streaming_response_wrapper(generate)
    
    return ai_app.app