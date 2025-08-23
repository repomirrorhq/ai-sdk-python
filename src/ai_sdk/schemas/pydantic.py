"""Pydantic schema validation adapter for AI SDK Python."""

from typing import Any, Dict, Type, TypeVar

try:
    from pydantic import BaseModel, ValidationError as PydanticValidationError
    from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
    PYDANTIC_AVAILABLE = True
except ImportError:
    BaseModel = object
    PydanticValidationError = Exception
    GenerateJsonSchema = object
    JsonSchemaValue = Any
    PYDANTIC_AVAILABLE = False

from .base import BaseSchema, ValidationResult, ValidationError

T = TypeVar('T', bound=BaseModel)


class PydanticSchema(BaseSchema[T]):
    """Pydantic-based schema validator.
    
    Wraps Pydantic models to provide a unified schema interface.
    """
    
    def __init__(self, model_class: Type[T]):
        if not PYDANTIC_AVAILABLE:
            raise ImportError(
                "Pydantic is required for PydanticSchema. "
                "Install it with: pip install pydantic"
            )
        
        if not issubclass(model_class, BaseModel):
            raise ValueError("model_class must be a Pydantic BaseModel subclass")
        
        self.model_class = model_class
    
    def validate(self, data: Any) -> ValidationResult[T]:
        """Validate data using Pydantic model.
        
        Args:
            data: The data to validate
            
        Returns:
            ValidationResult with validated model instance or error
        """
        try:
            if isinstance(data, dict):
                validated = self.model_class.model_validate(data)
            else:
                validated = self.model_class.model_validate_json(data)
            return ValidationResult(success=True, value=validated)
        except PydanticValidationError as e:
            error = ValidationError(
                message=f"Pydantic validation failed: {e}",
                errors=e.errors() if hasattr(e, 'errors') else {}
            )
            return ValidationResult(success=False, error=error)
        except Exception as e:
            error = ValidationError(f"Unexpected validation error: {e}")
            return ValidationResult(success=False, error=error)
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert Pydantic model to JSON Schema.
        
        Returns:
            JSON Schema dictionary
        """
        if not PYDANTIC_AVAILABLE:
            return {}
        
        try:
            return self.model_class.model_json_schema()
        except Exception:
            # Fallback for older Pydantic versions
            try:
                return self.model_class.schema()
            except Exception:
                return {"type": "object", "description": f"Schema for {self.model_class.__name__}"}
    
    @property
    def schema_type(self) -> str:
        """Get schema type identifier."""
        return "pydantic"
    
    def __repr__(self) -> str:
        return f"PydanticSchema({self.model_class.__name__})"


def pydantic_schema(model_class: Type[T]) -> PydanticSchema[T]:
    """Create a Pydantic schema validator.
    
    Args:
        model_class: Pydantic BaseModel class
        
    Returns:
        PydanticSchema validator
        
    Example:
        from pydantic import BaseModel
        
        class User(BaseModel):
            name: str
            age: int
            
        schema = pydantic_schema(User)
        result = schema.validate({"name": "Alice", "age": 30})
    """
    return PydanticSchema(model_class)