"""Reasoning utilities for AI SDK Python.

This module provides utilities for working with reasoning content and tokens,
particularly useful for models like OpenAI o1 that support reasoning capabilities.
"""

from __future__ import annotations

from typing import List, Optional

from ..providers.types import Content, ReasoningContent, Usage


def extract_reasoning_text(content: List[Content]) -> Optional[str]:
    """Extract reasoning text from content list.
    
    Args:
        content: List of content parts that may contain reasoning
        
    Returns:
        Combined reasoning text if any reasoning content is found, None otherwise
    """
    reasoning_parts = [
        part for part in content 
        if isinstance(part, ReasoningContent)
    ]
    
    if not reasoning_parts:
        return None
        
    return '\n'.join(part.text for part in reasoning_parts)


def add_usage(usage1: Usage, usage2: Usage) -> Usage:
    """Add two Usage objects together.
    
    Args:
        usage1: First usage object
        usage2: Second usage object
        
    Returns:
        Combined usage with summed token counts
    """
    return Usage(
        prompt_tokens=usage1.prompt_tokens + usage2.prompt_tokens,
        completion_tokens=usage1.completion_tokens + usage2.completion_tokens,
        total_tokens=usage1.total_tokens + usage2.total_tokens,
        reasoning_tokens=_add_optional_tokens(
            usage1.reasoning_tokens, 
            usage2.reasoning_tokens
        ),
        cached_input_tokens=_add_optional_tokens(
            usage1.cached_input_tokens,
            usage2.cached_input_tokens
        )
    )


def _add_optional_tokens(
    tokens1: Optional[int], 
    tokens2: Optional[int]
) -> Optional[int]:
    """Add two optional token counts."""
    if tokens1 is None and tokens2 is None:
        return None
    return (tokens1 or 0) + (tokens2 or 0)


def has_reasoning_tokens(usage: Usage) -> bool:
    """Check if usage contains reasoning tokens.
    
    Args:
        usage: Usage object to check
        
    Returns:
        True if reasoning_tokens is set and > 0, False otherwise
    """
    return usage.reasoning_tokens is not None and usage.reasoning_tokens > 0


def get_reasoning_token_ratio(usage: Usage) -> Optional[float]:
    """Get the ratio of reasoning tokens to total tokens.
    
    Args:
        usage: Usage object to analyze
        
    Returns:
        Ratio of reasoning tokens to total tokens, or None if no reasoning tokens
    """
    if not has_reasoning_tokens(usage) or usage.total_tokens == 0:
        return None
        
    return usage.reasoning_tokens / usage.total_tokens


class ReasoningExtractor:
    """Helper class for extracting and managing reasoning content."""
    
    def __init__(self):
        self._reasoning_parts: List[ReasoningContent] = []
        
    def add_reasoning(self, text: str, provider_metadata=None) -> ReasoningContent:
        """Add reasoning content.
        
        Args:
            text: Reasoning text
            provider_metadata: Optional provider-specific metadata
            
        Returns:
            Created ReasoningContent object
        """
        reasoning_content = ReasoningContent(
            text=text,
            provider_metadata=provider_metadata
        )
        self._reasoning_parts.append(reasoning_content)
        return reasoning_content
        
    def get_combined_reasoning(self) -> Optional[str]:
        """Get all reasoning text combined.
        
        Returns:
            Combined reasoning text, or None if no reasoning
        """
        if not self._reasoning_parts:
            return None
            
        return '\n'.join(part.text for part in self._reasoning_parts)
        
    def clear(self):
        """Clear all stored reasoning content."""
        self._reasoning_parts.clear()
        
    @property
    def reasoning_parts(self) -> List[ReasoningContent]:
        """Get all reasoning parts."""
        return self._reasoning_parts.copy()