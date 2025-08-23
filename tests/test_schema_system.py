"""Tests for the enhanced schema validation system."""

import pytest
from typing import Dict, Any, List

from ai_sdk.schemas import (
    BaseSchema, ValidationResult, SchemaValidationError,
    PydanticSchema, pydantic_schema,
    JSONSchemaValidator, jsonschema_schema
)

# Test with optional imports
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    BaseModel = object
    Field = None
    PYDANTIC_AVAILABLE = False

try:
    from ai_sdk.schemas import MarshmallowSchema, marshmallow_schema
    from marshmallow import Schema, fields
    MARSHMALLOW_AVAILABLE = True
except ImportError:
    MarshmallowSchema = None
    marshmallow_schema = None
    Schema = object
    fields = object
    MARSHMALLOW_AVAILABLE = False

try:
    from ai_sdk.schemas import CerberusSchema, cerberus_schema
    CERBERUS_AVAILABLE = True
except ImportError:
    CerberusSchema = None
    cerberus_schema = None
    CERBERUS_AVAILABLE = False


class TestBaseSchema:
    """Test the base schema interface."""
    
    def test_validation_result(self):
        """Test ValidationResult class."""
        # Test successful result
        result = ValidationResult(success=True, value={"test": "data"})
        assert result.success is True
        assert result.is_valid is True
        assert result.value == {"test": "data"}
        assert result.error is None
        
        # Test error result
        error = SchemaValidationError("Test error")
        result = ValidationResult(success=False, error=error)
        assert result.success is False
        assert result.is_valid is False
        assert result.value is None
        assert result.error == error
    
    def test_schema_validation_error(self):
        """Test SchemaValidationError class."""
        error = SchemaValidationError("Test message", {"field": "error"})
        assert str(error) == "Test message"
        assert error.errors == {"field": "error"}


@pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
class TestPydanticSchema:
    """Test Pydantic schema validation."""
    
    def test_pydantic_schema_creation(self):
        """Test creating a Pydantic schema."""
        class TestModel(BaseModel):
            name: str = Field(description="Name field")
            age: int = Field(description="Age field", ge=0)
        
        schema = pydantic_schema(TestModel)
        assert isinstance(schema, PydanticSchema)
        assert schema.schema_type == "pydantic"
        assert schema.model_class == TestModel
    
    def test_pydantic_validation_success(self):
        """Test successful Pydantic validation."""
        class TestModel(BaseModel):
            name: str
            age: int
        
        schema = pydantic_schema(TestModel)
        result = schema.validate({"name": "Alice", "age": 30})
        
        assert result.success is True
        assert result.error is None
        assert isinstance(result.value, TestModel)
        assert result.value.name == "Alice"
        assert result.value.age == 30
    
    def test_pydantic_validation_failure(self):
        """Test failed Pydantic validation."""
        class TestModel(BaseModel):
            name: str
            age: int
        
        schema = pydantic_schema(TestModel)
        
        # Missing required field
        result = schema.validate({"name": "Alice"})
        assert result.success is False
        assert result.error is not None
        assert "validation failed" in str(result.error).lower()
        
        # Invalid type
        result = schema.validate({"name": "Alice", "age": "not_an_int"})
        assert result.success is False
        assert result.error is not None
    
    def test_pydantic_json_schema_conversion(self):
        """Test converting Pydantic model to JSON Schema."""
        class TestModel(BaseModel):
            name: str = Field(description="Name field")
            age: int = Field(description="Age field", ge=0)
        
        schema = pydantic_schema(TestModel)
        json_schema = schema.to_json_schema()
        
        assert isinstance(json_schema, dict)
        assert "type" in json_schema
        assert "properties" in json_schema
        assert "name" in json_schema["properties"]
        assert "age" in json_schema["properties"]
    
    def test_pydantic_call_interface(self):
        """Test calling schema directly for validation."""
        class TestModel(BaseModel):
            name: str
            age: int
        
        schema = pydantic_schema(TestModel)
        
        # Valid data
        result = schema({"name": "Alice", "age": 30})
        assert isinstance(result, TestModel)
        assert result.name == "Alice"
        
        # Invalid data should raise exception
        with pytest.raises(SchemaValidationError):
            schema({"name": "Alice"})  # Missing age


class TestJSONSchemaValidator:
    """Test JSON Schema validation."""
    
    def test_jsonschema_creation(self):
        """Test creating a JSON Schema validator."""
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name", "age"]
        }
        
        schema = jsonschema_schema(schema_dict)
        assert isinstance(schema, JSONSchemaValidator)
        assert schema.schema_type == "jsonschema"
        assert schema.schema == schema_dict
    
    def test_jsonschema_validation_success(self):
        """Test successful JSON Schema validation."""
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name", "age"]
        }
        
        schema = jsonschema_schema(schema_dict)
        result = schema.validate({"name": "Alice", "age": 30})
        
        assert result.success is True
        assert result.error is None
        assert result.value == {"name": "Alice", "age": 30}
    
    def test_jsonschema_validation_failure(self):
        """Test failed JSON Schema validation."""
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name", "age"]
        }
        
        schema = jsonschema_schema(schema_dict)
        
        # Missing required field
        result = schema.validate({"name": "Alice"})
        assert result.success is False
        assert result.error is not None
        
        # Invalid type
        result = schema.validate({"name": "Alice", "age": "not_an_int"})
        assert result.success is False
        assert result.error is not None
    
    def test_jsonschema_to_json_schema(self):
        """Test JSON Schema to JSON Schema conversion (identity)."""
        schema_dict = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        schema = jsonschema_schema(schema_dict)
        result = schema.to_json_schema()
        
        assert result == schema_dict
        assert result is not schema_dict  # Should be a copy
    
    def test_invalid_schema_creation(self):
        """Test creating validator with invalid schema."""
        invalid_schema = {"type": "invalid_type"}
        
        with pytest.raises(ValueError):
            jsonschema_schema(invalid_schema)


@pytest.mark.skipif(not MARSHMALLOW_AVAILABLE, reason="Marshmallow not available")
class TestMarshmallowSchema:
    """Test Marshmallow schema validation."""
    
    def test_marshmallow_schema_creation(self):
        """Test creating a Marshmallow schema."""
        class TestSchema(Schema):
            name = fields.String(required=True)
            age = fields.Integer(required=True)
        
        schema = marshmallow_schema(TestSchema())
        assert isinstance(schema, MarshmallowSchema)
        assert schema.schema_type == "marshmallow"
    
    def test_marshmallow_validation_success(self):
        """Test successful Marshmallow validation."""
        class TestSchema(Schema):
            name = fields.String(required=True)
            age = fields.Integer(required=True)
        
        schema = marshmallow_schema(TestSchema())
        result = schema.validate({"name": "Alice", "age": 30})
        
        assert result.success is True
        assert result.error is None
        assert result.value == {"name": "Alice", "age": 30}
    
    def test_marshmallow_validation_failure(self):
        """Test failed Marshmallow validation."""
        class TestSchema(Schema):
            name = fields.String(required=True)
            age = fields.Integer(required=True)
        
        schema = marshmallow_schema(TestSchema())
        
        # Missing required field
        result = schema.validate({"name": "Alice"})
        assert result.success is False
        assert result.error is not None
        
        # Invalid type
        result = schema.validate({"name": "Alice", "age": "not_an_int"})
        assert result.success is False
        assert result.error is not None
    
    def test_marshmallow_json_schema_conversion(self):
        """Test converting Marshmallow schema to JSON Schema."""
        class TestSchema(Schema):
            name = fields.String(required=True, metadata={'description': 'Name field'})
            age = fields.Integer(required=True)
            email = fields.Email()
        
        schema = marshmallow_schema(TestSchema())
        json_schema = schema.to_json_schema()
        
        assert isinstance(json_schema, dict)
        assert json_schema["type"] == "object"
        assert "properties" in json_schema
        assert "name" in json_schema["properties"]
        assert "age" in json_schema["properties"]
        assert "email" in json_schema["properties"]
        assert "required" in json_schema
        assert set(json_schema["required"]) == {"name", "age"}


@pytest.mark.skipif(not CERBERUS_AVAILABLE, reason="Cerberus not available")  
class TestCerberusSchema:
    """Test Cerberus schema validation."""
    
    def test_cerberus_schema_creation(self):
        """Test creating a Cerberus schema."""
        schema_dict = {
            'name': {'type': 'string', 'required': True},
            'age': {'type': 'integer', 'required': True, 'min': 0}
        }
        
        schema = cerberus_schema(schema_dict)
        assert isinstance(schema, CerberusSchema)
        assert schema.schema_type == "cerberus"
        assert schema.schema == schema_dict
    
    def test_cerberus_validation_success(self):
        """Test successful Cerberus validation."""
        schema_dict = {
            'name': {'type': 'string', 'required': True},
            'age': {'type': 'integer', 'required': True, 'min': 0}
        }
        
        schema = cerberus_schema(schema_dict)
        result = schema.validate({"name": "Alice", "age": 30})
        
        assert result.success is True
        assert result.error is None
        assert result.value == {"name": "Alice", "age": 30}
    
    def test_cerberus_validation_failure(self):
        """Test failed Cerberus validation."""
        schema_dict = {
            'name': {'type': 'string', 'required': True},
            'age': {'type': 'integer', 'required': True, 'min': 0}
        }
        
        schema = cerberus_schema(schema_dict)
        
        # Missing required field
        result = schema.validate({"name": "Alice"})
        assert result.success is False
        assert result.error is not None
        
        # Invalid constraint
        result = schema.validate({"name": "Alice", "age": -1})
        assert result.success is False
        assert result.error is not None
    
    def test_cerberus_non_dict_validation(self):
        """Test Cerberus validation with non-dict input."""
        schema_dict = {
            'name': {'type': 'string', 'required': True}
        }
        
        schema = cerberus_schema(schema_dict)
        result = schema.validate("not_a_dict")
        
        assert result.success is False
        assert result.error is not None
        assert "dictionary input" in str(result.error)
    
    def test_cerberus_json_schema_conversion(self):
        """Test converting Cerberus schema to JSON Schema."""
        schema_dict = {
            'name': {'type': 'string', 'required': True},
            'age': {'type': 'integer', 'required': True, 'min': 0, 'max': 150},
            'tags': {'type': 'list', 'schema': {'type': 'string'}}
        }
        
        schema = cerberus_schema(schema_dict)
        json_schema = schema.to_json_schema()
        
        assert isinstance(json_schema, dict)
        assert json_schema["type"] == "object"
        assert "properties" in json_schema
        assert "name" in json_schema["properties"]
        assert "age" in json_schema["properties"]
        assert "tags" in json_schema["properties"]
        assert "required" in json_schema
        assert set(json_schema["required"]) == {"name", "age"}
        
        # Check constraint conversion
        age_prop = json_schema["properties"]["age"]
        assert age_prop["type"] == "integer"
        assert age_prop["minimum"] == 0
        assert age_prop["maximum"] == 150
        
        # Check array type conversion
        tags_prop = json_schema["properties"]["tags"]
        assert tags_prop["type"] == "array"
        assert tags_prop["items"]["type"] == "string"


class TestSchemaIntegration:
    """Test integration between different schema types."""
    
    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_pydantic_with_generate_object_mock(self):
        """Test Pydantic schema integration with object generation (mock)."""
        class User(BaseModel):
            name: str
            age: int
            email: str
        
        schema = pydantic_schema(User)
        
        # Mock data that would come from AI
        mock_ai_response = {
            "name": "John Doe",
            "age": 25,
            "email": "john@example.com"
        }
        
        result = schema.validate(mock_ai_response)
        assert result.success
        assert isinstance(result.value, User)
        assert result.value.name == "John Doe"
    
    def test_jsonschema_with_complex_structure(self):
        """Test JSON Schema with complex nested structures."""
        schema_dict = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "preferences": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["name"]
                }
            },
            "required": ["user"]
        }
        
        schema = jsonschema_schema(schema_dict)
        
        valid_data = {
            "user": {
                "name": "Alice",
                "preferences": ["coding", "reading"]
            }
        }
        
        result = schema.validate(valid_data)
        assert result.success
        assert result.value == valid_data
    
    def test_error_handling_consistency(self):
        """Test that all schema types handle errors consistently."""
        # Test with JSON Schema
        json_schema = jsonschema_schema({
            "type": "object",
            "properties": {"required_field": {"type": "string"}},
            "required": ["required_field"]
        })
        
        result = json_schema.validate({})
        assert not result.success
        assert isinstance(result.error, SchemaValidationError)
        
        # Test Pydantic if available
        if PYDANTIC_AVAILABLE:
            class TestModel(BaseModel):
                required_field: str
            
            pydantic_schema_obj = pydantic_schema(TestModel)
            result = pydantic_schema_obj.validate({})
            assert not result.success
            assert isinstance(result.error, SchemaValidationError)