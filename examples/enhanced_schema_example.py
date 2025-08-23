"""Enhanced Schema Validation Example for AI SDK Python.

This example demonstrates the new unified schema validation system
that supports multiple Python validation libraries:
- Pydantic (recommended)
- JSONSchema (pure JSON Schema)
- Marshmallow (optional)  
- Cerberus (optional)
"""

import asyncio
from typing import Any, Dict, List

# Import AI SDK
from ai_sdk import generate_object, create_openai

# Import schema validators
from ai_sdk.schemas import (
    pydantic_schema, 
    jsonschema_schema,
    # Optional imports (will be None if not installed)
    marshmallow_schema,
    cerberus_schema
)

# For Pydantic example
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    BaseModel = object
    Field = None
    PYDANTIC_AVAILABLE = False

# For Marshmallow example  
try:
    from marshmallow import Schema, fields
    MARSHMALLOW_AVAILABLE = True
except ImportError:
    Schema = object
    fields = object
    MARSHMALLOW_AVAILABLE = False


async def demonstrate_pydantic_schema():
    """Demonstrate Pydantic schema validation."""
    print("=== Pydantic Schema Example ===")
    
    if not PYDANTIC_AVAILABLE:
        print("Pydantic not available - skipping example")
        return
    
    # Define Pydantic model
    class BookReview(BaseModel):
        title: str = Field(description="The book title")
        author: str = Field(description="The book author")
        rating: int = Field(description="Rating from 1-5", ge=1, le=5)
        summary: str = Field(description="Brief review summary")
        recommend: bool = Field(description="Whether to recommend this book")
    
    # Create schema validator
    schema = pydantic_schema(BookReview)
    
    print(f"Schema type: {schema.schema_type}")
    print(f"JSON Schema: {schema.to_json_schema()}")
    
    # Test validation
    test_data = {
        "title": "The Python Handbook",
        "author": "John Smith", 
        "rating": 4,
        "summary": "Great introduction to Python programming",
        "recommend": True
    }
    
    result = schema.validate(test_data)
    print(f"Validation successful: {result.success}")
    if result.success:
        print(f"Validated data: {result.value}")
    
    # Use with AI SDK (commented out - requires API key)
    # provider = create_openai()  
    # result = await generate_object(
    #     model=provider.chat("gpt-4"),
    #     prompt="Write a book review for 'Dune' by Frank Herbert",
    #     schema=schema
    # )
    # print(f"AI generated review: {result.object}")


async def demonstrate_jsonschema_validation():
    """Demonstrate JSONSchema validation.""" 
    print("\n=== JSONSchema Example ===")
    
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
            "recommend": {"type": "boolean", "description": "Whether to recommend this book"}
        },
        "required": ["title", "author", "rating", "summary", "recommend"],
        "additionalProperties": False
    }
    
    # Create schema validator
    schema = jsonschema_schema(book_schema)
    
    print(f"Schema type: {schema.schema_type}")
    print(f"JSON Schema: {schema.to_json_schema()}")
    
    # Test validation
    test_data = {
        "title": "Clean Code",
        "author": "Robert Martin",
        "rating": 5,
        "summary": "Essential reading for any programmer",
        "recommend": True
    }
    
    result = schema.validate(test_data)
    print(f"Validation successful: {result.success}")
    if result.success:
        print(f"Validated data: {result.value}")


async def demonstrate_marshmallow_schema():
    """Demonstrate Marshmallow schema validation."""
    print("\n=== Marshmallow Schema Example ===")
    
    if not MARSHMALLOW_AVAILABLE or marshmallow_schema is None:
        print("Marshmallow not available - skipping example")
        return
    
    # Define Marshmallow schema
    class BookReviewSchema(Schema):
        title = fields.String(required=True, metadata={'description': 'The book title'})
        author = fields.String(required=True, metadata={'description': 'The book author'})
        rating = fields.Integer(required=True, validate=lambda x: 1 <= x <= 5,
                               metadata={'description': 'Rating from 1-5'})
        summary = fields.String(required=True, metadata={'description': 'Brief review summary'})
        recommend = fields.Boolean(required=True, metadata={'description': 'Whether to recommend'})
    
    # Create schema validator
    schema = marshmallow_schema(BookReviewSchema())
    
    print(f"Schema type: {schema.schema_type}")
    print(f"JSON Schema: {schema.to_json_schema()}")
    
    # Test validation
    test_data = {
        "title": "Design Patterns",
        "author": "Gang of Four",
        "rating": 4,
        "summary": "Classic software engineering book",
        "recommend": True
    }
    
    result = schema.validate(test_data)
    print(f"Validation successful: {result.success}")
    if result.success:
        print(f"Validated data: {result.value}")


async def demonstrate_cerberus_schema():
    """Demonstrate Cerberus schema validation."""
    print("\n=== Cerberus Schema Example ===")
    
    if cerberus_schema is None:
        print("Cerberus not available - skipping example")
        return
    
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
    
    print(f"Schema type: {schema.schema_type}")
    print(f"JSON Schema: {schema.to_json_schema()}")
    
    # Test validation
    test_data = {
        "title": "Effective Python", 
        "author": "Brett Slatkin",
        "rating": 5,
        "summary": "Great tips for Python developers",
        "recommend": True,
        "tags": ["python", "programming", "best-practices"]
    }
    
    result = schema.validate(test_data)
    print(f"Validation successful: {result.success}")
    if result.success:
        print(f"Validated data: {result.value}")


async def demonstrate_schema_error_handling():
    """Demonstrate error handling across different schema validators."""
    print("\n=== Error Handling Examples ===")
    
    # Test with invalid data
    invalid_data = {
        "title": "",  # Empty string
        "author": "Valid Author",
        "rating": 10,  # Out of range
        "summary": "Valid summary"
        # Missing required 'recommend' field
    }
    
    # Test JSONSchema validation
    book_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "minLength": 1},
            "author": {"type": "string"},
            "rating": {"type": "integer", "minimum": 1, "maximum": 5},
            "summary": {"type": "string"},
            "recommend": {"type": "boolean"}
        },
        "required": ["title", "author", "rating", "summary", "recommend"]
    }
    
    schema = jsonschema_schema(book_schema)
    result = schema.validate(invalid_data)
    
    print(f"JSONSchema validation failed (expected): {not result.success}")
    if result.error:
        print(f"Error message: {result.error}")
        print(f"Error details: {result.error.errors}")


async def main():
    """Run all schema examples."""
    print("AI SDK Python - Enhanced Schema Validation Examples")
    print("=" * 60)
    
    await demonstrate_pydantic_schema()
    await demonstrate_jsonschema_validation()
    await demonstrate_marshmallow_schema()
    await demonstrate_cerberus_schema()
    await demonstrate_schema_error_handling()
    
    print("\n" + "=" * 60)
    print("Schema validation examples completed!")
    print("\nNote: To use with AI generation, set your API keys:")
    print("export OPENAI_API_KEY='your-api-key'")


if __name__ == "__main__":
    asyncio.run(main())