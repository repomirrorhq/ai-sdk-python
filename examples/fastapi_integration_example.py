"""FastAPI Integration Example for AI SDK Python.

This example demonstrates how to build AI-powered FastAPI applications
using the AI SDK's FastAPI integration features.

Features demonstrated:
- Basic chat endpoints
- Streaming responses
- WebSocket chat
- Structured object generation
- Middleware integration
"""

import asyncio
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

# AI SDK imports
from ai_sdk import create_openai, generate_text, stream_text
from ai_sdk.integrations.fastapi import (
    AIFastAPI,
    fastapi_ai_middleware,
    streaming_chat_endpoint,
    websocket_chat_endpoint
)
from ai_sdk.schemas import pydantic_schema

# Pydantic for structured data
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    print("Pydantic not available - some features will be disabled")
    BaseModel = object
    Field = None
    PYDANTIC_AVAILABLE = False


# Example 1: Basic FastAPI app with AI middleware
def create_basic_ai_app():
    """Create a basic FastAPI app with AI SDK middleware."""
    app = FastAPI(title="AI SDK FastAPI Example")
    
    # Initialize AI provider (commented out - requires API key)
    # provider = create_openai()
    # fastapi_ai_middleware(app, default_provider=provider)
    
    @app.post("/chat")
    async def chat(messages: List[Dict[str, str]]):
        """Basic chat endpoint."""
        # In a real app, you'd use: request.state.ai_provider
        # result = await generate_text(model=request.state.ai_provider, messages=messages)
        # return {"response": result.text}
        
        # Demo response
        return {"response": "This is a demo response. Set up your API key to use real AI."}
    
    return app


# Example 2: Advanced AIFastAPI class usage
def create_advanced_ai_app():
    """Create an advanced AI application using AIFastAPI class."""
    
    # Initialize AI provider (commented out - requires API key)  
    # provider = create_openai()
    # ai_app = AIFastAPI(default_provider=provider)
    ai_app = AIFastAPI()  # Demo without provider
    
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
        # In a real implementation:
        # result = await generate_text(model=model, messages=messages)
        # return result.text
        return "Demo chat response"
    
    # Streaming chat endpoint
    @ai_app.streaming_chat_endpoint("/chat/stream")
    async def stream_chat(model, messages):
        """Streaming chat endpoint."""
        # In a real implementation:
        # async for chunk in stream_text(model=model, messages=messages):
        #     yield chunk.text_delta
        
        # Demo streaming
        demo_response = "This is a demo streaming response that shows how text would be streamed."
        for word in demo_response.split():
            yield word + " "
            await asyncio.sleep(0.1)  # Simulate streaming delay
    
    # Object generation endpoint
    if PYDANTIC_AVAILABLE:
        @ai_app.object_endpoint("/recommend/book", schema=pydantic_schema(BookRecommendation))
        async def recommend_book(model, prompt, schema):
            """Generate structured book recommendations."""
            # In a real implementation:
            # result = await generate_object(model=model, prompt=prompt, schema=schema)
            # return result.object
            
            # Demo response
            return {
                "title": "The Python Handbook",
                "author": "AI Assistant",
                "genre": "Programming",
                "rating": 5,
                "summary": "A comprehensive guide to Python programming",
                "why_recommended": "Perfect for learning AI SDK integration"
            }
        
        @ai_app.object_endpoint("/plan/travel", schema=pydantic_schema(TravelPlan))
        async def plan_travel(model, prompt, schema):
            """Generate structured travel plans."""
            return {
                "destination": "Paris, France",
                "duration_days": 7,
                "activities": ["Visit Eiffel Tower", "Louvre Museum", "Seine River cruise"],
                "estimated_budget": 2500.0,
                "best_season": "Spring or Fall"
            }
    
    # WebSocket chat endpoint
    @ai_app.websocket_chat("/ws/chat")
    async def websocket_chat_handler(websocket: WebSocket, model, messages):
        """WebSocket chat handler."""
        # In a real implementation:
        # await websocket_chat_endpoint(websocket, model, messages)
        
        # Demo WebSocket response
        demo_words = ["Hello", "from", "WebSocket", "chat", "endpoint!"]
        for word in demo_words:
            await websocket.send_json({
                "type": "text_delta",
                "text": word + " "
            })
            await asyncio.sleep(0.5)
        
        await websocket.send_json({"type": "done"})
    
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
    """Create complete demo app with HTML client."""
    ai_app = AIFastAPI()
    
    @ai_app.app.get("/")
    async def get_client():
        """Serve HTML client for WebSocket testing."""
        return HTMLResponse(HTML_CLIENT)
    
    @ai_app.chat_endpoint("/api/chat")
    async def api_chat(model, messages):
        return "Demo response from /api/chat endpoint"
    
    @ai_app.streaming_chat_endpoint("/api/chat/stream")
    async def api_stream_chat(model, messages):
        demo_response = "This is a streaming response from the API endpoint."
        for word in demo_response.split():
            yield word + " "
            await asyncio.sleep(0.1)
    
    @ai_app.websocket_chat("/ws/chat")
    async def ws_chat(websocket: WebSocket, model, messages):
        demo_words = ["Hello!", "This", "is", "a", "WebSocket", "demo", "response."]
        for word in demo_words:
            await websocket.send_json({
                "type": "text_delta",
                "text": word + " "
            })
            await asyncio.sleep(0.3)
        await websocket.send_json({"type": "done"})
    
    return ai_app.app


# Main application factory
def create_app(app_type: str = "advanced"):
    """Create the appropriate app type."""
    if app_type == "basic":
        return create_basic_ai_app()
    elif app_type == "advanced":
        return create_advanced_ai_app()
    elif app_type == "custom":
        return create_custom_streaming_app()
    elif app_type == "demo":
        return create_complete_demo_app()
    else:
        return create_advanced_ai_app()


# For uvicorn
app = create_app("demo")


if __name__ == "__main__":
    print("FastAPI AI SDK Integration Examples")
    print("===================================")
    print("\nAvailable apps:")
    print("- basic: Basic FastAPI app with AI middleware")
    print("- advanced: Advanced AIFastAPI class usage") 
    print("- custom: Custom streaming implementation")
    print("- demo: Complete demo with HTML client")
    print("\nTo run:")
    print("uvicorn fastapi_integration_example:app --reload")
    print("\nOr with different app types:")
    print("APP_TYPE=basic uvicorn fastapi_integration_example:app --reload")
    print("\nEndpoints:")
    print("- GET / - HTML client for WebSocket testing")
    print("- POST /api/chat - Basic chat")
    print("- POST /api/chat/stream - Streaming chat")
    print("- WS /ws/chat - WebSocket chat")
    if PYDANTIC_AVAILABLE:
        print("- POST /recommend/book - Structured book recommendations")
        print("- POST /plan/travel - Structured travel planning")
    print("\nNote: Set OPENAI_API_KEY environment variable for real AI responses")