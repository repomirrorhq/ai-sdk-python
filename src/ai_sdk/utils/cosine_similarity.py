"""Cosine similarity calculation for AI SDK Python."""

import math
from typing import List

from ..errors.base import InvalidArgumentError


def cosine_similarity(vector1: List[float], vector2: List[float]) -> float:
    """
    Calculates the cosine similarity between two vectors. This is a useful metric for
    comparing the similarity of two vectors such as embeddings.
    
    Args:
        vector1: The first vector.
        vector2: The second vector.
        
    Returns:
        The cosine similarity between vector1 and vector2.
        Returns 0 if either vector is the zero vector.
        
    Raises:
        InvalidArgumentError: If the vectors do not have the same length.
    """
    if len(vector1) != len(vector2):
        raise InvalidArgumentError(
            message="Vectors must have the same length",
            argument="vector1,vector2",
            value={
                "vector1_length": len(vector1),
                "vector2_length": len(vector2)
            }
        )
    
    n = len(vector1)
    
    if n == 0:
        return 0.0  # Return 0 for empty vectors
    
    magnitude_squared1 = 0.0
    magnitude_squared2 = 0.0
    dot_product = 0.0
    
    for i in range(n):
        value1 = vector1[i]
        value2 = vector2[i]
        
        magnitude_squared1 += value1 * value1
        magnitude_squared2 += value2 * value2
        dot_product += value1 * value2
    
    # Handle zero vectors
    if magnitude_squared1 == 0 or magnitude_squared2 == 0:
        return 0.0
    
    return dot_product / (math.sqrt(magnitude_squared1) * math.sqrt(magnitude_squared2))