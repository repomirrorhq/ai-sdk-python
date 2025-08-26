"""JSON utilities for AI SDK Python."""

import json
from typing import Any, Optional

from ..errors import InvalidResponseError

# Aliases for compatibility
parse_json = json.loads
parse_json_response = json.loads


def handle_json_parse_error(error: Exception, text: str) -> None:
    """Handle JSON parse errors by raising InvalidResponseError."""
    raise InvalidResponseError(
        f"Failed to parse JSON response: {error}",
        response_body=text,
        expected_format="JSON",
    ) from error


def parse_json_chunk(chunk: str) -> Any:
    """Parse JSON chunk for streaming."""
    return json.loads(chunk)


def parse_json_stream(stream: str) -> Any:
    """Parse JSON stream for streaming."""
    return json.loads(stream)


def ensure_json_parsable(data: Any) -> Any:
    """Ensure data is JSON parsable."""
    try:
        json.dumps(data)
        return data
    except (TypeError, ValueError):
        return str(data)


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


# Alias for compatibility
safe_json_parse = secure_json_parse


def extract_json_from_text(text: str) -> Optional[str]:
    """Extract JSON content from text.
    
    This function tries to find JSON content in a larger text string.
    It looks for JSON objects or arrays and returns the first valid JSON found.
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Extracted JSON string or None if no valid JSON found
    """
    import re
    
    # First try to parse the whole text as JSON
    try:
        json.loads(text)
        return text.strip()
    except json.JSONDecodeError:
        pass
    
    # Look for JSON-like patterns
    json_patterns = [
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Objects
        r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]',  # Arrays
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                json.loads(match)
                return match.strip()
            except json.JSONDecodeError:
                continue
                
    return None