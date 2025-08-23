"""Enhanced schema support for tools with multiple schema types."""

from __future__ import annotations

from typing import Any, Dict, Type, Union, get_origin, get_args
from pydantic import BaseModel
import inspect


# Type alias for flexible schema support
FlexibleSchema = Union[
    Dict[str, Any],           # JSON Schema
    Type[BaseModel],          # Pydantic model
    type,                     # Python class/type
    str,                      # String type name
]


def normalize_schema(schema: FlexibleSchema) -> Dict[str, Any]:
    """Convert various schema types to JSON schema.
    
    Args:
        schema: The schema in any supported format
        
    Returns:
        JSON schema dictionary
        
    Raises:
        ValueError: If schema type is not supported
    """
    if isinstance(schema, dict):
        # Already a JSON schema
        return schema
    
    elif isinstance(schema, type) and issubclass(schema, BaseModel):
        # Pydantic model
        return schema.model_json_schema()
    
    elif isinstance(schema, type):
        # Python type/class
        return _python_type_to_json_schema(schema)
    
    elif isinstance(schema, str):
        # String type name
        return _string_type_to_json_schema(schema)
    
    else:
        raise ValueError(f"Unsupported schema type: {type(schema)}")


def _python_type_to_json_schema(py_type: type) -> Dict[str, Any]:
    """Convert Python type to JSON schema."""
    # Handle basic types
    if py_type == str:
        return {"type": "string"}
    elif py_type == int:
        return {"type": "integer"}
    elif py_type == float:
        return {"type": "number"}
    elif py_type == bool:
        return {"type": "boolean"}
    elif py_type == list:
        return {"type": "array"}
    elif py_type == dict:
        return {"type": "object"}
    
    # Handle generic types (Python 3.8+)
    origin = get_origin(py_type)
    args = get_args(py_type)
    
    if origin is list:
        if args:
            item_schema = normalize_schema(args[0])
            return {"type": "array", "items": item_schema}
        else:
            return {"type": "array"}
    
    elif origin is dict:
        if len(args) == 2:
            # Dict[str, ValueType]
            value_schema = normalize_schema(args[1])
            return {
                "type": "object",
                "additionalProperties": value_schema
            }
        else:
            return {"type": "object"}
    
    elif origin is Union:
        # Handle Union types (including Optional)
        if len(args) == 2 and type(None) in args:
            # Optional type
            non_none_type = next(arg for arg in args if arg is not type(None))
            schema = normalize_schema(non_none_type)
            # Make it optional
            if "required" not in schema:
                schema["required"] = []
            return schema
        else:
            # General Union - use anyOf
            return {"anyOf": [normalize_schema(arg) for arg in args]}
    
    # For complex classes, try to introspect
    if hasattr(py_type, '__annotations__'):
        return _class_annotations_to_json_schema(py_type)
    
    # Fallback
    return {"type": "object", "description": f"Object of type {py_type.__name__}"}


def _string_type_to_json_schema(type_name: str) -> Dict[str, Any]:
    """Convert string type name to JSON schema."""
    type_mapping = {
        "string": {"type": "string"},
        "str": {"type": "string"}, 
        "integer": {"type": "integer"},
        "int": {"type": "integer"},
        "number": {"type": "number"},
        "float": {"type": "number"},
        "boolean": {"type": "boolean"},
        "bool": {"type": "boolean"},
        "array": {"type": "array"},
        "list": {"type": "array"},
        "object": {"type": "object"},
        "dict": {"type": "object"},
    }
    
    return type_mapping.get(type_name.lower(), {"type": "string"})


def _class_annotations_to_json_schema(cls: type) -> Dict[str, Any]:
    """Convert class annotations to JSON schema."""
    properties = {}
    required = []
    
    if hasattr(cls, '__annotations__'):
        for field_name, field_type in cls.__annotations__.items():
            # Skip private fields
            if field_name.startswith('_'):
                continue
                
            properties[field_name] = normalize_schema(field_type)
            
            # Check if field has default value
            if not hasattr(cls, field_name) or getattr(cls, field_name) is None:
                required.append(field_name)
    
    schema = {
        "type": "object",
        "properties": properties
    }
    
    if required:
        schema["required"] = required
    
    return schema


def extract_schema_info(schema: FlexibleSchema) -> Dict[str, Any]:
    """Extract useful information from a schema.
    
    Returns:
        Dictionary with schema metadata like title, description, examples
    """
    info = {}
    
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        # Extract from Pydantic model
        info["title"] = schema.__name__
        info["description"] = schema.__doc__ or ""
        
        # Get field descriptions
        field_descriptions = {}
        if hasattr(schema, 'model_fields'):
            for field_name, field_info in schema.model_fields.items():
                if hasattr(field_info, 'description') and field_info.description:
                    field_descriptions[field_name] = field_info.description
        
        if field_descriptions:
            info["field_descriptions"] = field_descriptions
    
    elif isinstance(schema, dict):
        # Extract from JSON schema
        for key in ["title", "description", "examples"]:
            if key in schema:
                info[key] = schema[key]
    
    elif isinstance(schema, type):
        # Extract from Python class
        info["title"] = schema.__name__
        info["description"] = schema.__doc__ or ""
    
    return info


def validate_schema_input(input_data: Any, schema: FlexibleSchema) -> Any:
    """Validate input data against a schema.
    
    Args:
        input_data: The data to validate
        schema: The schema to validate against
        
    Returns:
        Validated and potentially transformed data
        
    Raises:
        ValueError: If validation fails
    """
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        # Use Pydantic validation
        try:
            return schema.model_validate(input_data)
        except Exception as e:
            raise ValueError(f"Pydantic validation failed: {e}")
    
    elif isinstance(schema, dict):
        # Basic JSON schema validation (simplified)
        return _validate_against_json_schema(input_data, schema)
    
    elif isinstance(schema, type):
        # Basic Python type validation
        try:
            return schema(input_data)
        except Exception as e:
            raise ValueError(f"Type validation failed: {e}")
    
    else:
        # No validation possible, return as-is
        return input_data


def _validate_against_json_schema(data: Any, schema: Dict[str, Any]) -> Any:
    """Basic JSON schema validation (simplified implementation)."""
    schema_type = schema.get("type")
    
    if schema_type == "string" and not isinstance(data, str):
        raise ValueError(f"Expected string, got {type(data)}")
    elif schema_type == "integer" and not isinstance(data, int):
        raise ValueError(f"Expected integer, got {type(data)}")
    elif schema_type == "number" and not isinstance(data, (int, float)):
        raise ValueError(f"Expected number, got {type(data)}")
    elif schema_type == "boolean" and not isinstance(data, bool):
        raise ValueError(f"Expected boolean, got {type(data)}")
    elif schema_type == "array" and not isinstance(data, list):
        raise ValueError(f"Expected array, got {type(data)}")
    elif schema_type == "object" and not isinstance(data, dict):
        raise ValueError(f"Expected object, got {type(data)}")
    
    return data


def create_pydantic_tool_schema(
    input_model: Type[BaseModel],
    output_model: Optional[Type[BaseModel]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Create a tool schema from Pydantic models.
    
    Args:
        input_model: Pydantic model for input validation
        output_model: Optional Pydantic model for output validation
        name: Tool name (defaults to input_model.__name__)
        description: Tool description
        
    Returns:
        Tool schema dictionary
    """
    input_schema = input_model.model_json_schema()
    
    tool_schema = {
        "name": name or input_model.__name__,
        "description": description or input_model.__doc__ or "",
        "input_schema": input_schema,
        "input_model": input_model,
    }
    
    if output_model:
        tool_schema["output_schema"] = output_model.model_json_schema()
        tool_schema["output_model"] = output_model
    
    return tool_schema


# Example usage and test schemas
if __name__ == "__main__":
    from typing import List, Optional
    
    # Test with Pydantic model
    class PersonInput(BaseModel):
        name: str
        age: int
        email: Optional[str] = None
    
    # Test schema normalization
    schemas = [
        PersonInput,
        {"type": "object", "properties": {"name": {"type": "string"}}},
        str,
        List[str],
        "string"
    ]
    
    for schema in schemas:
        try:
            json_schema = normalize_schema(schema)
            print(f"Schema {schema} -> {json_schema}")
        except Exception as e:
            print(f"Failed to normalize {schema}: {e}")
    
    # Test validation
    try:
        result = validate_schema_input(
            {"name": "John", "age": 30}, 
            PersonInput
        )
        print(f"Validation result: {result}")
    except Exception as e:
        print(f"Validation failed: {e}")