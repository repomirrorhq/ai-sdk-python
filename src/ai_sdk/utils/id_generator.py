"""ID generation utilities for AI SDK Python."""

import random
import string
from typing import Callable, Optional

from ..errors.base import InvalidArgumentError


def create_id_generator(
    prefix: Optional[str] = None,
    size: int = 16,
    alphabet: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    separator: str = "-",
) -> Callable[[], str]:
    """
    Creates an ID generator.
    The total length of the ID is the sum of the prefix, separator, and random part length.
    Not cryptographically secure.
    
    Args:
        alphabet: The alphabet to use for the ID. 
                 Default: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.
        prefix: The prefix of the ID to generate. Optional.
        separator: The separator between the prefix and the random part of the ID. Default: '-'.
        size: The size of the random part of the ID to generate. Default: 16.
        
    Returns:
        A function that generates IDs.
        
    Raises:
        InvalidArgumentError: If separator is part of the alphabet.
    """
    def generator() -> str:
        return ''.join(random.choices(alphabet, k=size))
    
    if prefix is None:
        return generator
    
    # check that the separator is not part of the alphabet (otherwise prefix checking can fail randomly)
    if separator in alphabet:
        raise InvalidArgumentError(
            argument="separator",
            message=f'The separator "{separator}" must not be part of the alphabet "{alphabet}".'
        )
    
    return lambda: f"{prefix}{separator}{generator()}"


# Type alias for ID generator function
IdGenerator = Callable[[], str]

# Default ID generator - generates a 16-character random string
generate_id: IdGenerator = create_id_generator()