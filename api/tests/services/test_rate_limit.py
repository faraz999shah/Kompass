import pytest

from app.services.errors import RateLimitedError
from app.services.rate_limit import RateLimiter


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_allows_requests_up_to_the_limit() -> None:
    limiter = RateLimiter(limit=2, window_seconds=60, clock=FakeClock())

    limiter.check("phone")
    limiter.check("phone")

    with pytest.raises(RateLimitedError):
        limiter.check("phone")


def test_clients_are_counted_separately() -> None:
    limiter = RateLimiter(limit=1, window_seconds=60, clock=FakeClock())

    limiter.check("phone")
    limiter.check("laptop")


def test_requests_are_allowed_again_after_the_window() -> None:
    clock = FakeClock()
    limiter = RateLimiter(limit=1, window_seconds=60, clock=clock)
    limiter.check("phone")

    clock.now = 60.0

    limiter.check("phone")


def test_error_says_when_to_retry() -> None:
    clock = FakeClock()
    limiter = RateLimiter(limit=1, window_seconds=60, clock=clock)
    limiter.check("phone")
    clock.now = 45.0

    with pytest.raises(RateLimitedError) as raised:
        limiter.check("phone")

    assert raised.value.details["retry_after_seconds"] == 15.0
