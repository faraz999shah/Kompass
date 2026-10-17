"""Per-client request limits for the voice endpoints, which spend paid speech quota.

In-memory and per process: enough for a single API instance. A deployment with
several instances would need a shared store instead.
"""

import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable

from app.services.errors import RateLimitedError


class RateLimiter:
    """Allows each client at most `limit` requests in any `window_seconds` span."""

    def __init__(
        self,
        limit: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._limit = limit
        self._window = window_seconds
        self._clock = clock
        self._recent: defaultdict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, client_id: str) -> None:
        """Record one request from the client.

        Raises:
            RateLimitedError: If the client is already at its limit.
        """
        now = self._clock()
        with self._lock:
            recent = self._recent[client_id]
            while recent and now - recent[0] >= self._window:
                recent.popleft()
            if len(recent) >= self._limit:
                retry_after = self._window - (now - recent[0])
                raise RateLimitedError(
                    "Too many voice requests; try again shortly",
                    {"retry_after_seconds": round(retry_after, 1)},
                )
            recent.append(now)
