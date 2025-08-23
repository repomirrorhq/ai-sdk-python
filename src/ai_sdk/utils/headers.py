"""Header manipulation utilities for AI SDK Python."""

from typing import Dict, Optional, Union


def combine_headers(
    *headers: Optional[Dict[str, Optional[str]]]
) -> Dict[str, Optional[str]]:
    """
    Combines multiple header dictionaries into one.
    Later headers override earlier ones.
    
    Args:
        *headers: Variable number of header dictionaries to combine
        
    Returns:
        Combined header dictionary
    """
    combined: Dict[str, Optional[str]] = {}
    
    for header_dict in headers:
        if header_dict is not None:
            combined.update(header_dict)
    
    return combined


def clean_headers(headers: Dict[str, Optional[str]]) -> Dict[str, str]:
    """
    Remove None values from headers dictionary.
    
    Args:
        headers: Dictionary that may contain None values
        
    Returns:
        Dictionary with None values filtered out
    """
    return {k: v for k, v in headers.items() if v is not None}