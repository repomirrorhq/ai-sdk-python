#!/usr/bin/env python3
"""
Tests for Valibot-style schema validation system.

This test suite ensures that the Valibot-inspired schema validation
works correctly and provides the expected API compatibility.
"""

import pytest
from ai_sdk.schemas.valibot import (
    string, number, boolean, object, array, valibot_schema,
    ValiError, StringSchema, NumberSchema, BooleanSchema, 
    ObjectSchema, ArraySchema
)

class TestStringSchema:
    """Test string schema validation."""
    
    def test_valid_string(self):
        """Test valid string validation."""
        schema = string()
        result = schema.safe_parse("hello")
        assert result["success"] is True
        assert result["output"] == "hello"
    
    def test_invalid_type(self):
        """Test invalid type validation."""
        schema = string()
        result = schema.safe_parse(123)
        assert result["success"] is False
        assert len(result["issues"]) == 1
        assert result["issues"][0]["code"] == "invalid_type"
    
    def test_min_length(self):
        """Test minimum length validation."""
        schema = string(min_length=5)
        
        # Valid case
        result = schema.safe_parse("hello")
        assert result["success"] is True
        
        # Invalid case
        result = schema.safe_parse("hi")
        assert result["success"] is False
        assert result["issues"][0]["code"] == "too_small"
    
    def test_max_length(self):
        """Test maximum length validation."""
        schema = string(max_length=3)
        
        # Valid case
        result = schema.safe_parse("hi")
        assert result["success"] is True
        
        # Invalid case
        result = schema.safe_parse("hello")
        assert result["success"] is False
        assert result["issues"][0]["code"] == "too_big"
    
    def test_parse_method(self):
        """Test parse method that raises exceptions."""
        schema = string(min_length=5)
        
        # Valid case
        assert schema.parse("hello") == "hello"
        
        # Invalid case
        with pytest.raises(ValiError) as exc_info:
            schema.parse("hi")
        assert len(exc_info.value.issues) == 1
    
    def test_json_schema_conversion(self):
        """Test JSON schema conversion."""
        schema = string(min_length=2, max_length=10)
        json_schema = schema.to_json_schema()
        
        expected = {
            "type": "string",
            "minLength": 2,
            "maxLength": 10
        }
        assert json_schema == expected

class TestNumberSchema:
    """Test number schema validation."""
    
    def test_valid_numbers(self):
        """Test valid number validation."""
        schema = number()
        
        # Integer
        result = schema.safe_parse(42)
        assert result["success"] is True
        assert result["output"] == 42
        
        # Float
        result = schema.safe_parse(3.14)
        assert result["success"] is True
        assert result["output"] == 3.14
    
    def test_invalid_type(self):
        """Test invalid type validation."""
        schema = number()
        result = schema.safe_parse("42")
        assert result["success"] is False
        assert result["issues"][0]["code"] == "invalid_type"
    
    def test_min_value(self):
        """Test minimum value validation."""
        schema = number(min_value=10)
        
        # Valid case
        result = schema.safe_parse(15)
        assert result["success"] is True
        
        # Invalid case
        result = schema.safe_parse(5)
        assert result["success"] is False
        assert result["issues"][0]["code"] == "too_small"
    
    def test_max_value(self):
        """Test maximum value validation."""
        schema = number(max_value=100)
        
        # Valid case
        result = schema.safe_parse(50)
        assert result["success"] is True
        
        # Invalid case
        result = schema.safe_parse(150)
        assert result["success"] is False
        assert result["issues"][0]["code"] == "too_big"
    
    def test_json_schema_conversion(self):
        """Test JSON schema conversion."""
        schema = number(min_value=0, max_value=100)
        json_schema = schema.to_json_schema()
        
        expected = {
            "type": "number",
            "minimum": 0,
            "maximum": 100
        }
        assert json_schema == expected

class TestBooleanSchema:
    """Test boolean schema validation."""
    
    def test_valid_booleans(self):
        """Test valid boolean validation."""
        schema = boolean()
        
        # True
        result = schema.safe_parse(True)
        assert result["success"] is True
        assert result["output"] is True
        
        # False
        result = schema.safe_parse(False)
        assert result["success"] is True
        assert result["output"] is False
    
    def test_invalid_type(self):
        """Test invalid type validation."""
        schema = boolean()
        
        # String "true" should not be valid
        result = schema.safe_parse("true")
        assert result["success"] is False
        assert result["issues"][0]["code"] == "invalid_type"
        
        # Number should not be valid
        result = schema.safe_parse(1)
        assert result["success"] is False
        assert result["issues"][0]["code"] == "invalid_type"
    
    def test_json_schema_conversion(self):
        """Test JSON schema conversion."""
        schema = boolean()
        json_schema = schema.to_json_schema()
        
        expected = {"type": "boolean"}
        assert json_schema == expected

class TestObjectSchema:
    """Test object schema validation."""
    
    def test_valid_object(self):
        """Test valid object validation."""
        schema = object({
            "name": string(),
            "age": number()
        })
        
        data = {"name": "Alice", "age": 30}
        result = schema.safe_parse(data)
        assert result["success"] is True
        assert result["output"] == data
    
    def test_invalid_type(self):
        """Test invalid type validation."""
        schema = object({"name": string()})
        result = schema.safe_parse("not an object")
        assert result["success"] is False
        assert result["issues"][0]["code"] == "invalid_type"
    
    def test_missing_field(self):
        """Test missing required field."""
        schema = object({
            "name": string(),
            "age": number()
        })
        
        data = {"name": "Alice"}  # Missing age
        result = schema.safe_parse(data)
        assert result["success"] is False
        assert any(issue["code"] == "missing_field" for issue in result["issues"])
    
    def test_nested_validation_errors(self):
        """Test nested validation errors with proper paths."""
        schema = object({
            "user": object({
                "name": string(min_length=2),
                "age": number(min_value=0)
            })
        })
        
        data = {
            "user": {
                "name": "X",  # Too short
                "age": -5     # Too small
            }
        }
        
        result = schema.safe_parse(data)
        assert result["success"] is False
        assert len(result["issues"]) == 2
        
        # Check that paths are correctly set
        paths = [issue["path"] for issue in result["issues"]]
        assert ["user", "name"] in paths
        assert ["user", "age"] in paths
    
    def test_json_schema_conversion(self):
        """Test JSON schema conversion."""
        schema = object({
            "name": string(),
            "age": number()
        })
        
        json_schema = schema.to_json_schema()
        expected = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name", "age"],
            "additionalProperties": False
        }
        assert json_schema == expected

class TestArraySchema:
    """Test array schema validation."""
    
    def test_valid_array(self):
        """Test valid array validation."""
        schema = array(string())
        data = ["hello", "world"]
        result = schema.safe_parse(data)
        assert result["success"] is True
        assert result["output"] == data
    
    def test_invalid_type(self):
        """Test invalid type validation."""
        schema = array(string())
        result = schema.safe_parse("not an array")
        assert result["success"] is False
        assert result["issues"][0]["code"] == "invalid_type"
    
    def test_item_validation_errors(self):
        """Test item validation errors with proper paths."""
        schema = array(number(min_value=0))
        data = [5, -3, 10]  # -3 is invalid
        
        result = schema.safe_parse(data)
        assert result["success"] is False
        assert len(result["issues"]) == 1
        assert result["issues"][0]["path"] == [1]  # Index 1 has the error
    
    def test_json_schema_conversion(self):
        """Test JSON schema conversion."""
        schema = array(string())
        json_schema = schema.to_json_schema()
        
        expected = {
            "type": "array",
            "items": {"type": "string"}
        }
        assert json_schema == expected

class TestValiPythonSchemaIntegration:
    """Test integration with AI SDK schema system."""
    
    def test_ai_sdk_integration(self):
        """Test Valibot schema integration with AI SDK."""
        vali_schema = object({
            "name": string(),
            "count": number()
        })
        
        ai_schema = valibot_schema(vali_schema)
        
        # Valid data
        valid_data = {"name": "test", "count": 5}
        result = ai_schema.validate(valid_data)
        assert result.success is True
        assert result.data == valid_data
        
        # Invalid data
        invalid_data = {"name": "test", "count": "not a number"}
        result = ai_schema.validate(invalid_data)
        assert result.success is False
        assert isinstance(result.error, ValiError)
    
    def test_json_schema_conversion(self):
        """Test JSON schema conversion through AI SDK."""
        vali_schema = object({
            "title": string(min_length=1),
            "priority": number(min_value=1, max_value=5)
        })
        
        ai_schema = valibot_schema(vali_schema)
        json_schema = ai_schema.to_json_schema()
        
        expected = {
            "type": "object",
            "properties": {
                "title": {"type": "string", "minLength": 1},
                "priority": {"type": "number", "minimum": 1, "maximum": 5}
            },
            "required": ["title", "priority"],
            "additionalProperties": False
        }
        assert json_schema == expected

class TestComplexScenarios:
    """Test complex real-world scenarios."""
    
    def test_nested_complex_schema(self):
        """Test deeply nested schema validation."""
        schema = object({
            "users": array(
                object({
                    "id": string(),
                    "profile": object({
                        "name": string(min_length=1),
                        "age": number(min_value=0, max_value=150),
                        "active": boolean()
                    }),
                    "tags": array(string())
                })
            ),
            "metadata": object({
                "total": number(min_value=0),
                "page": number(min_value=1)
            })
        })
        
        valid_data = {
            "users": [
                {
                    "id": "user-1",
                    "profile": {
                        "name": "Alice",
                        "age": 30,
                        "active": True
                    },
                    "tags": ["developer", "python"]
                }
            ],
            "metadata": {
                "total": 1,
                "page": 1
            }
        }
        
        result = schema.safe_parse(valid_data)
        assert result["success"] is True
        assert result["output"] == valid_data
    
    def test_error_aggregation(self):
        """Test that multiple errors are properly aggregated."""
        schema = object({
            "name": string(min_length=5),
            "age": number(min_value=18, max_value=65),
            "email": string(min_length=5)
        })
        
        invalid_data = {
            "name": "Jo",      # Too short
            "age": 15,         # Too young
            "email": "a@b"     # Too short
        }
        
        result = schema.safe_parse(invalid_data)
        assert result["success"] is False
        assert len(result["issues"]) == 3  # All three fields should have errors

if __name__ == "__main__":
    pytest.main([__file__, "-v"])