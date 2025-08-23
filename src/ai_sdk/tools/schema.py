"""Schema utilities for tools in AI SDK Python."""

import json
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, ValidationError

from ..errors.base import InvalidArgumentError


def create_tool_schema(
    properties: Dict[str, Dict[str, Any]],
    required: Optional[List[str]] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a JSON schema for a tool's parameters.
    
    Args:
        properties: Dictionary of parameter properties
        required: List of required parameter names
        description: Optional description of the schema
        
    Returns:
        JSON schema dictionary
        
    Example:
        schema = create_tool_schema(
            properties={
                "location": {
                    "type": "string",
                    "description": "The location to get weather for"
                },
                "units": {
                    "type": "string", 
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature units"
                }
            },
            required=["location"]
        )
    """
    schema = {
        "type": "object",
        "properties": properties,
    }
    
    if required:
        schema["required"] = required
        
    if description:
        schema["description"] = description
        
    return schema


def pydantic_to_tool_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """Convert a Pydantic model to a tool parameter schema.
    
    Args:
        model: Pydantic model class
        
    Returns:
        JSON schema dictionary suitable for tool parameters
        
    Example:
        class WeatherParams(BaseModel):
            location: str = Field(description="Location to get weather for")
            units: str = Field(default="celsius", description="Temperature units")
            
        schema = pydantic_to_tool_schema(WeatherParams)
    """
    # Get the JSON schema from the Pydantic model
    schema = model.model_json_schema()
    
    # Remove the title if it exists (not needed for tool parameters)
    schema.pop("title", None)
    
    return schema


def validate_tool_input(input_data: Any, schema: Dict[str, Any]) -> Any:
    """Validate tool input against a JSON schema.
    
    Args:
        input_data: The input data to validate
        schema: JSON schema to validate against
        
    Returns:
        The validated input data
        
    Raises:
        InvalidArgumentError: If validation fails
    """
    try:
        # For now, we'll do basic type checking
        # A full implementation would use jsonschema library
        if schema.get("type") == "object":
            if not isinstance(input_data, dict):
                raise InvalidArgumentError(
                    "Input must be an object",
                    argument="input_data",
                    value=input_data,
                )
            
            # Check required fields
            required = schema.get("required", [])
            for field in required:
                if field not in input_data:
                    raise InvalidArgumentError(
                        f"Required field '{field}' is missing",
                        argument=field,
                        value=None,
                    )
            
            # Validate individual properties
            properties = schema.get("properties", {})
            for key, value in input_data.items():
                if key in properties:
                    prop_schema = properties[key]
                    _validate_property(value, prop_schema, key)
        
        return input_data
        
    except Exception as e:
        if isinstance(e, InvalidArgumentError):
            raise
        raise InvalidArgumentError(
            f"Input validation failed: {e}",
            argument="input_data",
            value=input_data,
        ) from e


def _validate_property(value: Any, schema: Dict[str, Any], field_name: str) -> None:
    """Validate a single property against its schema."""
    expected_type = schema.get("type")
    
    if expected_type == "string" and not isinstance(value, str):
        raise InvalidArgumentError(
            f"Field '{field_name}' must be a string",
            argument=field_name,
            value=value,
        )
    elif expected_type == "number" and not isinstance(value, (int, float)):
        raise InvalidArgumentError(
            f"Field '{field_name}' must be a number",
            argument=field_name,
            value=value,
        )
    elif expected_type == "integer" and not isinstance(value, int):
        raise InvalidArgumentError(
            f"Field '{field_name}' must be an integer",
            argument=field_name,
            value=value,
        )
    elif expected_type == "boolean" and not isinstance(value, bool):
        raise InvalidArgumentError(
            f"Field '{field_name}' must be a boolean",
            argument=field_name,
            value=value,
        )
    elif expected_type == "array" and not isinstance(value, list):
        raise InvalidArgumentError(
            f"Field '{field_name}' must be an array",
            argument=field_name,
            value=value,
        )
    elif expected_type == "object" and not isinstance(value, dict):
        raise InvalidArgumentError(
            f"Field '{field_name}' must be an object",
            argument=field_name,
            value=value,
        )
    
    # Check enum constraints
    if "enum" in schema and value not in schema["enum"]:
        raise InvalidArgumentError(
            f"Field '{field_name}' must be one of {schema['enum']}",
            argument=field_name,
            value=value,
        )


def create_function_tool_schema(
    name: str,
    description: str,
    parameters: Dict[str, Any],
) -> Dict[str, Any]:
    """Create a complete tool schema for function calling.
    
    Args:
        name: Name of the tool/function
        description: Description of what the tool does
        parameters: Parameter schema (should be object type)
        
    Returns:
        Complete tool schema for use with language models
    """
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        }
    }


# Common schema patterns for convenience

def string_parameter(description: str, enum: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create a string parameter schema."""
    param = {
        "type": "string",
        "description": description,
    }
    if enum:
        param["enum"] = enum
    return param


def number_parameter(description: str, minimum: Optional[float] = None, maximum: Optional[float] = None) -> Dict[str, Any]:
    """Create a number parameter schema."""
    param = {
        "type": "number",
        "description": description,
    }
    if minimum is not None:
        param["minimum"] = minimum
    if maximum is not None:
        param["maximum"] = maximum
    return param


def integer_parameter(description: str, minimum: Optional[int] = None, maximum: Optional[int] = None) -> Dict[str, Any]:
    """Create an integer parameter schema."""
    param = {
        "type": "integer",
        "description": description,
    }
    if minimum is not None:
        param["minimum"] = minimum
    if maximum is not None:
        param["maximum"] = maximum
    return param


def boolean_parameter(description: str) -> Dict[str, Any]:
    """Create a boolean parameter schema."""
    return {
        "type": "boolean",
        "description": description,
    }


def array_parameter(description: str, items: Dict[str, Any]) -> Dict[str, Any]:
    """Create an array parameter schema."""
    return {
        "type": "array",
        "description": description,
        "items": items,
    }


def object_parameter(description: str, properties: Dict[str, Any], required: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create an object parameter schema."""
    param = {
        "type": "object",
        "description": description,
        "properties": properties,
    }
    if required:
        param["required"] = required
    return param