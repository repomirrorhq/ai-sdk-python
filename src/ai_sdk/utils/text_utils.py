"""Utility functions for text processing."""

from typing import Optional


def get_potential_start_index(text: str, search_tag: str) -> Optional[int]:
    """
    Find the index where a tag might start, accounting for partial matches at the end.
    
    This function is used for streaming text processing where we might receive
    partial tag matches at buffer boundaries.
    
    Args:
        text: The text to search in
        search_tag: The tag to search for (e.g., "<thinking>", "</thinking>")
        
    Returns:
        The index where the tag might start, or None if no match is found
    """
    if not text or not search_tag:
        return None
    
    # First check for complete matches
    index = text.find(search_tag)
    if index != -1:
        return index
    
    # Check for partial matches at the end of the buffer
    # We need to check if the end of our text might be the beginning of the tag
    for i in range(1, min(len(search_tag), len(text)) + 1):
        suffix = text[-i:]
        prefix = search_tag[:i]
        if suffix == prefix:
            return len(text) - i
    
    return None