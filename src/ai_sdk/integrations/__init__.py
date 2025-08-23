"""Framework integrations for AI SDK Python.

This module provides integrations with popular Python web frameworks
to make it easier to build AI-powered web applications.
"""

# FastAPI integration (always available)
from .fastapi import fastapi_ai_middleware, AIFastAPI, streaming_chat_endpoint, websocket_chat_endpoint

# Flask integration (always available)
from .flask import AIFlask, ai_blueprint, streaming_response_wrapper

__all__ = [
    # FastAPI
    "fastapi_ai_middleware",
    "AIFastAPI",
    "streaming_chat_endpoint",
    "websocket_chat_endpoint",
    
    # Flask
    "AIFlask", 
    "ai_blueprint",
    "streaming_response_wrapper",
]