"""API key loading utilities for AI SDK Python."""

import os
from typing import Optional

from ..errors.base import LoadAPIKeyError


def load_api_key(
    api_key: Optional[str],
    environment_variable_name: str,
    api_key_parameter_name: str = "api_key",
    description: str = "API"
) -> str:
    """
    Load an API key from parameter or environment variable.
    
    Args:
        api_key: The API key value (if provided directly)
        environment_variable_name: Name of environment variable to check
        api_key_parameter_name: Name of the parameter for error messages
        description: Description of the service for error messages
        
    Returns:
        The loaded API key
        
    Raises:
        LoadAPIKeyError: If API key cannot be loaded or is invalid
    """
    if isinstance(api_key, str):
        return api_key
    
    if api_key is not None:
        raise LoadAPIKeyError(
            message=f"{description} API key must be a string."
        )
    
    # Try to load from environment variable
    api_key = os.environ.get(environment_variable_name)
    
    if api_key is None:
        raise LoadAPIKeyError(
            message=(
                f"{description} API key is missing. Pass it using the '{api_key_parameter_name}' "
                f"parameter or the {environment_variable_name} environment variable."
            )
        )
    
    if not isinstance(api_key, str):
        raise LoadAPIKeyError(
            message=(
                f"{description} API key must be a string. The value of the "
                f"{environment_variable_name} environment variable is not a string."
            )
        )
    
    return api_key


def load_optional_setting(
    value: Optional[str],
    environment_variable_name: str
) -> Optional[str]:
    """
    Load an optional setting from parameter or environment variable.
    
    Args:
        value: The setting value (if provided directly)
        environment_variable_name: Name of environment variable to check
        
    Returns:
        The loaded setting value or None
    """
    if value is not None:
        return value
    
    return os.environ.get(environment_variable_name)