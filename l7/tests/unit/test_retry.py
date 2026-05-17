"""Unit tests for retry helper. Covers T-U-RT-1..4."""

from __future__ import annotations

import pytest

from l7.service.retry import RetryError, with_retry


class FakeResp:
    def __init__(self, status: int) -> None:
        self.status_code = status


# T-U-RT-1 — retries 429/5xx up to 4 times.
def test_retries_5xx():
    calls = []

    def fn():
        calls.append(1)
        return FakeResp(503) if len(calls) < 5 else FakeResp(200)

    sleeps = []
    out = with_retry(fn, sleeper=lambda d: sleeps.append(d), jitter=0)
    assert out.status_code == 200
    assert len(calls) == 5  # 1 initial + 4 retries
    assert sleeps == [2.0, 4.0, 8.0, 16.0]


# T-U-RT-2 — backoff sequence is 2/4/8/16 (jitter applied).
def test_backoff_sequence_with_jitter():
    calls = []

    def fn():
        calls.append(1)
        return FakeResp(429)

    sleeps = []
    with pytest.raises(RetryError):
        with_retry(fn, sleeper=lambda d: sleeps.append(d), jitter=0.5)
    # 4 retries → 4 sleeps. jitter applied
    assert len(sleeps) == 4
    expected = [2.0, 4.0, 8.0, 16.0]
    for s, e in zip(sleeps, expected):
        assert e - 0.5 <= s <= e + 0.5


# T-U-RT-3 — 4xx (except 429) doesn't retry.
def test_no_retry_on_4xx_except_429():
    calls = []

    def fn():
        calls.append(1)
        return FakeResp(404)

    out = with_retry(fn, sleeper=lambda d: None, jitter=0)
    assert out.status_code == 404
    assert len(calls) == 1


# T-U-RT-4 — exception path retries on connection errors and gives up.
def test_connection_error_retries_then_raises():
    calls = []

    def fn():
        calls.append(1)
        raise ConnectionError("boom")

    with pytest.raises(RetryError):
        with_retry(fn, sleeper=lambda d: None, jitter=0)
    assert len(calls) == 5
