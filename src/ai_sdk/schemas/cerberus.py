"""Cerberus schema validation adapter for AI SDK Python."""

from typing import Any, Dict

try:
    from cerberus import Validator, ValidationError as CerberusValidationError
    CERBERUS_AVAILABLE = True
except ImportError:
    Validator = object
    CerberusValidationError = Exception
    CERBERUS_AVAILABLE = False

from .base import BaseSchema, ValidationResult, ValidationError


class CerberusSchema(BaseSchema[Dict[str, Any]]):
    """Cerberus-based schema validator.
    
    Uses Cerberus validation rules to validate data.
    """
    
    def __init__(self, schema: Dict[str, Any]):
        if not CERBERUS_AVAILABLE:
            raise ImportError(
                "Cerberus is required for CerberusSchema. "
                "Install it with: pip install cerberus"
            )
        
        self.schema = schema
        self.validator = Validator(schema)
    
    def validate(self, data: Any) -> ValidationResult[Dict[str, Any]]:
        """Validate data using Cerberus schema.
        
        Args:
            data: The data to validate
            
        Returns:
            ValidationResult with validated data or error
        """
        try:
            if not isinstance(data, dict):
                error = ValidationError("Cerberus validation requires dictionary input")
                return ValidationResult(success=False, error=error)
            
            if self.validator.validate(data):
                # Return normalized data if available, otherwise original
                validated_data = self.validator.normalized(data) or data
                return ValidationResult(success=True, value=validated_data)
            else:
                error = ValidationError(
                    message=f"Cerberus validation failed",
                    errors=self.validator.errors
                )
                return ValidationResult(success=False, error=error)
        except Exception as e:
            error = ValidationError(f"Unexpected validation error: {e}")
            return ValidationResult(success=False, error=error)
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert Cerberus schema to JSON Schema.
        
        Note: This is a basic conversion that may not cover all Cerberus features.
        
        Returns:
            JSON Schema dictionary
        """
        if not CERBERUS_AVAILABLE:
            return {}
        
        json_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Convert Cerberus schema to JSON Schema
        for field_name, field_config in self.schema.items():
            property_schema = self._convert_field_to_json_schema(field_config)
            json_schema["properties"][field_name] = property_schema
            
            # Check if field is required
            if isinstance(field_config, dict) and field_config.get('required', False):
                json_schema["required"].append(field_name)
        
        if not json_schema["required"]:
            del json_schema["required"]
        
        return json_schema
    
    def _convert_field_to_json_schema(self, field_config: Any) -> Dict[str, Any]:
        """Convert a Cerberus field configuration to JSON Schema property."""
        if not isinstance(field_config, dict):
            return {"type": "string", "description": f"Cerberus field: {field_config}"}
        
        # Basic type mappings
        type_mappings = {
            'string': {"type": "string"},
            'integer': {"type": "integer"},
            'float': {"type": "number"},
            'number': {"type": "number"},
            'boolean': {"type": "boolean"},
            'dict': {"type": "object"},
            'list': {"type": "array"},
            'datetime': {"type": "string", "format": "date-time"},
            'date': {"type": "string", "format": "date"},
        }
        
        result = {}
        
        # Handle type
        cerberus_type = field_config.get('type')
        if cerberus_type in type_mappings:
            result.update(type_mappings[cerberus_type])
        else:
            result["type"] = "string"  # fallback
        
        # Handle common properties
        if 'min' in field_config:
            result["minimum"] = field_config['min']
        if 'max' in field_config:
            result["maximum"] = field_config['max']
        if 'minlength' in field_config:
            result["minLength"] = field_config['minlength']
        if 'maxlength' in field_config:
            result["maxLength"] = field_config['maxlength']
        if 'allowed' in field_config:
            result["enum"] = field_config['allowed']
        if 'default' in field_config:
            result["default"] = field_config['default']
        
        # Handle nested schemas
        if 'schema' in field_config:
            if result.get("type") == "object":
                nested_schema = self._convert_schema_to_json_schema(field_config['schema'])
                result.update(nested_schema)
            elif result.get("type") == "array":
                nested_schema = self._convert_schema_to_json_schema(field_config['schema'])
                result["items"] = nested_schema
        
        return result
    
    def _convert_schema_to_json_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a nested Cerberus schema to JSON Schema."""
        result = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for field_name, field_config in schema.items():
            result["properties"][field_name] = self._convert_field_to_json_schema(field_config)
            
            if isinstance(field_config, dict) and field_config.get('required', False):
                result["required"].append(field_name)
        
        if not result["required"]:
            del result["required"]
        
        return result
    
    @property
    def schema_type(self) -> str:
        """Get schema type identifier."""
        return "cerberus"
    
    def __repr__(self) -> str:
        return f"CerberusSchema(fields={len(self.schema)})"


def cerberus_schema(schema: Dict[str, Any]) -> CerberusSchema:
    """Create a Cerberus schema validator.
    
    Args:
        schema: Cerberus schema dictionary
        
    Returns:
        CerberusSchema validator
        
    Example:
        schema = {
            'name': {'type': 'string', 'required': True},
            'age': {'type': 'integer', 'min': 0, 'required': True},
            'email': {'type': 'string', 'regex': r'^.+@.+\\.+$'}
        }
        
        validator = cerberus_schema(schema)
        result = validator.validate({"name": "Alice", "age": 30, "email": "alice@example.com"})
    """
    return CerberusSchema(schema)