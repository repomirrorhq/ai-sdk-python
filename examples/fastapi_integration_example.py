#!/usr/bin/env uv run
# /// script
# dependencies = [
#   "uvicorn",
#   "fastapi",
#   "pydantic",
# ]
# ///
"""FastAPI Integration Example for AI SDK Python.

This example demonstrates the essential AI SDK FastAPI integration features:
- Text generation with streaming
- Structured object generation  
- Tool calling
- WebSocket chat
- Comprehensive AI SDK integration

Requires OPENAI_API_KEY environment variable.
"""

import os
from typing import List, Dict, Any, Optional

# FastAPI imports
try:
    from fastapi import FastAPI, WebSocket, HTTPException, Request
    from fastapi.responses import HTMLResponse, StreamingResponse
    from fastapi.websockets import WebSocketDisconnect
except ImportError:
    print("FastAPI not installed. Install with: pip install fastapi uvicorn")
    exit(1)

# AI SDK imports
try:
    from ai_sdk.providers.openai import create_openai
    from ai_sdk.core.generate_text import generate_text, stream_text
    from ai_sdk.core.generate_object import generate_object
    from ai_sdk.integrations.fastapi import AIFastAPI
    from ai_sdk.schemas.pydantic import pydantic_schema
    from ai_sdk.tools.core import tool
    from ai_sdk.providers.types import Message
except ImportError as e:
    print(f"AI SDK import error: {e}")
    print("Make sure ai_sdk is installed and available")
    exit(1)

# Pydantic for structured data
from pydantic import BaseModel, Field


# Core AI SDK models
class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o-mini"

class BookRequest(BaseModel):
    preferences: str

class BookRecommendation(BaseModel):
    title: str = Field(description="Book title")
    author: str = Field(description="Book author")
    genre: str = Field(description="Book genre")
    rating: int = Field(description="Rating 1-5", ge=1, le=5)
    summary: str = Field(description="Brief summary")
    why_recommended: str = Field(description="Why this book is recommended")


# AI SDK Tools
@tool("get_weather", "Get current weather for a location")
def get_weather(location: str) -> str:
    """Mock weather tool for demonstration."""
    return f"The weather in {location} is sunny with 72°F temperature."

@tool("calculate", "Perform mathematical calculations")
def calculate(expression: str) -> str:
    """Safe calculator for basic math."""
    try:
        # Simple safe evaluation (production would need more security)
        result = eval(expression.replace(' ', ''))  # Simplified for demo
        return f"Result: {result}"
    except:
        return "Invalid mathematical expression"


# Main AI SDK FastAPI Application
def create_ai_app():
    """Create comprehensive AI application using AIFastAPI."""
    # Initialize AI provider
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    provider = create_openai(api_key=api_key)
    
    # Create AIFastAPI app with default provider
    ai_app = AIFastAPI(default_provider=provider)

    # Basic chat endpoint
    @ai_app.app.post("/chat")
    async def chat(request: ChatRequest):
        """Basic chat endpoint using AI SDK."""
        try:
            messages = [Message(role="user", content=request.message)]
            result = await generate_text(
                model=provider(request.model),
                messages=messages,
                max_tokens=1000,
            )
            return {"response": result.text}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

    # Streaming chat endpoint
    @ai_app.app.post("/chat/stream")
    async def stream_chat(request: ChatRequest):
        """Streaming chat endpoint using AI SDK."""
        try:
            messages = [Message(role="user", content=request.message)]
            
            async def generate():
                async for chunk in stream_text(
                    model=provider(request.model),
                    messages=messages,
                    max_tokens=1000,
                ):
                    if chunk.text_delta:
                        yield f'data: {{"text": "{chunk.text_delta}"}}\n\n'
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
            raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")

    # Tool-enabled chat endpoint
    @ai_app.app.post("/chat/tools")
    async def chat_with_tools(request: ChatRequest):
        """Chat endpoint with tool calling support."""
        try:
            messages = [Message(role="user", content=request.message)]
            result = await generate_text(
                model=provider(request.model),
                messages=messages,
                tools=[get_weather, calculate],
                max_tokens=1500
            )
            return {"response": result.text}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Tool chat failed: {str(e)}")

    # Structured object generation
    @ai_app.app.post("/recommend/book")
    async def recommend_book(request: BookRequest):
        """Generate structured book recommendations."""
        try:
            result = await generate_object(
                model=provider("gpt-4o-mini"),
                prompt=f"Recommend a book based on: {request.preferences}",
                schema=pydantic_schema(BookRecommendation)
            )
            return {"book": result.object}
        except Exception as e:
            # Fallback response if generation fails
            return {
                "book": {
                    "title": "The Pragmatic Programmer",
                    "author": "David Thomas and Andrew Hunt",
                    "genre": "Technology",
                    "rating": 5,
                    "summary": "Essential guide for software developers with practical advice and techniques.",
                    "why_recommended": f"Fallback recommendation due to error: {str(e)}"
                }
            }

    # WebSocket chat endpoint
    @ai_app.app.websocket("/ws/chat")
    async def websocket_chat(websocket: WebSocket):
        """Real-time WebSocket chat."""
        await websocket.accept()
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_json()
                message = data.get("message", "")
                
                if message:
                    messages = [Message(role="user", content=message)]
                    
                    # Stream response back
                    async for chunk in stream_text(
                        model=provider("gpt-4o-mini"),
                        messages=messages,
                        tools=[get_weather, calculate]
                    ):
                        if chunk.text_delta:
                            await websocket.send_json({
                                "type": "text_delta",
                                "text": chunk.text_delta
                            })
                    
                    await websocket.send_json({"type": "done"})
                    
        except WebSocketDisconnect:
            pass
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })

    # Health check endpoint
    @ai_app.app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "ai_sdk": "python",
            "provider": "openai",
            "features": [
                "chat",
                "streaming",
                "websocket",
                "object_generation",
                "tool_calling"
            ]
        }
    
    # List available tools endpoint
    @ai_app.app.get("/tools")
    async def list_tools():
        """List available tools."""
        return {
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Get current weather for a location",
                    "parameters": ["location"]
                },
                {
                    "name": "calculate",
                    "description": "Perform mathematical calculations", 
                    "parameters": ["expression"]
                }
            ]
        }

    return ai_app


# Enhanced demonstration HTML interface
def get_demo_html():
    """Simple HTML interface for testing AI SDK features."""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI SDK FastAPI Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .chat-area { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 15px; margin: 15px 0; background: #fafafa; border-radius: 5px; }
            .input-area { display: flex; gap: 10px; margin: 15px 0; align-items: center; }
            input, button, select { padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            input[type="text"] { flex: 1; }
            button { background: #007bff; color: white; cursor: pointer; border: none; }
            button:hover { background: #0056b3; }
            .response { background: #e9ecef; padding: 15px; margin: 8px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .user-msg { background: #d4edda; border-left-color: #28a745; }
            .error { background: #f8d7da; border-left-color: #dc3545; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI SDK FastAPI Demo</h1>
            <p>Test all AI SDK FastAPI integration features.</p>
            
            <div class="chat-area" id="chatArea"></div>
            
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Ask me anything..." />
                <select id="endpointSelect">
                    <option value="/chat">Basic Chat</option>
                    <option value="/chat/stream">Streaming Chat</option>
                    <option value="/chat/tools">Chat with Tools</option>
                </select>
                <button onclick="sendMessage()">Send</button>
            </div>
            
            <div class="input-area">
                <input type="text" id="bookInput" placeholder="What kind of book?" />
                <button onclick="getBookRecommendation()">📚 Get Book</button>
            </div>
            
            <button onclick="checkHealth()">💚 Health Check</button>
            <button onclick="listTools()">🔧 List Tools</button>
        </div>
        
        <script>
            function addToChatArea(content, className = 'response') {
                const chatArea = document.getElementById('chatArea');
                chatArea.innerHTML += '<div class="' + className + '">' + content + '</div>';
                chatArea.scrollTop = chatArea.scrollHeight;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const endpoint = document.getElementById('endpointSelect').value;
                const message = input.value.trim();
                if (!message) return;
                
                addToChatArea('<strong>You:</strong> ' + message, 'user-msg');
                input.value = '';
                
                try {
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    
                    if (endpoint === '/chat/stream') {
                        const reader = response.body.getReader();
                        let streamContent = '<strong>🤖 AI:</strong> ';
                        
                        while (true) {
                            const { done, value } = await reader.read();
                            if (done) break;
                            
                            const chunk = new TextDecoder().decode(value);
                            const lines = chunk.split('\\n');
                            
                            for (const line of lines) {
                                if (line.startsWith('data: ')) {
                                    const data = line.slice(6);
                                    if (data === '[DONE]') {
                                        addToChatArea(streamContent);
                                        return;
                                    }
                                    try {
                                        const parsed = JSON.parse(data);
                                        if (parsed.text) {
                                            streamContent += parsed.text;
                                        }
                                    } catch (e) {}
                                }
                            }
                        }
                    } else {
                        const data = await response.json();
                        addToChatArea('<strong>🤖 AI:</strong> ' + (data.response || data.error || 'No response'));
                    }
                } catch (error) {
                    addToChatArea('<strong>Error:</strong> ' + error.message, 'error');
                }
            }
            
            async function getBookRecommendation() {
                const input = document.getElementById('bookInput');
                const preferences = input.value.trim();
                if (!preferences) return;
                
                addToChatArea('<strong>You:</strong> Book for: ' + preferences, 'user-msg');
                
                try {
                    const response = await fetch('/recommend/book', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ preferences: preferences })
                    });
                    
                    const data = await response.json();
                    const book = data.book;
                    addToChatArea(
                        '<strong>📚 Book Recommendation:</strong><br/>' +
                        '<strong>Title:</strong> ' + book.title + '<br/>' +
                        '<strong>Author:</strong> ' + book.author + '<br/>' +
                        '<strong>Genre:</strong> ' + book.genre + '<br/>' +
                        '<strong>Rating:</strong> ' + book.rating + '/5⭐<br/>' +
                        '<strong>Summary:</strong> ' + book.summary + '<br/>' +
                        '<strong>Why:</strong> ' + book.why_recommended
                    );
                } catch (error) {
                    addToChatArea('<strong>Error:</strong> ' + error.message, 'error');
                }
            }
            
            async function checkHealth() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    addToChatArea('<strong>🟢 Health:</strong> ' + data.status + ', Features: ' + data.features.join(', '));
                } catch (error) {
                    addToChatArea('<strong>🔴 Error:</strong> ' + error.message, 'error');
                }
            }
            
            async function listTools() {
                try {
                    const response = await fetch('/tools');
                    const data = await response.json();
                    let toolsHtml = '<strong>🔧 Available Tools:</strong><br/>';
                    data.tools.forEach(tool => {
                        toolsHtml += '<strong>' + tool.name + ':</strong> ' + tool.description + '<br/>';
                    });
                    addToChatArea(toolsHtml);
                } catch (error) {
                    addToChatArea('<strong>Error:</strong> ' + error.message, 'error');
                }
            }
            
            // Auto-focus message input and enable Enter key
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Load health check on page load
            window.onload = function() {
                checkHealth();
            };
        </script>
    </body>
    </html>
    """)


# Main application setup
def main():
    """Main function to run the FastAPI application with AI SDK features."""
    print("🤖 AI SDK FastAPI Integration Example")
    print("=====================================")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable is required")
        print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        # Create AI application
        ai_app = create_ai_app()
        print("✅ Created AI SDK FastAPI application")
        
        # Add demo HTML endpoint
        @ai_app.app.get("/")
        async def root():
            return get_demo_html()
        
        print("🎉 AI SDK FastAPI Application ready!")
        print("\n📋 Available endpoints:")
        print("  GET  /          - 🌐 Interactive demo interface")
        print("  GET  /health    - 💚 Health check")
        print("  GET  /tools     - 🔧 List available tools")
        print("  POST /chat      - 💬 Basic chat")
        print("  POST /chat/stream - ⚡ Streaming chat")
        print("  POST /chat/tools - 🛠️ Chat with tools")
        print("  POST /recommend/book - 📚 Book recommendations")
        print("  WS   /ws/chat   - 🔄 WebSocket chat")
        
        print("\n🌐 Starting server on http://localhost:8000")
        print("📖 Open http://localhost:8000 in your browser for the interactive demo")
        print("\n💡 Features demonstrated:")
        print("  ✅ AI SDK integration with FastAPI")
        print("  ✅ Text generation and streaming")
        print("  ✅ Tool calling (weather, calculator)")
        print("  ✅ Structured object generation")
        print("  ✅ WebSocket real-time chat")
        
        # Run the server
        try:
            import uvicorn
            uvicorn.run(
                ai_app.app, 
                host="0.0.0.0", 
                port=8000, 
                reload=True,
                log_level="info"
            )
        except ImportError:
            print("❌ uvicorn not available. Install with: pip install uvicorn")
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        print("💡 Troubleshooting:")
        print("  1. Check OPENAI_API_KEY is set correctly")
        print("  2. Ensure all dependencies are installed")
        print("  3. Verify ai_sdk package is available")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting AI SDK FastAPI Integration Example...")
    main()