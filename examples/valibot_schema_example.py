#!/usr/bin/env python3
"""
Example demonstrating Valibot-style schema validation in AI SDK Python.

This example shows how to use Valibot-inspired schema validation, providing
a familiar API for developers coming from the TypeScript ecosystem while
leveraging Python's type system.
"""

import asyncio
from ai_sdk import generate_text
from ai_sdk.providers.openai import openai
from ai_sdk.schemas import string, number, boolean, object, array, valibot_schema

# Example: Using Valibot-style schemas for structured generation
async def valibot_schema_example():
    """Demonstrate Valibot-style schema validation."""
    
    print("🔬 Valibot-Style Schema Example")
    print("=" * 50)
    
    # Define a schema using Valibot-style API
    user_schema = object({
        "name": string(min_length=1, max_length=100),
        "age": number(min_value=0, max_value=150),
        "email": string(),
        "is_active": boolean(),
        "hobbies": array(string())
    })
    
    # Convert to AI SDK schema
    ai_schema = valibot_schema(user_schema)
    
    print("📋 Schema defined using Valibot-style API:")
    print("- name: string (1-100 chars)")
    print("- age: number (0-150)")
    print("- email: string")
    print("- is_active: boolean")
    print("- hobbies: array of strings")
    print()
    
    try:
        # Generate structured data using the schema
        result = await generate_text(
            model=openai("gpt-4"),
            prompt="Generate a realistic user profile for a software developer",
            schema=ai_schema,
            max_tokens=200
        )
        
        print("✅ Generated user profile:")
        print(f"📄 Raw response: {result.text}")
        if result.object:
            print(f"👤 Parsed object: {result.object}")
            
            # Demonstrate validation
            print("\n🔍 Schema validation results:")
            validation_result = ai_schema.validate(result.object)
            if validation_result.success:
                print("✅ Validation passed!")
                print(f"📊 Validated data: {validation_result.data}")
            else:
                print("❌ Validation failed!")
                print(f"🐛 Error: {validation_result.error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Demonstrate error handling with invalid data
        print("\n🧪 Testing validation with invalid data:")
        test_invalid_data()

def test_invalid_data():
    """Test schema validation with invalid data."""
    
    # Create a simple schema
    person_schema = object({
        "name": string(min_length=2),
        "age": number(min_value=0, max_value=120)
    })
    
    # Test with invalid data
    invalid_data = {
        "name": "X",  # Too short
        "age": 150,   # Too high
        "extra": "field"  # Extra field (not allowed in strict object)
    }
    
    result = person_schema.safe_parse(invalid_data)
    if not result["success"]:
        print("🐛 Validation issues found:")
        for i, issue in enumerate(result["issues"], 1):
            print(f"  {i}. {issue['message']}")
            if issue.get("path"):
                print(f"     Path: {' -> '.join(map(str, issue['path']))}")

async def comparison_example():
    """Compare Valibot-style with other schema systems."""
    
    print("\n🆚 Schema System Comparison")
    print("=" * 50)
    
    # Same schema defined in different ways
    
    # 1. Valibot-style
    vali_schema = object({
        "title": string(min_length=1),
        "priority": number(min_value=1, max_value=5)
    })
    
    print("1️⃣ Valibot-style:")
    print("   object({'title': string(min_length=1), 'priority': number(1, 5)})")
    
    # 2. JSON Schema equivalent
    json_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "minLength": 1},
            "priority": {"type": "number", "minimum": 1, "maximum": 5}
        },
        "required": ["title", "priority"],
        "additionalProperties": False
    }
    
    print("2️⃣ JSON Schema equivalent:")
    print("   Complex nested dictionary structure")
    
    # 3. Test data
    test_data = {"title": "Important Task", "priority": 3}
    
    # Validate with Valibot-style
    vali_result = vali_schema.safe_parse(test_data)
    print(f"\n✅ Valibot validation: {'Success' if vali_result['success'] else 'Failed'}")
    
    # Show JSON Schema conversion
    print(f"🔄 Valibot -> JSON Schema: {vali_schema.to_json_schema()}")

async def advanced_example():
    """Show advanced Valibot-style features."""
    
    print("\n🚀 Advanced Valibot Features")
    print("=" * 50)
    
    # Complex nested schema
    api_response_schema = object({
        "data": array(
            object({
                "id": string(),
                "attributes": object({
                    "name": string(min_length=1),
                    "score": number(min_value=0, max_value=100),
                    "active": boolean()
                })
            })
        ),
        "meta": object({
            "total": number(min_value=0),
            "page": number(min_value=1)
        })
    })
    
    # Test data
    test_response = {
        "data": [
            {
                "id": "user-123",
                "attributes": {
                    "name": "Alice Smith",
                    "score": 85,
                    "active": True
                }
            }
        ],
        "meta": {
            "total": 1,
            "page": 1
        }
    }
    
    result = api_response_schema.safe_parse(test_response)
    print(f"📊 Complex validation result: {'✅ Success' if result['success'] else '❌ Failed'}")
    
    if result["success"]:
        print("🎯 All nested validations passed!")
        print(f"📋 Data structure: {len(result['output']['data'])} items")

if __name__ == "__main__":
    async def main():
        await valibot_schema_example()
        await comparison_example()
        await advanced_example()
        
        print("\n🎉 Valibot Schema Example Complete!")
        print("\nKey Benefits:")
        print("✨ Familiar API for TypeScript developers")
        print("🐍 Python-native implementation")
        print("🔧 Integrates seamlessly with AI SDK")
        print("📝 Clear validation error messages")
        print("🔄 JSON Schema interoperability")
    
    asyncio.run(main())