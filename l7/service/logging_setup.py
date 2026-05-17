"""Structured JSON logging to stderr. NFR-F1-2, masks secrets per NFR-F1-4."""

from __future__ import annotations

import json
import logging
import re
import sys
import time
from typing import Any

_SECRET_PATTERNS = (
    re.compile(r"(sk_hedra_[A-Za-z0-9_\-]+)"),
    re.compile(r"(Bearer\s+[A-Za-z0-9_\-\.]+)", re.IGNORECASE),
)


def _mask(value: str) -> str:
    masked = value
    for pat in _SECRET_PATTERNS:
        masked = pat.sub("sk_***", masked)
    return masked


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": _mask(record.getMessage()),
        }
        for key, value in record.__dict__.items():
            if key in {
                "args", "msg", "levelname", "name", "exc_info", "exc_text",
                "stack_info", "lineno", "funcName", "created", "msecs",
                "relativeCreated", "thread", "threadName", "processName",
                "process", "pathname", "filename", "module", "levelno",
            }:
                continue
            try:
                json.dumps(value)
                payload[key] = (
                    _mask(value) if isinstance(value, str) else value
                )
            except TypeError:
                payload[key] = repr(value)
        if record.exc_info:
            payload["exc"] = _mask(self.formatException(record.exc_info))
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    return logging.getLogger("l7")
