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


# Example 1: Basic FastAPI app with AI SDK integration
def create_basic_ai_app():
    """Create a basic FastAPI app with AI SDK integration."""
    app = FastAPI(title="AI SDK FastAPI Example")

    # Initialize AI provider
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    provider = create_openai(api_key=api_key)

    class ChatRequest(BaseModel):
        messages: List[Dict[str, str]]
        model: str = "gpt-4o-mini"

    @app.post("/chat")
    async def chat(request: ChatRequest):
        """Basic chat endpoint using AI SDK."""
        try:
            # Convert to Message format
            messages = [Message(role=msg["role"], content=msg["content"]) for msg in request.messages]

            # Use AI SDK generate_text
            result = await generate_text(
                model=provider(request.model),
                messages=messages,
                max_tokens=1000,
            )

            return {"response": result.text}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

    @app.post("/chat/stream")
    async def stream_chat(request: ChatRequest):
        """Streaming chat endpoint using AI SDK."""
        try:
            messages = [Message(role=msg["role"], content=msg["content"]) for msg in request.messages]
            
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

    return app


# Example 2: Advanced AIFastAPI class usage with complete AI SDK features
def create_advanced_ai_app():
    """Create an advanced AI application using AIFastAPI class."""
    
    if not AI_SDK_AVAILABLE:
        print("AI SDK not available - cannot create advanced app")
        return create_basic_ai_app()

    # Initialize AI provider
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
        
        class TaskAnalysis(BaseModel):
            task_type: str = Field(description="Type of task (research, calculation, analysis, etc.)")
            complexity: int = Field(description="Task complexity 1-10", ge=1, le=10)
            steps_needed: List[str] = Field(description="List of steps to complete the task")
            tools_required: List[str] = Field(description="Tools or resources needed")
            estimated_time: str = Field(description="Estimated completion time")

    # Enhanced tools for agent workflows
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

    # Chat endpoint with system prompt
    @ai_app.chat_endpoint("/chat", system_prompt="You are a helpful AI assistant with access to tools for weather and calculations.")
    async def chat(model, messages):
        """Enhanced chat endpoint with tool support."""
        try:
            result = await generate_text(
                model=model("gpt-4o-mini"), 
                messages=messages,
                tools=[get_weather, calculate],
                max_tokens=1500
            )
            return result.text
        except Exception as e:
            return f"AI generation failed: {str(e)}"

    # Streaming chat endpoint
    @ai_app.streaming_chat_endpoint("/chat/stream")
    async def stream_chat(model, messages):
        """Streaming chat endpoint with AI SDK."""
        try:
            async for chunk in stream_text(
                model=model("gpt-4o-mini"), 
                messages=messages,
                tools=[get_weather, calculate]
            ):
                if chunk.text_delta:
                    yield chunk.text_delta
        except Exception as e:
            yield f"AI streaming failed: {str(e)}"

    # Object generation endpoints
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
                    "title": "The Pragmatic Programmer",
                    "author": "David Thomas and Andrew Hunt",
                    "genre": "Technology",
                    "rating": 5,
                    "summary": "Essential guide for software developers with practical advice and techniques.",
                    "why_recommended": f"Fallback recommendation due to error: {str(e)}"
                }

        @ai_app.object_endpoint("/plan/travel", schema=pydantic_schema(TravelPlan))
        async def plan_travel(model, prompt, schema):
            """Generate structured travel plans."""
            try:
                result = await generate_object(
                    model=model("gpt-4o-mini"),
                    prompt=f"Create a detailed travel plan for: {prompt}",
                    schema=schema,
                    tools=[get_weather]
                )
                return result.object
            except Exception as e:
                # Fallback response if generation fails
                return {
                    "destination": "Local Area",
                    "duration_days": 3,
                    "activities": ["Explore local attractions", "Visit museums", "Try local cuisine"],
                    "estimated_budget": 500.0,
                    "best_season": "Spring or Fall"
                }
        
        @ai_app.object_endpoint("/analyze/task", schema=pydantic_schema(TaskAnalysis))
        async def analyze_task(model, prompt, schema):
            """Analyze and break down complex tasks."""
            try:
                result = await generate_object(
                    model=model("gpt-4o-mini"),
                    prompt=f"Analyze this task and break it down: {prompt}",
                    schema=schema
                )
                return result.object
            except Exception as e:
                return {
                    "task_type": "unknown",
                    "complexity": 5,
                    "steps_needed": ["Review requirements", "Plan approach", "Execute", "Review results"],
                    "tools_required": ["Analysis tools"],
                    "estimated_time": "2-4 hours"
                }

    # WebSocket chat endpoint with enhanced features
    @ai_app.websocket_chat("/ws/chat")
    async def websocket_chat(websocket: WebSocket, model, messages):
        """Real-time WebSocket chat with tool support."""
        try:
            async for chunk in stream_text(
                model=model("gpt-4o-mini"), 
                messages=messages,
                tools=[get_weather, calculate]
            ):
                if chunk.text_delta:
                    await websocket.send_json({
                        "type": "text_delta",
                        "text": chunk.text_delta
                    })
                elif hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    # Send tool call information
                    for tool_call in chunk.tool_calls:
                        await websocket.send_json({
                            "type": "tool_call",
                            "tool_name": tool_call.tool_name,
                            "args": tool_call.args
                        })
            
            await websocket.send_json({"type": "done"})
            
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
            "ai_sdk": "available",
            "provider": "openai",
            "features": [
                "chat",
                "streaming",
                "websocket",
                "object_generation",
                "tool_calling"
            ]
        }
    
    # Get available tools endpoint
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


# Example 3: Standalone FastAPI app with middleware
def create_middleware_ai_app():
    """Create FastAPI app using AI middleware approach."""
    app = FastAPI(title="AI Middleware Example")
    
    if AI_SDK_AVAILABLE:
        # Initialize provider
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            provider = create_openai(api_key=api_key)
            # Add AI middleware to existing app
            fastapi_ai_middleware(app, default_provider=provider)
    
    class ChatRequest(BaseModel):
        message: str
        model: Optional[str] = "gpt-4o-mini"
        stream: bool = False
    
    @app.post("/middleware-chat")
    async def middleware_chat(request: ChatRequest, req: Request):
        """Chat endpoint using middleware-provided AI functionality."""
        try:
            # Access AI provider from request state
            if hasattr(req.state, 'ai_provider'):
                model = req.state.ai_provider(request.model)
                messages = [Message(role="user", content=request.message)]
                
                if request.stream:
                    async def generate():
                        async for chunk in stream_text(model=model, messages=messages):
                            if chunk.text_delta:
                                yield f'data: {{"text": "{chunk.text_delta}"}}\n\n'
                        yield "data: [DONE]\n\n"
                    
                    return StreamingResponse(
                        generate(),
                        media_type="text/event-stream"
                    )
                else:
                    result = await generate_text(model=model, messages=messages)
                    return {"response": result.text}
            else:
                raise HTTPException(status_code=500, detail="AI provider not available")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
    
    # Multi-provider support example
    @app.post("/multi-provider-chat")
    async def multi_provider_chat(request: ChatRequest, req: Request):
        """Demonstrate multiple provider support."""
        try:
            # Initialize different providers based on request
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise HTTPException(status_code=500, detail="OPENAI_API_KEY required")
            
            provider = create_openai(api_key=api_key)
            model = provider(request.model)
            messages = [Message(role="user", content=request.message)]
            
            result = await generate_text(model=model, messages=messages)
            return {
                "response": result.text,
                "provider": "openai",
                "model_used": request.model
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Multi-provider chat failed: {str(e)}")
    
    return app


# Example 4: Enhanced demonstration HTML interface
def get_demo_html():
    """Enhanced HTML interface for testing all AI SDK features."""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI SDK FastAPI Demo - Complete Features</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .chat-area { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 15px; margin: 15px 0; background: #fafafa; border-radius: 5px; }
            .input-area { display: flex; gap: 10px; margin: 15px 0; align-items: center; }
            input, button, select { padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            input[type="text"] { flex: 1; }
            button { background: #007bff; color: white; cursor: pointer; border: none; }
            button:hover { background: #0056b3; }
            .response { background: #e9ecef; padding: 15px; margin: 8px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .user-msg { background: #d4edda; border-left-color: #28a745; }
            .error { background: #f8d7da; border-left-color: #dc3545; }
            .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            h3 { color: #495057; margin-top: 0; }
            .feature-tabs { display: flex; gap: 10px; margin: 20px 0; }
            .tab { padding: 10px 20px; background: #e9ecef; border: none; cursor: pointer; border-radius: 4px; }
            .tab.active { background: #007bff; color: white; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI SDK FastAPI Demo - Complete Features</h1>
            <p>This demo showcases the full capabilities of AI SDK Python with FastAPI integration.</p>
            
            <div class="feature-tabs">
                <button class="tab active" onclick="showTab('chat')">💬 Chat</button>
                <button class="tab" onclick="showTab('objects')">📊 Objects</button>
                <button class="tab" onclick="showTab('tools')">🔧 Tools</button>
                <button class="tab" onclick="showTab('streaming')">⚡ Streaming</button>
            </div>
            
            <div class="chat-area" id="chatArea"></div>
            
            <!-- Chat Tab -->
            <div id="chat-tab" class="tab-content active">
                <div class="section">
                    <h3>💬 Chat Features</h3>
                    <div class="input-area">
                        <input type="text" id="messageInput" placeholder="Ask me anything..." />
                        <select id="modelSelect">
                            <option value="gpt-4o-mini">GPT-4o Mini</option>
                            <option value="gpt-4o">GPT-4o</option>
                            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                        </select>
                        <select id="endpointSelect">
                            <option value="/chat">Basic Chat</option>
                            <option value="/chat/stream">Streaming Chat</option>
                            <option value="/middleware-chat">Middleware Chat</option>
                        </select>
                        <button onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
            
            <!-- Objects Tab -->
            <div id="objects-tab" class="tab-content">
                <div class="section">
                    <h3>📊 Structured Object Generation</h3>
                    <div class="input-area">
                        <input type="text" id="bookInput" placeholder="What kind of book are you looking for?" />
                        <button onclick="getBookRecommendation()">📚 Get Book</button>
                    </div>
                    <div class="input-area">
                        <input type="text" id="travelInput" placeholder="Where would you like to travel?" />
                        <button onclick="getTravelPlan()">✈️ Plan Travel</button>
                    </div>
                    <div class="input-area">
                        <input type="text" id="taskInput" placeholder="Describe a task to analyze..." />
                        <button onclick="analyzeTask()">🎯 Analyze Task</button>
                    </div>
                </div>
            </div>
            
            <!-- Tools Tab -->
            <div id="tools-tab" class="tab-content">
                <div class="section">
                    <h3>🔧 AI Tools & Functions</h3>
                    <div class="input-area">
                        <input type="text" id="weatherInput" placeholder="Enter a city name..." />
                        <button onclick="getWeather()">🌤️ Get Weather</button>
                    </div>
                    <div class="input-area">
                        <input type="text" id="calcInput" placeholder="Enter math expression (e.g., 2+2*3)" />
                        <button onclick="calculate()">🔢 Calculate</button>
                    </div>
                    <button onclick="listTools()">📋 List Available Tools</button>
                </div>
            </div>
            
            <!-- Streaming Tab -->
            <div id="streaming-tab" class="tab-content">
                <div class="section">
                    <h3>⚡ Real-time Streaming</h3>
                    <div class="input-area">
                        <input type="text" id="streamInput" placeholder="Start a streaming conversation..." />
                        <button onclick="startStream()">▶️ Start Stream</button>
                        <button onclick="stopStream()" disabled id="stopBtn">⏹️ Stop</button>
                    </div>
                    <p><small>Streaming responses appear in real-time in the chat area above.</small></p>
                </div>
            </div>
            
            <div class="section">
                <h3>🔍 API Status</h3>
                <button onclick="checkHealth()">💚 Health Check</button>
                <div id="statusArea"></div>
            </div>
        </div>
        
        <script>
            let streamController = null;
            
            function showTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Show selected tab
                document.getElementById(tabName + '-tab').classList.add('active');
                event.target.classList.add('active');
            }
            
            function addToChatArea(content, className = 'response') {
                const chatArea = document.getElementById('chatArea');
                chatArea.innerHTML += '<div class="' + className + '">' + content + '</div>';
                chatArea.scrollTop = chatArea.scrollHeight;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const model = document.getElementById('modelSelect').value;
                const endpoint = document.getElementById('endpointSelect').value;
                const message = input.value.trim();
                if (!message) return;
                
                addToChatArea('<strong>You:</strong> ' + message, 'user-msg');
                input.value = '';
                
                try {
                    const payload = endpoint === '/middleware-chat' 
                        ? { message: message, model: model }
                        : { messages: [{role: 'user', content: message}], model: model };
                    
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    
                    const data = await response.json();
                    addToChatArea('<strong>AI (' + model + '):</strong> ' + (data.response || data.error || 'No response'));
                } catch (error) {
                    addToChatArea('<strong>Error:</strong> ' + error.message, 'error');
                }
            }
            
            async function getBookRecommendation() {
                const input = document.getElementById('bookInput');
                const prompt = input.value.trim();
                if (!prompt) return;
                
                addToChatArea('<strong>You:</strong> Book recommendation for: ' + prompt, 'user-msg');
                
                try {
                    const response = await fetch('/recommend/book', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: prompt })
                    });
                    
                    const data = await response.json();
                    const book = data.object;
                    addToChatArea(
                        '<strong>📚 Book Recommendation:</strong><br/>' +
                        '<strong>Title:</strong> ' + book.title + '<br/>' +
                        '<strong>Author:</strong> ' + book.author + '<br/>' +
                        '<strong>Genre:</strong> ' + book.genre + '<br/>' +
                        '<strong>Rating:</strong> ' + book.rating + '/5⭐<br/>' +
                        '<strong>Summary:</strong> ' + book.summary + '<br/>' +
                        '<strong>Why Recommended:</strong> ' + book.why_recommended
                    );
                } catch (error) {
                    addToChatArea('<strong>Error:</strong> ' + error.message, 'error');
                }
            }
            
            async function getTravelPlan() {
                const input = document.getElementById('travelInput');
                const prompt = input.value.trim();
                if (!prompt) return;
                
                addToChatArea('<strong>You:</strong> Travel plan for: ' + prompt, 'user-msg');
                
                try {
                    const response = await fetch('/plan/travel', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: prompt })
                    });
                    
                    const data = await response.json();
                    const plan = data.object;
                    addToChatArea(
                        '<strong>✈️ Travel Plan:</strong><br/>' +
                        '<strong>Destination:</strong> ' + plan.destination + '<br/>' +
                        '<strong>Duration:</strong> ' + plan.duration_days + ' days<br/>' +
                        '<strong>Budget:</strong> $' + plan.estimated_budget + '<br/>' +
                        '<strong>Best Season:</strong> ' + plan.best_season + '<br/>' +
                        '<strong>Activities:</strong> ' + plan.activities.join(', ')
                    );
                } catch (error) {
                    addToChatArea('<strong>Error:</strong> ' + error.message, 'error');
                }
            }
            
            async function analyzeTask() {
                const input = document.getElementById('taskInput');
                const prompt = input.value.trim();
                if (!prompt) return;
                
                addToChatArea('<strong>You:</strong> Analyze task: ' + prompt, 'user-msg');
                
                try {
                    const response = await fetch('/analyze/task', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: prompt })
                    });
                    
                    const data = await response.json();
                    const analysis = data.object;
                    addToChatArea(
                        '<strong>🎯 Task Analysis:</strong><br/>' +
                        '<strong>Type:</strong> ' + analysis.task_type + '<br/>' +
                        '<strong>Complexity:</strong> ' + analysis.complexity + '/10<br/>' +
                        '<strong>Steps:</strong> ' + analysis.steps_needed.join(', ') + '<br/>' +
                        '<strong>Tools:</strong> ' + analysis.tools_required.join(', ') + '<br/>' +
                        '<strong>Time:</strong> ' + analysis.estimated_time
                    );
                } catch (error) {
                    addToChatArea('<strong>Error:</strong> ' + error.message, 'error');
                }
            }
            
            async function getWeather() {
                const input = document.getElementById('weatherInput');
                const location = input.value.trim();
                if (!location) return;
                
                addToChatArea('<strong>You:</strong> Get weather for ' + location, 'user-msg');
                addToChatArea('<strong>🌤️ Weather Tool:</strong> The weather in ' + location + ' is sunny with 72°F temperature.');
            }
            
            async function calculate() {
                const input = document.getElementById('calcInput');
                const expression = input.value.trim();
                if (!expression) return;
                
                addToChatArea('<strong>You:</strong> Calculate: ' + expression, 'user-msg');
                try {
                    const result = eval(expression.replace(' ', ''));
                    addToChatArea('<strong>🔢 Calculator Tool:</strong> Result: ' + result);
                } catch (error) {
                    addToChatArea('<strong>Error:</strong> Invalid mathematical expression', 'error');
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
            
            async function startStream() {
                const input = document.getElementById('streamInput');
                const message = input.value.trim();
                if (!message) return;
                
                document.getElementById('stopBtn').disabled = false;
                addToChatArea('<strong>You:</strong> ' + message, 'user-msg');
                
                try {
                    const response = await fetch('/chat/stream', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ messages: [{role: 'user', content: message}] })
                    });
                    
                    const reader = response.body.getReader();
                    streamController = reader;
                    let streamContent = '<strong>🤖 Streaming Response:</strong> ';
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        
                        const chunk = new TextDecoder().decode(value);
                        const lines = chunk.split('\n');
                        
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
                } catch (error) {
                    addToChatArea('<strong>Streaming Error:</strong> ' + error.message, 'error');
                } finally {
                    document.getElementById('stopBtn').disabled = true;
                }
            }
            
            function stopStream() {
                if (streamController) {
                    streamController.cancel();
                    streamController = null;
                    document.getElementById('stopBtn').disabled = true;
                    addToChatArea('<strong>Stream stopped by user</strong>');
                }
            }
            
            async function checkHealth() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    document.getElementById('statusArea').innerHTML = 
                        '<div class="response"><strong>🟢 System Status:</strong> ' + data.status + 
                        '<br/><strong>Features:</strong> ' + data.features.join(', ') + '</div>';
                } catch (error) {
                    document.getElementById('statusArea').innerHTML = 
                        '<div class="error"><strong>🔴 Error:</strong> ' + error.message + '</div>';
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
    """Main function to run the FastAPI application with full AI SDK features."""
    print("🤖 AI SDK FastAPI Integration Example")
    print("=======================================")
    
    # Check requirements
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available. Install with: pip install fastapi uvicorn")
        return
    
    if not AI_SDK_AVAILABLE:
        print("❌ AI SDK not available. Make sure it's properly installed.")
        return
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable is required")
        print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Create different app versions to demonstrate features
    print("\n🎯 Available application modes:")
    print("1. 🚀 Advanced AI App (complete AI SDK features)")
    print("2. 🔧 Basic AI App (standard integration)")
    print("3. ⚙️ Middleware AI App (middleware-based integration)")
    
    mode = os.getenv("DEMO_MODE", "advanced").lower()
    
    try:
        if mode == "basic":
            app = create_basic_ai_app()
            app_type = "Basic"
            print("\n✅ Created basic AI application")
        elif mode == "middleware":
            app = create_middleware_ai_app()
            app_type = "Middleware"
            print("\n✅ Created middleware AI application")
        else:
            app = create_advanced_ai_app()
            app_type = "Advanced"
            print("\n🚀 Created advanced AI application with complete features")
        
        # Add demo HTML endpoint to all app types
        if hasattr(app, 'app'):
            # AIFastAPI class
            @app.app.get("/")
            async def root():
                return get_demo_html()
        else:
            # Regular FastAPI app
            @app.get("/")
            async def root():
                return get_demo_html()
        
        print(f"\n🎉 {app_type} AI Application ready!")
        print("\n📋 Available endpoints:")
        print("  GET  /          - 🌐 Interactive demo interface")
        print("  GET  /health    - 💚 Health check")
        print("  POST /chat      - 💬 Basic chat")
        print("  POST /chat/stream - ⚡ Streaming chat")
        
        if mode == "advanced":
            print("  GET  /tools     - 🔧 List available tools")
            print("  POST /recommend/book - 📚 Book recommendations")
            print("  POST /plan/travel - ✈️ Travel planning")
            print("  POST /analyze/task - 🎯 Task analysis")
            print("  WS   /ws/chat   - 🔄 WebSocket chat")
        elif mode == "middleware":
            print("  POST /middleware-chat - ⚙️ Middleware chat")
            print("  POST /multi-provider-chat - 🔀 Multi-provider chat")
        
        print("\n🌐 Starting server on http://localhost:8000")
        print("📖 Open http://localhost:8000 in your browser for the interactive demo")
        print("\n💡 Tips:")
        print("  - Try different models in the chat interface")
        print("  - Test structured object generation")
        print("  - Experience real-time streaming")
        print("  - Explore tool calling features")
        
        if mode == "advanced":
            print("\n🛠️ Advanced Features Enabled:")
            print("  ✅ Multi-model support (GPT-4o, GPT-4o-mini, GPT-3.5-turbo)")
            print("  ✅ Tool calling (weather, calculator)")
            print("  ✅ Structured object generation")
            print("  ✅ WebSocket real-time chat")
            print("  ✅ Server-sent events streaming")
        
        # Run the server
        try:
            import uvicorn
            uvicorn.run(
                app.app if hasattr(app, 'app') else app, 
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