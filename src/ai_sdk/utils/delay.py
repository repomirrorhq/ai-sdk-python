"""Delay utilities for AI SDK Python."""

import asyncio
from typing import Optional


async def delay(
    delay_in_ms: Optional[int] = None,
    *,
    cancel_event: Optional[asyncio.Event] = None
) -> None:
    """
    Creates a coroutine that waits for a specified delay.
    
    Args:
        delay_in_ms: The delay duration in milliseconds. If None, returns immediately.
        cancel_event: Optional Event to cancel the delay
        
    Raises:
        asyncio.CancelledError: When the delay is cancelled
    """
    if delay_in_ms is None:
        return
        
    delay_in_seconds = delay_in_ms / 1000.0
    
    if cancel_event is None:
        await asyncio.sleep(delay_in_seconds)
    else:
        try:
            # Wait for either the delay or the cancel event
            await asyncio.wait_for(
                cancel_event.wait(),
                timeout=delay_in_seconds
            )
            # If we get here, the event was set (cancelled)
            raise asyncio.CancelledError("Delay was cancelled")
        except asyncio.TimeoutError:
            # This is the normal case - delay completed
            pass