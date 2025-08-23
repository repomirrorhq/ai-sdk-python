"""Secure JSON parsing utilities for AI SDK Python.

Licensed under BSD-3-Clause (this file only)
Code adapted from https://github.com/fastify/secure-json-parse/
"""

import json
import re
import sys
from typing import Any


# Patterns to detect potentially dangerous JSON
SUSPECT_PROTO_RX = re.compile(r'"__proto__"\s*:')
SUSPECT_CONSTRUCTOR_RX = re.compile(r'"constructor"\s*:')


def secure_json_parse(text: str) -> Any:
    """
    Parse JSON text securely by filtering out dangerous prototype properties.
    
    This function prevents prototype pollution attacks by removing __proto__
    and constructor properties from parsed objects.
    
    Args:
        text: JSON string to parse
        
    Returns:
        Parsed JSON object
        
    Raises:
        json.JSONDecodeError: If the JSON is invalid
        SyntaxError: If the JSON contains forbidden prototype properties
    """
    # Performance optimization - disable traceback during parsing
    original_tracebacklimit = getattr(sys, 'tracebacklimit', 1000)
    
    try:
        sys.tracebacklimit = 0
        return _parse(text)
    finally:
        sys.tracebacklimit = original_tracebacklimit


def _parse(text: str) -> Any:
    """Internal JSON parsing with prototype pollution protection."""
    # Parse normally
    obj = json.loads(text)
    
    # Ignore None and non-dict/list objects
    if obj is None or not isinstance(obj, (dict, list)):
        return obj
    
    # Quick check for suspicious patterns before deep scanning
    if (not SUSPECT_PROTO_RX.search(text) and 
        not SUSPECT_CONSTRUCTOR_RX.search(text)):
        return obj
    
    # Scan result for proto keys
    return _filter_dangerous_keys(obj)


def _filter_dangerous_keys(obj: Any) -> Any:
    """Filter out dangerous prototype properties from nested objects."""
    to_check = [obj]
    
    while to_check:
        current_items = to_check
        to_check = []
        
        for item in current_items:
            if isinstance(item, dict):
                # Check for dangerous keys
                if '__proto__' in item:
                    raise SyntaxError('Object contains forbidden prototype property')
                
                if ('constructor' in item and 
                    isinstance(item.get('constructor'), dict) and
                    'prototype' in item['constructor']):
                    raise SyntaxError('Object contains forbidden prototype property')
                
                # Add nested objects/lists for checking
                for value in item.values():
                    if isinstance(value, (dict, list)):
                        to_check.append(value)
            
            elif isinstance(item, list):
                # Add nested objects/lists for checking
                for value in item:
                    if isinstance(value, (dict, list)):
                        to_check.append(value)
    
    return obj