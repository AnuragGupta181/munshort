"""Rate limiter with random delays and exponential backoff."""

import asyncio
import random


class RateLimiter:
    """Implements random delays and exponential backoff for anti-detection."""

    def __init__(self, min_delay: float = 3.0, max_delay: float = 7.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.backoff_factor = 1.0
        self.max_backoff = 60.0

    async def wait(self):
        """Wait a random delay between requests."""
        delay = random.uniform(self.min_delay, self.max_delay) * self.backoff_factor
        delay = min(delay, self.max_backoff)
        await asyncio.sleep(delay)

    def increase_backoff(self):
        """Increase backoff after a failed request."""
        self.backoff_factor = min(self.backoff_factor * 2, 8.0)

    def reset_backoff(self):
        """Reset backoff after a successful request."""
        self.backoff_factor = 1.0
