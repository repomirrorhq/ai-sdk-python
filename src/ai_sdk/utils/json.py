"""JSON utilities for AI SDK Python."""

import json
from typing import Any, Optional

from ..errors import InvalidResponseError


def secure_json_parse(
    text: str,
    expected_type: Optional[type] = None,
) -> Any:
    """Securely parse JSON text with validation.
    
    Args:
        text: JSON text to parse
        expected_type: Expected type of the parsed result
        
    Returns:
        Parsed JSON object
        
    Raises:
        InvalidResponseError: If parsing fails or type doesn't match
    """
    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        raise InvalidResponseError(
            f"Failed to parse JSON response: {e}",
            response_body=text,
            expected_format="JSON",
        ) from e
    
    if expected_type is not None and not isinstance(result, expected_type):
        raise InvalidResponseError(
            f"Expected {expected_type.__name__}, got {type(result).__name__}",
            response_body=text,
            expected_format=f"{expected_type.__name__} JSON",
        )
    
    return result