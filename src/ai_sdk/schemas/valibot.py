"""
Valibot-style schema validation for AI SDK Python.

This module provides a Valibot-inspired schema validation system for Python,
offering a similar API to the TypeScript Valibot library while leveraging
Python's type system and validation capabilities.

Note: This is not a direct port of Valibot, but rather a Python-native
implementation that provides similar functionality and API patterns.
"""

import json
from typing import Any, Dict, List, Union, Optional, Callable, TypeVar, Generic, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod

try:
    from .base import BaseSchema, ValidationResult, ValidationError
except ImportError:
    # For standalone testing - define minimal base classes
    T_co = TypeVar('T_co', covariant=True)
    
    class ValidationError(Exception):
        """Base validation error."""
        pass
    
    class ValidationResult(Generic[T_co]):
        """Validation result container."""
        def __init__(self, success: bool, data: Any = None, error: Exception = None):
            self.success = success
            self.data = data
            self.error = error
    
    class BaseSchema(ABC, Generic[T_co]):
        """Base schema class."""
        @abstractmethod
        def validate(self, data: Any) -> ValidationResult[T_co]:
            pass
        
        @abstractmethod
        def to_json_schema(self) -> Dict[str, Any]:
            pass

T = TypeVar('T')

class ValiError(ValidationError):
    """Error raised when Valibot-style validation fails."""
    
    def __init__(self, issues: List[Dict[str, Any]]):
        self.issues = issues
        message = f"Validation failed with {len(issues)} issue(s)"
        super().__init__(message)

@dataclass
class ValidationIssue:
    """Represents a validation issue in Valibot style."""
    code: str
    message: str
    path: Optional[List[Union[str, int]]] = None
    input: Any = None
    expected: Optional[str] = None
    received: Optional[str] = None

class ValiSchema(ABC, Generic[T]):
    """Base class for Valibot-style schemas."""
    
    @abstractmethod
    def parse(self, value: Any) -> T:
        """Parse and validate a value, raising ValiError on failure."""
        pass
    
    @abstractmethod
    def safe_parse(self, value: Any) -> Dict[str, Any]:
        """Safely parse a value, returning result with success/error info."""
        pass
    
    @abstractmethod
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert schema to JSON Schema format."""
        pass

class StringSchema(ValiSchema[str]):
    """String validation schema."""
    
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None):
        self.min_length = min_length
        self.max_length = max_length
    
    def parse(self, value: Any) -> str:
        result = self.safe_parse(value)
        if result["success"]:
            return result["output"]
        else:
            raise ValiError(result["issues"])
    
    def safe_parse(self, value: Any) -> Dict[str, Any]:
        issues = []
        
        if not isinstance(value, str):
            issues.append({
                "code": "invalid_type",
                "message": f"Expected string, received {type(value).__name__}",
                "input": value,
                "expected": "string",
                "received": type(value).__name__
            })
            return {"success": False, "issues": issues}
        
        if self.min_length is not None and len(value) < self.min_length:
            issues.append({
                "code": "too_small",
                "message": f"String must be at least {self.min_length} characters long",
                "input": value,
                "expected": f"length >= {self.min_length}",
                "received": f"length = {len(value)}"
            })
        
        if self.max_length is not None and len(value) > self.max_length:
            issues.append({
                "code": "too_big", 
                "message": f"String must be at most {self.max_length} characters long",
                "input": value,
                "expected": f"length <= {self.max_length}",
                "received": f"length = {len(value)}"
            })
        
        if issues:
            return {"success": False, "issues": issues}
        
        return {"success": True, "output": value}
    
    def to_json_schema(self) -> Dict[str, Any]:
        schema = {"type": "string"}
        if self.min_length is not None:
            schema["minLength"] = self.min_length
        if self.max_length is not None:
            schema["maxLength"] = self.max_length
        return schema

class NumberSchema(ValiSchema[Union[int, float]]):
    """Number validation schema."""
    
    def __init__(self, min_value: Optional[Union[int, float]] = None, 
                 max_value: Optional[Union[int, float]] = None):
        self.min_value = min_value
        self.max_value = max_value
    
    def parse(self, value: Any) -> Union[int, float]:
        result = self.safe_parse(value)
        if result["success"]:
            return result["output"]
        else:
            raise ValiError(result["issues"])
    
    def safe_parse(self, value: Any) -> Dict[str, Any]:
        issues = []
        
        if not isinstance(value, (int, float)):
            issues.append({
                "code": "invalid_type",
                "message": f"Expected number, received {type(value).__name__}",
                "input": value,
                "expected": "number",
                "received": type(value).__name__
            })
            return {"success": False, "issues": issues}
        
        if self.min_value is not None and value < self.min_value:
            issues.append({
                "code": "too_small",
                "message": f"Number must be at least {self.min_value}",
                "input": value,
                "expected": f">= {self.min_value}",
                "received": str(value)
            })
        
        if self.max_value is not None and value > self.max_value:
            issues.append({
                "code": "too_big",
                "message": f"Number must be at most {self.max_value}",
                "input": value,
                "expected": f"<= {self.max_value}",
                "received": str(value)
            })
        
        if issues:
            return {"success": False, "issues": issues}
        
        return {"success": True, "output": value}
    
    def to_json_schema(self) -> Dict[str, Any]:
        schema = {"type": "number"}
        if self.min_value is not None:
            schema["minimum"] = self.min_value
        if self.max_value is not None:
            schema["maximum"] = self.max_value
        return schema

class BooleanSchema(ValiSchema[bool]):
    """Boolean validation schema."""
    
    def parse(self, value: Any) -> bool:
        result = self.safe_parse(value)
        if result["success"]:
            return result["output"]
        else:
            raise ValiError(result["issues"])
    
    def safe_parse(self, value: Any) -> Dict[str, Any]:
        if not isinstance(value, bool):
            return {
                "success": False, 
                "issues": [{
                    "code": "invalid_type",
                    "message": f"Expected boolean, received {type(value).__name__}",
                    "input": value,
                    "expected": "boolean",
                    "received": type(value).__name__
                }]
            }
        
        return {"success": True, "output": value}
    
    def to_json_schema(self) -> Dict[str, Any]:
        return {"type": "boolean"}

class ObjectSchema(ValiSchema[Dict[str, Any]]):
    """Object validation schema."""
    
    def __init__(self, shape: Dict[str, ValiSchema]):
        self.shape = shape
    
    def parse(self, value: Any) -> Dict[str, Any]:
        result = self.safe_parse(value)
        if result["success"]:
            return result["output"]
        else:
            raise ValiError(result["issues"])
    
    def safe_parse(self, value: Any) -> Dict[str, Any]:
        issues = []
        
        if not isinstance(value, dict):
            return {
                "success": False,
                "issues": [{
                    "code": "invalid_type",
                    "message": f"Expected object, received {type(value).__name__}",
                    "input": value,
                    "expected": "object",
                    "received": type(value).__name__
                }]
            }
        
        output = {}
        
        for key, schema in self.shape.items():
            if key in value:
                field_result = schema.safe_parse(value[key])
                if field_result["success"]:
                    output[key] = field_result["output"]
                else:
                    # Add path information to issues
                    for issue in field_result["issues"]:
                        issue["path"] = [key] + (issue.get("path", []))
                    issues.extend(field_result["issues"])
            else:
                issues.append({
                    "code": "missing_field",
                    "message": f"Required field '{key}' is missing",
                    "path": [key],
                    "expected": "required field",
                    "received": "undefined"
                })
        
        if issues:
            return {"success": False, "issues": issues}
        
        return {"success": True, "output": output}
    
    def to_json_schema(self) -> Dict[str, Any]:
        properties = {}
        required = []
        
        for key, schema in self.shape.items():
            properties[key] = schema.to_json_schema()
            required.append(key)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False
        }

class ArraySchema(ValiSchema[List[Any]]):
    """Array validation schema."""
    
    def __init__(self, item_schema: ValiSchema):
        self.item_schema = item_schema
    
    def parse(self, value: Any) -> List[Any]:
        result = self.safe_parse(value)
        if result["success"]:
            return result["output"]
        else:
            raise ValiError(result["issues"])
    
    def safe_parse(self, value: Any) -> Dict[str, Any]:
        issues = []
        
        if not isinstance(value, list):
            return {
                "success": False,
                "issues": [{
                    "code": "invalid_type",
                    "message": f"Expected array, received {type(value).__name__}",
                    "input": value,
                    "expected": "array",
                    "received": type(value).__name__
                }]
            }
        
        output = []
        
        for i, item in enumerate(value):
            item_result = self.item_schema.safe_parse(item)
            if item_result["success"]:
                output.append(item_result["output"])
            else:
                # Add path information to issues
                for issue in item_result["issues"]:
                    issue["path"] = [i] + (issue.get("path", []))
                issues.extend(item_result["issues"])
        
        if issues:
            return {"success": False, "issues": issues}
        
        return {"success": True, "output": output}
    
    def to_json_schema(self) -> Dict[str, Any]:
        return {
            "type": "array",
            "items": self.item_schema.to_json_schema()
        }

class ValiPythonSchema(BaseSchema[T]):
    """Adapter to make Valibot-style schemas work with AI SDK schema system."""
    
    def __init__(self, vali_schema: ValiSchema[T]):
        self.vali_schema = vali_schema
    
    def validate(self, data: Any) -> ValidationResult[T]:
        """Validate data using the Valibot schema."""
        try:
            result = self.vali_schema.safe_parse(data)
            if result["success"]:
                return ValidationResult(success=True, data=result["output"])
            else:
                error = ValiError(result["issues"])
                return ValidationResult(success=False, error=error)
        except Exception as e:
            return ValidationResult(success=False, error=ValidationError(str(e)))
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON schema."""
        return self.vali_schema.to_json_schema()

# Convenience functions (Valibot-style API)
def string(min_length: Optional[int] = None, max_length: Optional[int] = None) -> StringSchema:
    """Create a string schema."""
    return StringSchema(min_length=min_length, max_length=max_length)

def number(min_value: Optional[Union[int, float]] = None, 
          max_value: Optional[Union[int, float]] = None) -> NumberSchema:
    """Create a number schema."""
    return NumberSchema(min_value=min_value, max_value=max_value)

def boolean() -> BooleanSchema:
    """Create a boolean schema."""
    return BooleanSchema()

def object(shape: Dict[str, ValiSchema]) -> ObjectSchema:
    """Create an object schema."""
    return ObjectSchema(shape)

def array(item_schema: ValiSchema) -> ArraySchema:
    """Create an array schema."""
    return ArraySchema(item_schema)

def valibot_schema(vali_schema: ValiSchema[T]) -> ValiPythonSchema[T]:
    """Create an AI SDK schema from a Valibot-style schema."""
    return ValiPythonSchema(vali_schema)

# Export the main API similar to TypeScript Valibot
__all__ = [
    # Schema types
    "ValiSchema",
    "StringSchema", 
    "NumberSchema",
    "BooleanSchema",
    "ObjectSchema",
    "ArraySchema",
    "ValiPythonSchema",
    
    # Factory functions (Valibot API style)
    "string",
    "number", 
    "boolean",
    "object",
    "array",
    "valibot_schema",
    
    # Error types
    "ValiError",
    "ValidationIssue",
]