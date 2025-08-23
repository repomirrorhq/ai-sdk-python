# Enhanced Features Guide - AI SDK Python

This guide covers the new enhanced features added to AI SDK Python, bringing it to near-complete feature parity with the TypeScript AI SDK.

## Table of Contents

1. [Enhanced Schema Validation System](#enhanced-schema-validation-system)
2. [Framework Integrations](#framework-integrations)
   - [FastAPI Integration](#fastapi-integration)
   - [Flask Integration](#flask-integration)
3. [Advanced Streaming Features](#advanced-streaming-features)
4. [Migration from Basic Usage](#migration-from-basic-usage)
5. [Best Practices](#best-practices)

## Enhanced Schema Validation System

The AI SDK Python now supports multiple validation libraries beyond Pydantic, providing flexibility for different project requirements.

### Supported Validation Libraries

#### 1. Pydantic (Recommended)

```python
from pydantic import BaseModel, Field
from ai_sdk.schemas import pydantic_schema
from ai_sdk import generate_object, create_openai

class BookReview(BaseModel):
    title: str = Field(description="The book title")
    author: str = Field(description="The book author")
    rating: int = Field(description="Rating from 1-5", ge=1, le=5)
    summary: str = Field(description="Brief review summary")
    recommend: bool = Field(description="Whether to recommend this book")

# Create schema validator
schema = pydantic_schema(BookReview)

# Use with AI generation
provider = create_openai()
result = await generate_object(
    model=provider.chat("gpt-4"),
    prompt="Write a book review for 'Dune' by Frank Herbert",
    schema=schema
)

print(f"Generated review: {result.object}")
```

#### 2. JSONSchema (Pure JSON Schema)

```python
from ai_sdk.schemas import jsonschema_schema

# Define JSON Schema
book_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "The book title"},
        "author": {"type": "string", "description": "The book author"},
        "rating": {
            "type": "integer", 
            "minimum": 1, 
            "maximum": 5,
            "description": "Rating from 1-5"
        },
        "summary": {"type": "string", "description": "Brief review summary"},
        "recommend": {"type": "boolean", "description": "Whether to recommend"}
    },
    "required": ["title", "author", "rating", "summary", "recommend"],
    "additionalProperties": False
}

# Create schema validator
schema = jsonschema_schema(book_schema)

# Validate data manually
test_data = {
    "title": "Dune",
    "author": "Frank Herbert",
    "rating": 5,
    "summary": "Epic science fiction masterpiece",
    "recommend": True
}

result = schema.validate(test_data)
if result.success:
    print(f"Valid data: {result.value}")
else:
    print(f"Validation error: {result.error}")
```

#### 3. Marshmallow (Optional)

```python
# Requires: pip install marshmallow
from marshmallow import Schema, fields
from ai_sdk.schemas import marshmallow_schema

class BookReviewSchema(Schema):
    title = fields.String(required=True, metadata={'description': 'The book title'})
    author = fields.String(required=True, metadata={'description': 'The book author'})
    rating = fields.Integer(required=True, validate=lambda x: 1 <= x <= 5,
                           metadata={'description': 'Rating from 1-5'})
    summary = fields.String(required=True, metadata={'description': 'Brief review summary'})
    recommend = fields.Boolean(required=True, metadata={'description': 'Whether to recommend'})

# Create schema validator
schema = marshmallow_schema(BookReviewSchema())

# Use with AI generation or manual validation
result = schema.validate({
    "title": "Foundation",
    "author": "Isaac Asimov", 
    "rating": 4,
    "summary": "Classic science fiction series",
    "recommend": True
})
```

#### 4. Cerberus (Optional)

```python
# Requires: pip install cerberus
from ai_sdk.schemas import cerberus_schema

# Define Cerberus schema
book_review_schema = {
    'title': {'type': 'string', 'required': True},
    'author': {'type': 'string', 'required': True},
    'rating': {'type': 'integer', 'min': 1, 'max': 5, 'required': True},
    'summary': {'type': 'string', 'required': True},
    'recommend': {'type': 'boolean', 'required': True},
    'tags': {
        'type': 'list',
        'schema': {'type': 'string'},
        'required': False
    }
}

# Create schema validator
schema = cerberus_schema(book_review_schema)

# Use for validation
result = schema.validate({
    "title": "The Martian",
    "author": "Andy Weir",
    "rating": 4,
    "summary": "Survival story on Mars",
    "recommend": True,
    "tags": ["science-fiction", "survival", "mars"]
})
```

### Schema Validation Features

All schema validators provide a unified interface:

```python
# Common interface for all schema types
schema = pydantic_schema(MyModel)  # or jsonschema_schema, marshmallow_schema, etc.

# Validate data
result = schema.validate(data)
if result.success:
    validated_data = result.value
else:
    error = result.error
    print(f"Error: {error}")
    print(f"Details: {error.errors}")

# Direct validation (raises exception on error)
try:
    validated_data = schema(data)
except SchemaValidationError as e:
    print(f"Validation failed: {e}")

# Convert to JSON Schema format
json_schema = schema.to_json_schema()

# Check schema type
print(f"Schema type: {schema.schema_type}")  # 'pydantic', 'jsonschema', etc.
```

## Framework Integrations

### FastAPI Integration

The FastAPI integration provides high-level decorators and utilities for building AI-powered APIs.

#### Basic Usage

```python
from fastapi import FastAPI
from ai_sdk import create_openai
from ai_sdk.integrations.fastapi import AIFastAPI

# Initialize with AI provider
provider = create_openai()
ai_app = AIFastAPI(default_provider=provider)

# Basic chat endpoint
@ai_app.chat_endpoint("/chat")
async def chat(model, messages):
    result = await generate_text(model=model, messages=messages)
    return result.text

# Streaming chat endpoint
@ai_app.streaming_chat_endpoint("/chat/stream")
async def stream_chat(model, messages):
    async for chunk in stream_text(model=model, messages=messages):
        yield chunk.text_delta

# Structured object generation
from ai_sdk.schemas import pydantic_schema

@ai_app.object_endpoint("/generate/recipe", schema=pydantic_schema(Recipe))
async def generate_recipe(model, prompt, schema):
    result = await generate_object(model=model, prompt=prompt, schema=schema)
    return result.object

# WebSocket chat
@ai_app.websocket_chat("/ws/chat")
async def websocket_chat(websocket, model, messages):
    async for chunk in stream_text(model=model, messages=messages):
        await websocket.send_json({
            "type": "text_delta",
            "text": chunk.text_delta
        })
    await websocket.send_json({"type": "done"})

# Access the FastAPI app
app = ai_app.app
```

#### Advanced FastAPI Features

```python
from fastapi import FastAPI, Request
from ai_sdk.integrations.fastapi import fastapi_ai_middleware

# Use with existing FastAPI app
app = FastAPI()
provider = create_openai()

# Add AI middleware
fastapi_ai_middleware(app, default_provider=provider)

@app.post("/custom-chat")
async def custom_chat(request: Request):
    # Access AI provider from request state
    model = request.state.ai_provider
    
    # Use AI SDK utilities
    generate_text = request.state.ai_sdk['generate_text']
    
    data = await request.json()
    result = await generate_text(model=model, messages=data["messages"])
    
    return {"response": result.text}
```

#### FastAPI with Custom Middleware

```python
from ai_sdk.integrations.fastapi import AIFastAPIMiddleware

class CustomAIMiddleware(AIFastAPIMiddleware):
    async def dispatch(self, request, call_next):
        # Add custom logic before AI processing
        start_time = time.time()
        
        response = await super().dispatch(request, call_next)
        
        # Add processing time header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

app.add_middleware(CustomAIMiddleware, default_provider=provider)
```

### Flask Integration

The Flask integration provides decorators and utilities for building AI-powered Flask applications.

#### Basic Usage

```python
from flask import Flask
from ai_sdk import create_openai
from ai_sdk.integrations.flask import AIFlask

# Initialize with AI provider
provider = create_openai()
ai_app = AIFlask(default_provider=provider)

# Basic chat endpoint
@ai_app.chat_route("/chat")
def chat():
    data = request.get_json()
    messages = data.get("messages", [])
    
    result = asyncio.run(generate_text(model=g.ai_provider, messages=messages))
    return {"response": result.text}

# Streaming chat endpoint  
@ai_app.streaming_route("/chat/stream")
def stream_chat():
    data = request.get_json()
    messages = data.get("messages", [])
    
    async def generate():
        async for chunk in stream_text(model=g.ai_provider, messages=messages):
            yield chunk.text_delta
    
    return streaming_response_wrapper(generate())

# Structured object generation
@ai_app.object_route("/generate/summary", schema=pydantic_schema(Summary))
def generate_summary():
    data = request.get_json()
    prompt = data["prompt"]
    
    result = asyncio.run(generate_object(
        model=g.ai_provider, 
        prompt=prompt, 
        schema=g.ai_schema
    ))
    return {"summary": result.object}

# Access the Flask app
app = ai_app.app
```

#### Flask Blueprints

```python
from ai_sdk.integrations.flask import ai_blueprint

# Create AI-enabled blueprint
ai_bp = ai_blueprint("ai", __name__, default_provider=provider)

@ai_bp.route("/health")
def health():
    return {"status": "healthy", "ai_provider": g.ai_provider is not None}

@ai_bp.route("/chat", methods=["POST"])
@async_route
async def blueprint_chat():
    data = request.get_json()
    messages = data.get("messages", [])
    
    result = await generate_text(model=g.ai_provider, messages=messages)
    return {"response": result.text}

# Register blueprint
app = Flask(__name__)
app.register_blueprint(ai_bp, url_prefix="/ai")
```

#### Flask Utility Functions

```python
from ai_sdk.integrations.flask import (
    streaming_response_wrapper,
    async_route,
    create_chat_app
)

# Create a complete chat app quickly
provider = create_openai()
app = create_chat_app(
    provider=provider, 
    system_prompt="You are a helpful assistant specialized in Python programming."
)

# Custom streaming endpoint
@app.route("/custom-stream", methods=["POST"])
def custom_stream():
    def generate_response():
        # Your custom streaming logic
        for i in range(10):
            yield f"Processing step {i+1}...\n"
            time.sleep(0.1)
    
    return streaming_response_wrapper(generate_response)

# Async route handling
@app.route("/async-endpoint")
@async_route
async def async_endpoint():
    # Use async/await in Flask route
    await asyncio.sleep(0.1)
    return {"status": "async complete"}
```

## Advanced Streaming Features

### Multi-Model Streaming

```python
from ai_sdk import create_openai, create_anthropic, stream_text
import asyncio

async def multi_model_streaming():
    """Stream responses from multiple models simultaneously."""
    openai = create_openai()
    anthropic = create_anthropic()
    
    messages = [{"role": "user", "content": "Explain quantum computing"}]
    
    async def stream_from_model(model, model_name):
        async for chunk in stream_text(model=model, messages=messages):
            yield f"[{model_name}] {chunk.text_delta}"
    
    # Stream from both models
    openai_stream = stream_from_model(openai.chat("gpt-4"), "OpenAI")
    anthropic_stream = stream_from_model(anthropic.chat("claude-3-sonnet"), "Anthropic")
    
    # Merge streams (simplified example)
    async for chunk in merge_streams(openai_stream, anthropic_stream):
        print(chunk)
```

### Custom Stream Processing

```python
from ai_sdk.streaming import smooth_stream, ChunkDetector

async def enhanced_streaming():
    """Enhanced streaming with custom processing."""
    provider = create_openai()
    
    # Custom chunk detector for different content types
    detector = ChunkDetector(
        code_patterns=[r'```\w+', r'```'],
        list_patterns=[r'^\d+\.', r'^\*', r'^-'],
        heading_patterns=[r'^#+\s']
    )
    
    async for chunk in stream_text(
        model=provider.chat("gpt-4"),
        messages=[{"role": "user", "content": "Write a Python tutorial"}]
    ):
        # Process chunk based on content type
        chunk_type = detector.detect(chunk.text_delta)
        
        if chunk_type == "code":
            print(f"CODE: {chunk.text_delta}")
        elif chunk_type == "heading":
            print(f"HEADING: {chunk.text_delta}")
        else:
            print(f"TEXT: {chunk.text_delta}")
```

## Migration from Basic Usage

### Before (Basic Usage)

```python
from ai_sdk import generate_text, create_openai
import asyncio

async def basic_chat():
    provider = create_openai()
    result = await generate_text(
        model=provider.chat("gpt-4"),
        messages=[{"role": "user", "content": "Hello"}]
    )
    return result.text

# Run with asyncio
response = asyncio.run(basic_chat())
```

### After (FastAPI Integration)

```python
from ai_sdk.integrations.fastapi import AIFastAPI
from ai_sdk import create_openai

provider = create_openai()
ai_app = AIFastAPI(default_provider=provider)

@ai_app.chat_endpoint("/chat")
async def chat(model, messages):
    result = await generate_text(model=model, messages=messages)
    return result.text

# Now you have a full REST API with one decorator!
app = ai_app.app  # Use with uvicorn app:app
```

### Before (Manual Schema Validation)

```python
from pydantic import BaseModel
import json

class Response(BaseModel):
    answer: str
    confidence: float

# Manual validation
raw_response = '{"answer": "42", "confidence": 0.95}'
data = json.loads(raw_response)
validated = Response(**data)
```

### After (Unified Schema System)

```python
from ai_sdk.schemas import pydantic_schema, jsonschema_schema, marshmallow_schema

# Choose your preferred validation library
schema = pydantic_schema(Response)  # or jsonschema_schema, etc.

# Unified validation interface
result = schema.validate(data)
if result.success:
    validated_data = result.value
else:
    print(f"Error: {result.error}")
```

## Best Practices

### 1. Schema Selection

- **Use Pydantic** for new projects with complex validation needs
- **Use JSONSchema** for simple validation or when working with existing JSON schemas  
- **Use Marshmallow** if already using it in your project
- **Use Cerberus** for lightweight validation needs

### 2. Framework Integration

- **Choose FastAPI** for modern async APIs with automatic OpenAPI documentation
- **Choose Flask** for simple APIs or when integrating with existing Flask applications

### 3. Error Handling

```python
from ai_sdk.schemas import SchemaValidationError
from ai_sdk.errors import AISDKError

try:
    result = await generate_object(model=model, prompt=prompt, schema=schema)
    validated_data = schema.validate(result.object)
    
    if not validated_data.success:
        # Handle validation error
        logger.error(f"Validation failed: {validated_data.error}")
        return {"error": "Invalid response format"}
        
except AISDKError as e:
    # Handle AI SDK specific errors
    logger.error(f"AI SDK error: {e}")
    return {"error": "AI service unavailable"}
    
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
    return {"error": "Internal server error"}
```

### 4. Performance Optimization

```python
# Use streaming for long responses
@ai_app.streaming_chat_endpoint("/chat/stream")
async def optimized_chat(model, messages):
    async for chunk in stream_text(
        model=model, 
        messages=messages,
        max_tokens=1000,  # Limit response length
        temperature=0.7   # Adjust creativity vs consistency
    ):
        yield chunk.text_delta

# Use connection pooling for high-traffic applications
provider = create_openai(
    # Configure connection pooling
    http_client=httpx.AsyncClient(
        limits=httpx.Limits(max_keepalive_connections=100)
    )
)
```

### 5. Security Considerations

```python
# Sanitize user inputs
import html
from ai_sdk.utils import secure_json

@ai_app.chat_endpoint("/secure-chat")
async def secure_chat(model, messages):
    # Sanitize messages
    sanitized_messages = []
    for msg in messages:
        if msg.get("role") == "user":
            # Escape HTML and limit length
            content = html.escape(msg.get("content", ""))[:1000]
            sanitized_messages.append({"role": "user", "content": content})
        else:
            sanitized_messages.append(msg)
    
    result = await generate_text(model=model, messages=sanitized_messages)
    return {"response": result.text}
```

## Conclusion

The enhanced AI SDK Python now provides comprehensive feature parity with the TypeScript version, including:

- ✅ **Multiple Schema Validation Libraries** - Flexible validation with your preferred library
- ✅ **Framework Integrations** - FastAPI and Flask integrations with decorators and utilities  
- ✅ **Advanced Streaming** - Enhanced streaming capabilities with custom processing
- ✅ **Production Ready** - Error handling, security, and performance optimizations
- ✅ **Easy Migration** - Simple upgrade path from basic usage

These features make AI SDK Python the most comprehensive and flexible AI toolkit for Python developers, supporting everything from simple scripts to production-scale applications.