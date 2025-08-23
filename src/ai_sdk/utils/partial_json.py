"""Partial JSON parsing utilities for AI SDK Python."""

import json
import re
from typing import Any, Dict, Literal, Optional, Tuple, Union

from .secure_json import secure_json_parse


def parse_partial_json(json_text: Optional[str]) -> Dict[str, Any]:
    """
    Attempts to parse partial JSON text, with repair capabilities.
    
    Args:
        json_text: The JSON text to parse (may be partial/malformed)
        
    Returns:
        Dictionary with:
        - value: The parsed value (or None if failed)
        - state: One of 'undefined-input', 'successful-parse', 'repaired-parse', 'failed-parse'
    """
    if json_text is None:
        return {"value": None, "state": "undefined-input"}
    
    # Try parsing as-is first
    try:
        value = secure_json_parse(json_text)
        return {"value": value, "state": "successful-parse"}
    except (json.JSONDecodeError, SyntaxError):
        pass
    
    # Try with repair
    try:
        fixed_json = fix_json(json_text)
        value = secure_json_parse(fixed_json)
        return {"value": value, "state": "repaired-parse"}
    except (json.JSONDecodeError, SyntaxError):
        pass
    
    return {"value": None, "state": "failed-parse"}


def fix_json(text: str) -> str:
    """
    Attempts to fix malformed JSON by adding missing closing brackets/quotes.
    
    This is a simplified version that handles common cases:
    - Missing closing quotes
    - Missing closing brackets/braces
    - Incomplete literals
    
    Args:
        text: The malformed JSON text
        
    Returns:
        Potentially fixed JSON text
    """
    if not text:
        return text
    
    text = text.strip()
    if not text:
        return text
    
    # Track bracket/brace depth
    brace_count = 0
    bracket_count = 0
    in_string = False
    escape_next = False
    
    i = 0
    while i < len(text):
        char = text[i]
        
        if escape_next:
            escape_next = False
            i += 1
            continue
        
        if char == '\\' and in_string:
            escape_next = True
            i += 1
            continue
        
        if char == '"':
            in_string = not in_string
        elif not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
        
        i += 1
    
    # Fix unclosed string
    if in_string:
        text += '"'
    
    # Fix incomplete literals
    if text.endswith(('tru', 'tr', 't')):
        text = text[:-len(text.split()[-1])] + 'true'
    elif text.endswith(('fals', 'fal', 'fa', 'f')):
        text = text[:-len(text.split()[-1])] + 'false'
    elif text.endswith(('nul', 'nu', 'n')):
        text = text[:-len(text.split()[-1])] + 'null'
    
    # Close open braces and brackets
    text += '}' * max(0, brace_count)
    text += ']' * max(0, bracket_count)
    
    return text