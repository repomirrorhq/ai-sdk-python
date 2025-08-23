#!/usr/bin/env python3
"""Simple test for Valibot schema without dependencies."""

import sys
sys.path.append('src')

from ai_sdk.schemas.valibot import string, number, boolean, object, array

def test_basic_validation():
    """Test basic validation functionality."""
    
    print("🧪 Testing Valibot Schema System")
    print("=" * 40)
    
    # Test string schema
    print("1. String validation:")
    str_schema = string(min_length=2, max_length=10)
    
    # Valid case
    result = str_schema.safe_parse("hello")
    print(f"   'hello' -> {'✅ Valid' if result['success'] else '❌ Invalid'}")
    
    # Invalid case (too short)
    result = str_schema.safe_parse("x")
    print(f"   'x' -> {'✅ Valid' if result['success'] else '❌ Invalid'}")
    if not result['success']:
        print(f"     Issues: {[issue['message'] for issue in result['issues']]}")
    
    # Test number schema
    print("\n2. Number validation:")
    num_schema = number(min_value=0, max_value=100)
    
    # Valid case
    result = num_schema.safe_parse(50)
    print(f"   50 -> {'✅ Valid' if result['success'] else '❌ Invalid'}")
    
    # Invalid case (too high)
    result = num_schema.safe_parse(150)
    print(f"   150 -> {'✅ Valid' if result['success'] else '❌ Invalid'}")
    if not result['success']:
        print(f"     Issues: {[issue['message'] for issue in result['issues']]}")
    
    # Test object schema
    print("\n3. Object validation:")
    obj_schema = object({
        "name": string(min_length=1),
        "age": number(min_value=0)
    })
    
    # Valid case
    valid_data = {"name": "Alice", "age": 30}
    result = obj_schema.safe_parse(valid_data)
    print(f"   {valid_data} -> {'✅ Valid' if result['success'] else '❌ Invalid'}")
    
    # Invalid case
    invalid_data = {"name": "", "age": -5}
    result = obj_schema.safe_parse(invalid_data)
    print(f"   {invalid_data} -> {'✅ Valid' if result['success'] else '❌ Invalid'}")
    if not result['success']:
        print(f"     Issues: {[issue['message'] for issue in result['issues']]}")
    
    # Test array schema
    print("\n4. Array validation:")
    arr_schema = array(string())
    
    # Valid case
    valid_array = ["hello", "world"]
    result = arr_schema.safe_parse(valid_array)
    print(f"   {valid_array} -> {'✅ Valid' if result['success'] else '❌ Invalid'}")
    
    # Invalid case
    invalid_array = ["hello", 123]
    result = arr_schema.safe_parse(invalid_array)
    print(f"   {invalid_array} -> {'✅ Valid' if result['success'] else '❌ Invalid'}")
    if not result['success']:
        print(f"     Issues: {[issue['message'] for issue in result['issues']]}")
    
    # Test JSON Schema conversion
    print("\n5. JSON Schema conversion:")
    schema = object({
        "title": string(min_length=1),
        "priority": number(min_value=1, max_value=5)
    })
    
    json_schema = schema.to_json_schema()
    print(f"   Valibot -> JSON Schema:")
    print(f"   {json_schema}")
    
    print("\n✅ All basic tests completed!")

if __name__ == "__main__":
    test_basic_validation()