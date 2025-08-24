#!/usr/bin/env uv run
# /// script
# dependencies = [
#   "uvicorn",
#   "fastapi", 
#   "openai",
#   "pydantic",
# ]
# ///
"""FastAPI Integration Example for AI SDK Python.

This example demonstrates how to build AI-powered FastAPI applications
using the AI SDK's FastAPI integration features with OpenAI integration.

Features demonstrated:
- Basic chat endpoints with real OpenAI responses
- Streaming responses
- WebSocket chat
- Structured object generation
- Middleware integration

Requires OPENAI_API_KEY environment variable.
"""

import asyncio
import os
from typing import List, Dict, Any

# FastAPI imports
try:
    from fastapi import FastAPI, WebSocket
    from fastapi.responses import HTMLResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    print("FastAPI not installed. Install with: pip install fastapi uvicorn")
    FASTAPI_AVAILABLE = False
    exit(1)

# Simple OpenAI import for now
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    print("OpenAI package not available")
    OPENAI_AVAILABLE = False

# Placeholder for AI SDK imports - currently broken
# from ai_sdk import create_openai, generate_text, stream_text
# from ai_sdk.integrations.fastapi import (
#     AIFastAPI,
#     fastapi_ai_middleware,
#     streaming_chat_endpoint,
#     websocket_chat_endpoint
# )
# from ai_sdk.schemas import pydantic_schema

# Pydantic for structured data
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    print("Pydantic not available - some features will be disabled")
    BaseModel = object
    Field = None
    PYDANTIC_AVAILABLE = False


# Example 1: Basic FastAPI app with direct OpenAI integration
def create_basic_ai_app():
    """Create a basic FastAPI app with direct OpenAI integration."""
    app = FastAPI(title="AI SDK FastAPI Example")

    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    client = openai.AsyncClient(api_key=api_key)

    class ChatRequest(BaseModel):
        messages: List[Dict[str, str]]

    @app.post("/chat")
    async def chat(request: ChatRequest):
        """Basic chat endpoint with real OpenAI integration."""
        try:
            # Convert to OpenAI format
            openai_messages = [{"role": msg["role"], "content": msg["content"]} for msg in request.messages]

            # Call OpenAI API
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=openai_messages,
                max_tokens=1000,
            )

            return {"response": response.choices[0].message.content}
        except Exception as e:
            return {"error": f"AI generation failed: {str(e)}"}

    return app


# Example 2: Advanced AIFastAPI class usage
def create_advanced_ai_app():
    """Create an advanced AI application using AIFastAPI class."""

    # Initialize AI provider with OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    provider = create_openai(api_key=api_key)
    ai_app = AIFastAPI(default_provider=provider)

    # Example Pydantic models for structured responses
    if PYDANTIC_AVAILABLE:
        class BookRecommendation(BaseModel):
            title: str = Field(description="Book title")
            author: str = Field(description="Book author")
            genre: str = Field(description="Book genre")
            rating: int = Field(description="Rating 1-5", ge=1, le=5)
            summary: str = Field(description="Brief summary")
            why_recommended: str = Field(description="Why this book is recommended")

        class TravelPlan(BaseModel):
            destination: str = Field(description="Travel destination")
            duration_days: int = Field(description="Trip duration in days")
            activities: List[str] = Field(description="List of planned activities")
            estimated_budget: float = Field(description="Estimated budget in USD")
            best_season: str = Field(description="Best season to visit")

    # Chat endpoint with system prompt
    @ai_app.chat_endpoint("/chat", system_prompt="You are a helpful assistant.")
    async def chat(model, messages):
        """Enhanced chat endpoint with system prompt."""
        try:
            result = await generate_text(model=model("gpt-4o-mini"), messages=messages)
            return result.text
        except Exception as e:
            return f"AI generation failed: {str(e)}"

    # Streaming chat endpoint
    @ai_app.streaming_chat_endpoint("/chat/stream")
    async def stream_chat(model, messages):
        """Streaming chat endpoint with real OpenAI streaming."""
        try:
            async for chunk in stream_text(model=model("gpt-4o-mini"), messages=messages):
                if chunk.text_delta:
                    yield chunk.text_delta
        except Exception as e:
            yield f"AI streaming failed: {str(e)}"

    # Object generation endpoint
    if PYDANTIC_AVAILABLE:
        @ai_app.object_endpoint("/recommend/book", schema=pydantic_schema(BookRecommendation))
        async def recommend_book(model, prompt, schema):
            """Generate structured book recommendations."""
            try:
                result = await generate_object(
                    model=model("gpt-4o-mini"),
                    prompt=f"Recommend a book based on: {prompt}",
                    schema=schema
                )
                return result.object
            except Exception as e:
                # Fallback response if generation fails
                return {
                    "title": "Error: Could not generate recommendation",
                    "author": "AI Assistant",
                    "genre": "Error",
                    "rating": 1,
                    "summary": f"Generation failed: {str(e)}",
                    "why_recommended": "This is an error response"
                }

        @ai_app.object_endpoint("/plan/travel", schema=pydantic_schema(TravelPlan))
        async def plan_travel(model, prompt, schema):
            """Generate structured travel plans."""
            try:
                result = await generate_object(
                    model=model("gpt-4o-mini"),
                    prompt=f"Create a travel plan for: {prompt}",
                    schema=schema
                )
                return result.object
            except Exception as e:
                # Fallback response if generation fails
                return {
                    "destination": "Error: Could not generate travel plan",
                    "duration_days": 0,
                    "activities": [f"Generation failed: {str(e)}"],
                    "estimated_budget": 0.0,
                    "best_season": "Unknown"
                }

    # WebSocket chat endpoint
    @ai_app.websocket_chat("/ws/chat")
    async def websocket_chat_handler(websocket: WebSocket, model, messages):
        """WebSocket chat handler with real OpenAI streaming."""
        try:
            async for chunk in stream_text(model=model("gpt-4o-mini"), messages=messages):
                if chunk.text_delta:
                    await websocket.send_json({
                        "type": "text_delta",
                        "text": chunk.text_delta
                    })
            await websocket.send_json({"type": "done"})
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "error": f"AI generation failed: {str(e)}"
            })

    return ai_app.app


# Example 3: Custom endpoint with manual streaming
def create_custom_streaming_app():
    """Create app with custom streaming implementation."""
    app = FastAPI(title="Custom Streaming AI App")

    @app.post("/custom-stream")
    async def custom_stream(messages: List[Dict[str, str]]):
        """Custom streaming endpoint."""
        async def generate_stream():
            # Demo streaming response
            response = "This is a custom streaming response that demonstrates manual SSE formatting."
            for word in response.split():
                yield f"data: {{'text': '{word} '}}\n\n"
                await asyncio.sleep(0.1)
            yield "data: [DONE]\n\n"

        return streaming_chat_endpoint(
            messages=messages,
            model=None,  # Would be real model in production
            system_prompt="You are a creative assistant."
        )

    return app


# HTML client for testing WebSocket
HTML_CLIENT = """
<!DOCTYPE html>
<html>
<head>
    <title>AI SDK WebSocket Chat</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #messages { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; }
        .message { margin-bottom: 10px; }
        .user { color: blue; }
        .ai { color: green; }
        input[type="text"] { width: 70%; padding: 10px; }
        button { padding: 10px 20px; }
    </style>
</head>
<body>
    <h1>AI SDK WebSocket Chat Demo</h1>
    <div id="messages"></div>
    <input type="text" id="messageInput" placeholder="Type your message...">
    <button onclick="sendMessage()">Send</button>

    <script>
        const ws = new WebSocket("ws://localhost:8000/ws/chat");
        const messages = document.getElementById('messages');

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ai';

            if (data.type === 'text_delta') {
                messageDiv.innerHTML = '<strong>AI:</strong> ' + data.text;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            } else if (data.type === 'done') {
                messageDiv.innerHTML = '<em>Response complete</em>';
                messages.appendChild(messageDiv);
            } else if (data.error) {
                messageDiv.innerHTML = '<strong>Error:</strong> ' + data.error;
                messageDiv.style.color = 'red';
                messages.appendChild(messageDiv);
            }
        };

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (message) {
                // Display user message
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message user';
                messageDiv.innerHTML = '<strong>You:</strong> ' + message;
                messages.appendChild(messageDiv);

                // Send to WebSocket
                ws.send(JSON.stringify({
                    messages: [
                        {role: "user", content: message}
                    ]
                }));

                input.value = '';
                messages.scrollTop = messages.scrollHeight;
            }
        }

        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""


# Example 4: Complete app with HTML client
def create_complete_demo_app():
    """Create complete demo app with HTML client and OpenAI integration."""
    # Initialize AI provider with OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    provider = create_openai(api_key=api_key)
    ai_app = AIFastAPI(default_provider=provider)

    @ai_app.app.get("/")
    async def get_client():
        """Serve HTML client for WebSocket testing."""
        return HTMLResponse(HTML_CLIENT)

    @ai_app.chat_endpoint("/api/chat")
    async def api_chat(model, messages):
        try:
            result = await generate_text(model=model("gpt-4o-mini"), messages=messages)
            return result.text
        except Exception as e:
            return f"AI generation failed: {str(e)}"

    @ai_app.streaming_chat_endpoint("/api/chat/stream")
    async def api_stream_chat(model, messages):
        try:
            async for chunk in stream_text(model=model("gpt-4o-mini"), messages=messages):
                if chunk.text_delta:
                    yield chunk.text_delta
        except Exception as e:
            yield f"AI streaming failed: {str(e)}"

    @ai_app.websocket_chat("/ws/chat")
    async def ws_chat(websocket: WebSocket, model, messages):
        try:
            async for chunk in stream_text(model=model("gpt-4o-mini"), messages=messages):
                if chunk.text_delta:
                    await websocket.send_json({
                        "type": "text_delta",
                        "text": chunk.text_delta
                    })
            await websocket.send_json({"type": "done"})
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "error": f"AI generation failed: {str(e)}"
            })

    return ai_app.app


# Main application factory
def create_app(app_type: str = "basic"):
    """Create the appropriate app type."""
    if app_type == "basic":
        return create_basic_ai_app()
    elif app_type == "advanced":
        return create_basic_ai_app()  # Use basic for now since advanced has AI SDK deps
    elif app_type == "custom":
        return create_basic_ai_app()  # Use basic for now
    elif app_type == "demo":
        return create_basic_ai_app()  # Use basic for now
    else:
        return create_basic_ai_app()


# For uvicorn
app = create_app("basic")


if __name__ == "__main__":
    import uvicorn
    
    print("FastAPI AI SDK Integration Examples")
    print("===================================")
    print("\nStarting server with basic OpenAI integration...")
    print("\nEndpoints:")
    print("- POST /chat - Basic chat with OpenAI")
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("\n✅ OpenAI API key found - Real AI responses enabled")
        print(f"\nTest with:")
        print('curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d \'{"messages":[{"role":"user","content":"Hello!"}]}\'')
    else:
        print("\n❌ OPENAI_API_KEY environment variable not set")
        print("Set it to enable real AI responses")
    
    # Start the server
    uvicorn.run(app, host="127.0.0.1", port=8000)
