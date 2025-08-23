"""Text repair functionality for object generation."""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, Optional, Type, Union

from pydantic import BaseModel, ValidationError

from ..errors.base import AISDKError


class TextRepairError(AISDKError):
    """Error during text repair process."""
    
    def __init__(self, original_text: str, repair_attempts: int, last_error: Exception) -> None:
        self.original_text = original_text
        self.repair_attempts = repair_attempts
        self.last_error = last_error
        super().__init__(f"Failed to repair text after {repair_attempts} attempts: {last_error}")


class TextRepairFunction:
    """Function to repair malformed JSON text."""
    
    def __init__(self, repair_func: Optional[Callable[[str, Exception], Optional[str]]] = None) -> None:
        """Initialize with optional custom repair function.
        
        Args:
            repair_func: Custom repair function that takes (text, error) and returns repaired text or None
        """
        self.repair_func = repair_func
    
    def repair(
        self, 
        text: str, 
        error: Exception,
        schema: Optional[Type[BaseModel]] = None
    ) -> Optional[str]:
        """Attempt to repair malformed JSON text.
        
        Args:
            text: The malformed text to repair
            error: The original parsing error
            schema: Optional schema for validation
            
        Returns:
            Repaired text or None if repair failed
        """
        if self.repair_func:
            try:
                return self.repair_func(text, error)
            except Exception:
                pass  # Fall back to default repair
        
        return self._default_repair(text, error, schema)
    
    def _default_repair(
        self, 
        text: str, 
        error: Exception,
        schema: Optional[Type[BaseModel]] = None
    ) -> Optional[str]:
        """Default repair strategies for common JSON issues."""
        repair_strategies = [
            self._extract_json_from_text,
            self._fix_trailing_commas,
            self._fix_missing_quotes,
            self._fix_incomplete_json,
            self._fix_escaped_quotes,
            self._fix_newlines_in_strings,
        ]
        
        for strategy in repair_strategies:
            try:
                repaired = strategy(text)
                if repaired and repaired != text:
                    # Test if the repaired text is valid JSON
                    json.loads(repaired)
                    return repaired
            except (json.JSONDecodeError, ValueError):
                continue
        
        return None
    
    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """Extract JSON from text that may contain additional content."""
        # Try to find JSON object or array in the text
        patterns = [
            r'\{.*\}',  # Object
            r'\[.*\]',  # Array
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                # Try the first match that might be complete JSON
                for match in matches:
                    try:
                        json.loads(match)
                        return match
                    except json.JSONDecodeError:
                        continue
        
        return None
    
    def _fix_trailing_commas(self, text: str) -> str:
        """Remove trailing commas before closing brackets."""
        # Remove trailing commas before }
        text = re.sub(r',(\s*})', r'\1', text)
        # Remove trailing commas before ]
        text = re.sub(r',(\s*])', r'\1', text)
        return text
    
    def _fix_missing_quotes(self, text: str) -> str:
        """Add missing quotes around keys and string values."""
        # Fix unquoted keys (simple heuristic)
        text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', text)
        return text
    
    def _fix_incomplete_json(self, text: str) -> str:
        """Try to complete incomplete JSON structures."""
        text = text.strip()
        
        # Count braces and brackets
        open_braces = text.count('{') - text.count('}')
        open_brackets = text.count('[') - text.count(']')
        
        # Add missing closing braces/brackets
        text += '}' * open_braces
        text += ']' * open_brackets
        
        return text
    
    def _fix_escaped_quotes(self, text: str) -> str:
        """Fix incorrectly escaped quotes."""
        # Fix double backslashes before quotes
        text = re.sub(r'\\\\["\']', r'\\"', text)
        return text
    
    def _fix_newlines_in_strings(self, text: str) -> str:
        """Fix unescaped newlines in JSON strings."""
        # This is a simple approach - in practice you'd want more sophisticated string parsing
        text = re.sub(r'(\"\w*)\n(\w*\")', r'\1\\n\2', text)
        return text


def create_default_repair_function() -> TextRepairFunction:
    """Create a default text repair function with common strategies."""
    return TextRepairFunction()


def create_custom_repair_function(
    custom_repairs: Dict[str, Callable[[str], str]]
) -> TextRepairFunction:
    """Create a repair function with custom repair strategies.
    
    Args:
        custom_repairs: Dictionary mapping error patterns to repair functions
    """
    def repair_func(text: str, error: Exception) -> Optional[str]:
        error_msg = str(error).lower()
        
        for pattern, repair_strategy in custom_repairs.items():
            if pattern.lower() in error_msg:
                try:
                    return repair_strategy(text)
                except Exception:
                    continue
        
        return None
    
    return TextRepairFunction(repair_func)


async def parse_with_repair(
    text: str,
    schema: Type[BaseModel],
    repair_function: Optional[TextRepairFunction] = None,
    max_repair_attempts: int = 3
) -> BaseModel:
    """Parse JSON text with repair attempts if parsing fails.
    
    Args:
        text: The JSON text to parse
        schema: The Pydantic model to validate against
        repair_function: Optional repair function
        max_repair_attempts: Maximum number of repair attempts
        
    Returns:
        Parsed and validated object
        
    Raises:
        TextRepairError: If all repair attempts fail
        ValidationError: If the object doesn't match the schema
    """
    repair_func = repair_function or create_default_repair_function()
    
    # First try to parse as-is
    try:
        data = json.loads(text)
        return schema.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        original_error = e
        current_text = text
        
        # Attempt repairs
        for attempt in range(max_repair_attempts):
            try:
                repaired_text = repair_func.repair(current_text, e, schema)
                if repaired_text is None:
                    break
                
                # Try to parse repaired text
                data = json.loads(repaired_text)
                return schema.model_validate(data)
                
            except (json.JSONDecodeError, ValidationError) as repair_error:
                current_text = repaired_text if repaired_text else current_text
                e = repair_error
        
        raise TextRepairError(text, max_repair_attempts, original_error)


def repair_json_string(text: str, repair_function: Optional[TextRepairFunction] = None) -> str:
    """Repair a JSON string without schema validation.
    
    Args:
        text: The JSON text to repair
        repair_function: Optional repair function
        
    Returns:
        Repaired JSON string
        
    Raises:
        TextRepairError: If repair fails
    """
    repair_func = repair_function or create_default_repair_function()
    
    try:
        # First try to parse as-is
        json.loads(text)
        return text
    except json.JSONDecodeError as e:
        repaired = repair_func.repair(text, e)
        if repaired:
            try:
                json.loads(repaired)  # Validate it's valid JSON
                return repaired
            except json.JSONDecodeError:
                pass
        
        raise TextRepairError(text, 1, e)