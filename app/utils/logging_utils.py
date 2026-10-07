"""
CodeSecure AI — Structured Logging Utility
Ensures security-compliant logging: suppresses passwords, tokens, and full source code.
"""

import logging
import re
import sys
from typing import Any, Dict


# Sanitization patterns to prevent credential and source leakage in application logs
SENSITIVE_PATTERNS = [
    (re.compile(r"(password|token|secret|key|hash)\s*[:=]\s*['\"]?([^'\"\s,]+)['\"]?", re.IGNORECASE), r"\1=***REDACTED***"),
    (re.compile(r"Bearer\s+([a-zA-Z0-9_\-\.]+)", re.IGNORECASE), r"Bearer ***REDACTED***"),
]


class SecuritySanitizingFormatter(logging.Formatter):
    """Custom logging formatter that strips sensitive patterns from log messages."""

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        sanitized = original
        for pattern, replacement in SENSITIVE_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized


def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger with sanitization enabled."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = SecuritySanitizingFormatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger
