"""Dictionary manipulation utilities for AI SDK Python."""

from typing import Dict, Optional, TypeVar

T = TypeVar('T')


def remove_none_entries(record: Dict[str, Optional[T]]) -> Dict[str, T]:
    """
    Removes entries from a dictionary where the value is None.
    
    Args:
        record: The input dictionary whose values may be None.
        
    Returns:
        A new dictionary containing only entries with non-None values.
    """
    return {k: v for k, v in record.items() if v is not None}


def merge_dicts(*dicts: Optional[Dict[str, T]]) -> Dict[str, T]:
    """
    Merge multiple dictionaries, with later dictionaries taking precedence.
    
    Args:
        *dicts: Variable number of dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result: Dict[str, T] = {}
    
    for d in dicts:
        if d is not None:
            result.update(d)
    
    return result