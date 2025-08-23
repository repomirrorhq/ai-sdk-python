"""Flask Integration Example for AI SDK Python.

This example demonstrates how to build AI-powered Flask applications
using the AI SDK's Flask integration features.

Features demonstrated:
- AIFlask class with decorators
- Flask blueprints with AI integration
- Streaming responses
- Structured object generation
- Async route handling
"""

import asyncio
from typing import List, Dict, Any

# Flask imports
try:
    from flask import Flask, request, jsonify, g
    FLASK_AVAILABLE = True
except ImportError:
    print("Flask not installed. Install with: pip install flask")
    FLASK_AVAILABLE = False
    exit(1)

# AI SDK imports
from ai_sdk import create_openai, generate_text, stream_text
from ai_sdk.integrations.flask import (
    AIFlask,
    ai_blueprint,
    streaming_response_wrapper,
    async_route,
    create_chat_app
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


# Example 1: Basic Flask app with AIFlask class
def create_basic_ai_flask_app():
    """Create basic AIFlask application."""
    
    # Initialize AI provider (commented out - requires API key)
    # provider = create_openai()
    # ai_app = AIFlask(default_provider=provider)
    ai_app = AIFlask()  # Demo without provider
    
    @ai_app.chat_route("/chat", system_prompt="You are a helpful assistant.")
    def chat():
        """Basic chat route with system prompt."""
        data = request.get_json()
        messages = data.get("messages", [])
        
        # In real implementation:
        # result = asyncio.run(generate_text(model=g.ai_provider, messages=messages))
        # return {"response": result.text}
        
        # Demo response
        return {"response": f"Demo response to: {messages[-1].get('content', 'No message') if messages else 'No messages'}"}
    
    @ai_app.streaming_route("/chat/stream")
    def stream_chat():
        """Streaming chat route."""
        data = request.get_json()
        messages = data.get("messages", [])
        
        def generate_demo():
            """Demo generator for streaming."""
            demo_response = "This is a demo streaming response from Flask integration."
            for word in demo_response.split():
                yield word + " "
        
        return streaming_response_wrapper(generate_demo)
    
    return ai_app.app


# Example 2: Using Flask blueprints with AI integration
def create_blueprint_example():
    """Create Flask app using AI blueprints."""
    app = Flask(__name__)
    
    # Initialize AI provider (commented out - requires API key)
    # provider = create_openai()
    # ai_bp = ai_blueprint("ai", __name__, default_provider=provider)
    ai_bp = ai_blueprint("ai", __name__)  # Demo without provider
    
    # Pydantic models for structured responses
    if PYDANTIC_AVAILABLE:
        class WeatherReport(BaseModel):
            location: str = Field(description="Location name")
            temperature: float = Field(description="Temperature in Celsius")
            condition: str = Field(description="Weather condition")
            humidity: int = Field(description="Humidity percentage")
            recommendation: str = Field(description="Clothing/activity recommendation")
        
        class RecipeRecommendation(BaseModel):
            name: str = Field(description="Recipe name")
            cuisine: str = Field(description="Cuisine type")
            prep_time_minutes: int = Field(description="Preparation time in minutes")
            ingredients: List[str] = Field(description="List of ingredients")
            instructions: List[str] = Field(description="Cooking instructions")
            difficulty: str = Field(description="Difficulty level: easy, medium, hard")
    
    @ai_bp.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return {"status": "healthy", "ai_provider": g.ai_provider is not None}
    
    @ai_bp.route("/chat", methods=["POST"])
    @async_route
    async def blueprint_chat():
        """Chat endpoint in blueprint."""
        data = request.get_json()
        messages = data.get("messages", [])
        
        # Demo response
        return {"response": "Blueprint chat response", "messages_received": len(messages)}
    
    @ai_bp.route("/chat/stream", methods=["POST"])
    def blueprint_stream():
        """Streaming endpoint in blueprint."""
        data = request.get_json()
        messages = data.get("messages", [])
        
        async def generate():
            # In real implementation:
            # async for chunk in stream_text(model=g.ai_provider, messages=messages):
            #     yield chunk.text_delta
            
            # Demo streaming
            words = ["Streaming", "response", "from", "Flask", "blueprint", "integration"]
            for word in words:
                yield word + " "
                await asyncio.sleep(0.2)
        
        return streaming_response_wrapper(generate)
    
    if PYDANTIC_AVAILABLE:
        @ai_bp.route("/weather", methods=["POST"])
        def get_weather():
            """Get weather report with structured response."""
            data = request.get_json()
            location = data.get("location", "Unknown")
            
            # Demo structured response
            weather_data = {
                "location": location,
                "temperature": 22.5,
                "condition": "Partly Cloudy",
                "humidity": 65,
                "recommendation": "Light jacket recommended"
            }
            
            schema = pydantic_schema(WeatherReport)
            result = schema.validate(weather_data)
            
            if result.success:
                return {"weather": result.value.dict()}
            else:
                return {"error": str(result.error)}, 400
        
        @ai_bp.route("/recipe", methods=["POST"])
        def get_recipe():
            """Get recipe recommendation with structured response."""
            data = request.get_json()
            cuisine = data.get("cuisine", "Italian")
            
            # Demo structured response
            recipe_data = {
                "name": "Classic Pasta Carbonara",
                "cuisine": cuisine,
                "prep_time_minutes": 20,
                "ingredients": [
                    "400g spaghetti",
                    "200g pancetta",
                    "4 large eggs",
                    "100g Pecorino Romano cheese",
                    "Black pepper",
                    "Salt"
                ],
                "instructions": [
                    "Boil pasta in salted water until al dente",
                    "Cook pancetta until crispy",
                    "Mix eggs with grated cheese",
                    "Combine hot pasta with pancetta",
                    "Add egg mixture off heat, stirring quickly",
                    "Season with black pepper and serve"
                ],
                "difficulty": "medium"
            }
            
            schema = pydantic_schema(RecipeRecommendation)
            result = schema.validate(recipe_data)
            
            if result.success:
                return {"recipe": result.value.dict()}
            else:
                return {"error": str(result.error)}, 400
    
    # Register blueprint
    app.register_blueprint(ai_bp, url_prefix="/ai")
    
    @app.route("/")
    def index():
        """Index page with available endpoints."""
        endpoints = [
            "GET /ai/health - Health check",
            "POST /ai/chat - Basic chat",
            "POST /ai/chat/stream - Streaming chat",
        ]
        
        if PYDANTIC_AVAILABLE:
            endpoints.extend([
                "POST /ai/weather - Weather report (structured)",
                "POST /ai/recipe - Recipe recommendation (structured)"
            ])
        
        return {
            "message": "Flask AI SDK Integration Demo",
            "endpoints": endpoints,
            "note": "Set OPENAI_API_KEY for real AI responses"
        }
    
    return app


# Example 3: Advanced streaming with custom formatting
def create_advanced_streaming_app():
    """Create app with advanced streaming features."""
    ai_app = AIFlask()
    
    @ai_app.app.route("/stream/markdown", methods=["POST"])
    def stream_markdown():
        """Stream response formatted as markdown."""
        data = request.get_json()
        topic = data.get("topic", "Python programming")
        
        def generate_markdown():
            """Generate markdown content."""
            markdown_content = [
                f"# Guide to {topic}\n\n",
                "## Introduction\n\n",
                f"This is a comprehensive guide about {topic}.\n\n",
                "## Key Points\n\n",
                "- Point one with detailed explanation\n",
                "- Point two with examples\n", 
                "- Point three with best practices\n\n",
                "## Conclusion\n\n",
                f"Understanding {topic} is essential for developers.\n"
            ]
            
            for line in markdown_content:
                yield line
        
        return streaming_response_wrapper(generate_markdown)
    
    @ai_app.app.route("/stream/json", methods=["POST"]) 
    def stream_json():
        """Stream response as JSON objects."""
        import json
        
        def generate_json():
            """Generate streaming JSON responses."""
            responses = [
                {"type": "start", "message": "Starting analysis..."},
                {"type": "progress", "percentage": 25, "status": "Processing data"},
                {"type": "progress", "percentage": 50, "status": "Analyzing patterns"},
                {"type": "progress", "percentage": 75, "status": "Generating insights"},
                {"type": "result", "data": {"score": 85, "confidence": "high"}},
                {"type": "complete", "message": "Analysis finished"}
            ]
            
            for response in responses:
                yield f"data: {json.dumps(response)}\n\n"
        
        from flask import Response
        return Response(
            generate_json(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    
    return ai_app.app


# Example 4: Complete demo application
def create_complete_demo():
    """Create complete demo application with all features."""
    app = Flask(__name__)
    
    # Use the built-in chat app creator
    # provider = create_openai()  # Commented out - requires API key
    # chat_app = create_chat_app(provider, system_prompt="You are a helpful assistant.")
    
    # Manual setup for demo
    ai_app = AIFlask()
    
    @ai_app.app.route("/")
    def index():
        """Main index page with HTML client."""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Flask AI SDK Demo</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .chat-box { border: 1px solid #ccc; height: 400px; overflow-y: scroll; 
                           padding: 10px; margin: 10px 0; background: #f9f9f9; }
                .input-group { margin: 10px 0; }
                input[type="text"] { width: 70%; padding: 10px; }
                button { padding: 10px 20px; margin: 0 5px; }
                .message { margin: 5px 0; padding: 5px; }
                .user { background: #e3f2fd; }
                .ai { background: #f1f8e9; }
                .endpoint-list { background: #fff3e0; padding: 15px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Flask AI SDK Integration Demo</h1>
                
                <div class="endpoint-list">
                    <h3>Available Endpoints:</h3>
                    <ul>
                        <li><strong>POST /chat</strong> - Basic chat</li>
                        <li><strong>POST /chat/stream</strong> - Streaming chat</li>
                        <li><strong>POST /test/stream</strong> - Test streaming</li>
                    </ul>
                </div>
                
                <div class="chat-box" id="chatBox"></div>
                
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Type your message...">
                    <button onclick="sendMessage()">Send</button>
                    <button onclick="sendStreamMessage()">Send (Stream)</button>
                    <button onclick="clearChat()">Clear</button>
                </div>
            </div>
            
            <script>
                function addMessage(content, isUser = false) {
                    const chatBox = document.getElementById('chatBox');
                    const div = document.createElement('div');
                    div.className = 'message ' + (isUser ? 'user' : 'ai');
                    div.innerHTML = '<strong>' + (isUser ? 'You' : 'AI') + ':</strong> ' + content;
                    chatBox.appendChild(div);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
                
                async function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const message = input.value.trim();
                    if (!message) return;
                    
                    addMessage(message, true);
                    input.value = '';
                    
                    try {
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ messages: [{ role: 'user', content: message }] })
                        });
                        const data = await response.json();
                        addMessage(data.response);
                    } catch (error) {
                        addMessage('Error: ' + error.message);
                    }
                }
                
                async function sendStreamMessage() {
                    const input = document.getElementById('messageInput');
                    const message = input.value.trim();
                    if (!message) return;
                    
                    addMessage(message, true);
                    input.value = '';
                    
                    try {
                        const response = await fetch('/chat/stream', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ messages: [{ role: 'user', content: message }] })
                        });
                        
                        const reader = response.body.getReader();
                        const decoder = new TextDecoder();
                        let streamedText = '';
                        
                        while (true) {
                            const { done, value } = await reader.read();
                            if (done) break;
                            
                            const chunk = decoder.decode(value);
                            const lines = chunk.split('\\n');
                            
                            for (const line of lines) {
                                if (line.startsWith('data: ')) {
                                    const data = line.slice(6);
                                    if (data === '[DONE]') {
                                        addMessage(streamedText);
                                        streamedText = '';
                                        break;
                                    }
                                    try {
                                        const parsed = JSON.parse(data);
                                        streamedText += parsed.text || '';
                                    } catch (e) {
                                        // Ignore parse errors
                                    }
                                }
                            }
                        }
                    } catch (error) {
                        addMessage('Error: ' + error.message);
                    }
                }
                
                function clearChat() {
                    document.getElementById('chatBox').innerHTML = '';
                }
                
                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
            </script>
        </body>
        </html>
        '''
    
    @ai_app.chat_route("/chat")
    def demo_chat():
        """Demo chat endpoint."""
        data = request.get_json()
        messages = data.get("messages", [])
        last_message = messages[-1].get("content", "No message") if messages else "No messages"
        
        return {"response": f"Demo response to: '{last_message}'. (This is a demo - set up API key for real AI)"}
    
    @ai_app.streaming_route("/chat/stream")
    def demo_stream():
        """Demo streaming endpoint."""
        data = request.get_json()
        messages = data.get("messages", [])
        
        def generate():
            response = "This is a demo streaming response that shows how Flask integration works with AI SDK."
            for word in response.split():
                yield word + " "
        
        return streaming_response_wrapper(generate)
    
    @ai_app.app.route("/test/stream", methods=["POST"])
    def test_stream():
        """Test streaming endpoint."""
        def generate_test():
            import time
            for i in range(10):
                yield f"Chunk {i+1} of 10... "
        
        return streaming_response_wrapper(generate_test)
    
    return ai_app.app


# Main application factory
def create_app(app_type: str = "demo"):
    """Create the appropriate app type."""
    if app_type == "basic":
        return create_basic_ai_flask_app()
    elif app_type == "blueprint":
        return create_blueprint_example()
    elif app_type == "streaming":
        return create_advanced_streaming_app()
    elif app_type == "demo":
        return create_complete_demo()
    else:
        return create_complete_demo()


# For Flask CLI
app = create_app("demo")


if __name__ == "__main__":
    print("Flask AI SDK Integration Examples")
    print("=================================")
    print("\nAvailable apps:")
    print("- basic: Basic AIFlask application")
    print("- blueprint: Flask blueprints with AI integration")
    print("- streaming: Advanced streaming features")
    print("- demo: Complete demo with HTML client")
    print("\nTo run:")
    print("python flask_integration_example.py")
    print("\nOr with Flask CLI:")
    print("export FLASK_APP=flask_integration_example")
    print("flask run --debug")
    print("\nEndpoints (demo app):")
    print("- GET / - HTML client for testing")
    print("- POST /chat - Basic chat")
    print("- POST /chat/stream - Streaming chat")
    print("- POST /test/stream - Test streaming")
    print("\nNote: Set OPENAI_API_KEY environment variable for real AI responses")
    
    # Run the app
    app.run(debug=True, port=5000)