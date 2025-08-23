"""JSONSchema validation adapter for AI SDK Python."""

from typing import Any, Dict, Optional

try:
    import jsonschema
    from jsonschema import validate, ValidationError as JSONSchemaValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    jsonschema = None
    validate = None
    JSONSchemaValidationError = Exception  
    JSONSCHEMA_AVAILABLE = False

from .base import BaseSchema, ValidationResult, ValidationError


class JSONSchemaValidator(BaseSchema[Dict[str, Any]]):
    """JSONSchema-based validator.
    
    Uses the jsonschema library to validate data against JSON Schema specifications.
    """
    
    def __init__(self, schema: Dict[str, Any], draft: Optional[str] = None):
        if not JSONSCHEMA_AVAILABLE:
            raise ImportError(
                "jsonschema is required for JSONSchemaValidator. "
                "Install it with: pip install jsonschema"
            )
        
        self.schema = schema
        self.draft = draft or "draft7"
        
        # Validate the schema itself
        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except Exception as e:
            raise ValueError(f"Invalid JSON Schema: {e}")
    
    def validate(self, data: Any) -> ValidationResult[Dict[str, Any]]:
        """Validate data against JSON Schema.
        
        Args:
            data: The data to validate
            
        Returns:
            ValidationResult with validated data or error
        """
        try:
            validate(instance=data, schema=self.schema)
            return ValidationResult(success=True, value=data)
        except JSONSchemaValidationError as e:
            error = ValidationError(
                message=f"JSON Schema validation failed: {e.message}",
                errors={"path": list(e.absolute_path), "message": e.message}
            )
            return ValidationResult(success=False, error=error)
        except Exception as e:
            error = ValidationError(f"Unexpected validation error: {e}")
            return ValidationResult(success=False, error=error)
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Return the JSON Schema.
        
        Returns:
            The JSON Schema dictionary
        """
        return self.schema.copy()
    
    @property
    def schema_type(self) -> str:
        """Get schema type identifier."""
        return "jsonschema"
    
    def __repr__(self) -> str:
        return f"JSONSchemaValidator(draft={self.draft})"


def jsonschema_schema(schema: Dict[str, Any], draft: Optional[str] = None) -> JSONSchemaValidator:
    """Create a JSON Schema validator.
    
    Args:
        schema: JSON Schema dictionary
        draft: JSON Schema draft version (default: "draft7")
        
    Returns:
        JSONSchemaValidator instance
        
    Example:
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name"]
        }
        
        validator = jsonschema_schema(schema)
        result = validator.validate({"name": "Alice", "age": 30})
    """
    return JSONSchemaValidator(schema, draft)