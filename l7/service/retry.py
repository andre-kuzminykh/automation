"""Retry helper with exponential backoff. Covers NR-F1-6, NFR-F1-5."""

from __future__ import annotations

import random
import time
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")

DEFAULT_BACKOFFS = (2.0, 4.0, 8.0, 16.0)


class RetryError(Exception):
    """Raised when all retry attempts have been exhausted."""


def with_retry(
    fn: Callable[[], T],
    *,
    retry_on_status: Iterable[int] = (429, 500, 502, 503, 504),
    retry_on_exceptions: tuple[type[BaseException], ...] = (
        ConnectionError,
        TimeoutError,
    ),
    backoffs: Iterable[float] = DEFAULT_BACKOFFS,
    sleeper: Callable[[float], None] = time.sleep,
    jitter: float = 0.5,
) -> T:
    """Run `fn` with retry. `fn` may either return a value or raise.

    If the returned value has `.status_code` attribute, it is checked against
    `retry_on_status`.

    Backoffs: 2, 4, 8, 16 seconds with random jitter ±`jitter`s.
    """
    delays = list(backoffs)
    last_exc: BaseException | None = None
    last_status: int | None = None

    for attempt in range(len(delays) + 1):
        try:
            result = fn()
            status = getattr(result, "status_code", None)
            if status is not None and int(status) in retry_on_status:
                last_status = int(status)
                if attempt >= len(delays):
                    raise RetryError(
                        f"all retries exhausted, last status={last_status}"
                    )
            else:
                return result
        except retry_on_exceptions as exc:
            last_exc = exc
            if attempt >= len(delays):
                raise RetryError(f"all retries exhausted: {exc}") from exc

        delay = delays[attempt] + random.uniform(-jitter, jitter)
        sleeper(max(0.0, delay))

    # unreachable in practice
    raise RetryError(
        f"unreachable retry path; last_exc={last_exc}, last_status={last_status}"
    )
