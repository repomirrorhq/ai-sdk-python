"""Marshmallow schema validation adapter for AI SDK Python."""

from typing import Any, Dict, Type, TypeVar

try:
    from marshmallow import Schema, ValidationError as MarshmallowValidationError, fields
    from marshmallow.schema import SchemaMeta
    MARSHMALLOW_AVAILABLE = True
except ImportError:
    Schema = object
    MarshmallowValidationError = Exception
    fields = object
    SchemaMeta = object
    MARSHMALLOW_AVAILABLE = False

from .base import BaseSchema, ValidationResult, ValidationError

T = TypeVar('T')


class MarshmallowSchema(BaseSchema[Dict[str, Any]]):
    """Marshmallow-based schema validator.
    
    Wraps Marshmallow schemas to provide a unified schema interface.
    """
    
    def __init__(self, schema: Schema):
        if not MARSHMALLOW_AVAILABLE:
            raise ImportError(
                "Marshmallow is required for MarshmallowSchema. "
                "Install it with: pip install marshmallow"
            )
        
        if not isinstance(schema, Schema):
            raise ValueError("schema must be a Marshmallow Schema instance")
        
        self.schema = schema
    
    def validate(self, data: Any) -> ValidationResult[Dict[str, Any]]:
        """Validate data using Marshmallow schema.
        
        Args:
            data: The data to validate
            
        Returns:
            ValidationResult with validated data or error
        """
        try:
            validated = self.schema.load(data)
            return ValidationResult(success=True, value=validated)
        except MarshmallowValidationError as e:
            error = ValidationError(
                message=f"Marshmallow validation failed: {e}",
                errors=e.messages if hasattr(e, 'messages') else {}
            )
            return ValidationResult(success=False, error=error)
        except Exception as e:
            error = ValidationError(f"Unexpected validation error: {e}")
            return ValidationResult(success=False, error=error)
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert Marshmallow schema to JSON Schema.
        
        Note: This is a basic conversion that may not cover all Marshmallow features.
        
        Returns:
            JSON Schema dictionary
        """
        if not MARSHMALLOW_AVAILABLE:
            return {}
        
        json_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Convert Marshmallow fields to JSON Schema properties
        for field_name, field_obj in self.schema.fields.items():
            property_schema = self._convert_field_to_json_schema(field_obj)
            json_schema["properties"][field_name] = property_schema
            
            # Check if field is required
            if field_obj.required:
                json_schema["required"].append(field_name)
        
        if not json_schema["required"]:
            del json_schema["required"]
        
        return json_schema
    
    def _convert_field_to_json_schema(self, field) -> Dict[str, Any]:
        """Convert a Marshmallow field to JSON Schema property."""
        if not MARSHMALLOW_AVAILABLE:
            return {"type": "string"}
        
        # Basic field type mappings
        field_mappings = {
            fields.String: {"type": "string"},
            fields.Integer: {"type": "integer"},
            fields.Float: {"type": "number"},
            fields.Boolean: {"type": "boolean"},
            fields.List: {"type": "array"},
            fields.Dict: {"type": "object"},
            fields.Email: {"type": "string", "format": "email"},
            fields.Url: {"type": "string", "format": "uri"},
            fields.DateTime: {"type": "string", "format": "date-time"},
            fields.Date: {"type": "string", "format": "date"},
            fields.Time: {"type": "string", "format": "time"},
        }
        
        for field_type, schema in field_mappings.items():
            if isinstance(field, field_type):
                result = schema.copy()
                
                # Add description if available
                if hasattr(field, 'metadata') and 'description' in field.metadata:
                    result["description"] = field.metadata['description']
                
                # Handle List fields
                if isinstance(field, fields.List) and hasattr(field, 'inner'):
                    result["items"] = self._convert_field_to_json_schema(field.inner)
                
                return result
        
        # Default fallback
        return {"type": "string", "description": f"Marshmallow field: {type(field).__name__}"}
    
    @property
    def schema_type(self) -> str:
        """Get schema type identifier."""
        return "marshmallow"
    
    def __repr__(self) -> str:
        return f"MarshmallowSchema({self.schema.__class__.__name__})"


def marshmallow_schema(schema: Schema) -> MarshmallowSchema:
    """Create a Marshmallow schema validator.
    
    Args:
        schema: Marshmallow Schema instance
        
    Returns:
        MarshmallowSchema validator
        
    Example:
        from marshmallow import Schema, fields
        
        class UserSchema(Schema):
            name = fields.String(required=True)
            age = fields.Integer(required=True)
            
        schema = marshmallow_schema(UserSchema())
        result = schema.validate({"name": "Alice", "age": 30})
    """
    return MarshmallowSchema(schema)