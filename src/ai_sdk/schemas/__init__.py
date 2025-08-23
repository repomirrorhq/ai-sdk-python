"""Schema validation system for AI SDK Python.

This module provides a unified interface for schema validation with support
for multiple Python validation libraries including Pydantic, JSONSchema,
Marshmallow, and Cerberus.
"""

from .base import BaseSchema, ValidationResult, ValidationError as SchemaValidationError
from .pydantic import PydanticSchema, pydantic_schema
from .jsonschema import JSONSchemaValidator, jsonschema_schema

# Optional integrations (fail gracefully if not installed)
try:
    from .marshmallow import MarshmallowSchema, marshmallow_schema
except ImportError:
    MarshmallowSchema = None
    marshmallow_schema = None

try:
    from .cerberus import CerberusSchema, cerberus_schema  
except ImportError:
    CerberusSchema = None
    cerberus_schema = None

# Valibot-style support (always available)
from .valibot import (
    ValiSchema, StringSchema, NumberSchema, BooleanSchema, 
    ObjectSchema, ArraySchema, ValiPythonSchema, ValiError,
    string, number, boolean, object, array, valibot_schema
)

__all__ = [
    # Base interfaces
    "BaseSchema",
    "ValidationResult", 
    "SchemaValidationError",
    
    # Pydantic support (always available)
    "PydanticSchema",
    "pydantic_schema",
    
    # JSONSchema support (always available)
    "JSONSchemaValidator", 
    "jsonschema_schema",
    
    # Valibot-style support (always available)
    "ValiSchema",
    "StringSchema",
    "NumberSchema", 
    "BooleanSchema",
    "ObjectSchema",
    "ArraySchema",
    "ValiPythonSchema",
    "ValiError",
    "string",
    "number",
    "boolean",
    "object", 
    "array",
    "valibot_schema",
    
    # Optional integrations
    "MarshmallowSchema",
    "marshmallow_schema",
    "CerberusSchema", 
    "cerberus_schema",
]