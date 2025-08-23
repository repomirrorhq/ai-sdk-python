"""Base schema interfaces and types for AI SDK Python schema validation."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar, Union
from dataclasses import dataclass

T = TypeVar('T')


class ValidationError(Exception):
    """Raised when schema validation fails."""
    
    def __init__(self, message: str, errors: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.errors = errors or {}


@dataclass
class ValidationResult(Generic[T]):
    """Result of schema validation."""
    
    success: bool
    value: Optional[T] = None
    error: Optional[ValidationError] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if validation was successful."""
        return self.success and self.error is None


class BaseSchema(ABC, Generic[T]):
    """Abstract base class for all schema validators.
    
    This provides a unified interface for schema validation across
    different Python validation libraries.
    """
    
    @abstractmethod
    def validate(self, data: Any) -> ValidationResult[T]:
        """Validate data against the schema.
        
        Args:
            data: The data to validate
            
        Returns:
            ValidationResult containing the validated data or error
        """
        pass
    
    @abstractmethod
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert schema to JSON Schema format.
        
        Returns:
            JSON Schema dictionary
        """
        pass
    
    @property
    @abstractmethod
    def schema_type(self) -> str:
        """Get the type of schema validator (e.g., 'pydantic', 'jsonschema')."""
        pass
    
    def __call__(self, data: Any) -> T:
        """Convenient validation method that raises on error.
        
        Args:
            data: The data to validate
            
        Returns:
            The validated data
            
        Raises:
            ValidationError: If validation fails
        """
        result = self.validate(data)
        if not result.success or result.error:
            raise result.error or ValidationError("Validation failed")
        return result.value