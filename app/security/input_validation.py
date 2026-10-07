"""
CodeSecure AI — Input Validation Module
Validates source code, log payloads, file extensions, and file sizes.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple
from app.config import settings


def sanitize_filename(filename: str) -> str:
    """Removes path separators and dangerous characters from user-supplied filenames."""
    # Strip any directory path components
    basename = os.path.basename(filename.strip())
    # Keep only alphanumeric, dots, underscores, dashes
    sanitized = re.sub(r"[^a-zA-Z0-9_\.\-]", "_", basename)
    # Remove leading dots to prevent hidden files
    sanitized = sanitized.lstrip(".")
    return sanitized or "unnamed_file.cpp"


def validate_file_extension(filename: str, allowed_extensions: Optional[List[str]] = None) -> Tuple[bool, str]:
    """Ensures file extension matches approved C/C++ or log extensions."""
    if allowed_extensions is None:
        allowed_extensions = settings.ALLOWED_FILE_EXTENSIONS

    ext = Path(filename).suffix.lower()
    if not ext:
        return False, "File must have an explicit extension (e.g., .c, .cpp, .h, .log)"

    if ext not in [e.lower() for e in allowed_extensions]:
        return False, f"Extension '{ext}' is not permitted. Allowed: {', '.join(allowed_extensions)}"

    return True, ""


def validate_code_content(code: str, max_size_bytes: Optional[int] = None) -> Tuple[bool, str]:
    """
    Validates source code text:
    - Non-empty
    - Under maximum size
    - Plain text (not binary)
    """
    if not code or not code.strip():
        return False, "Source code cannot be empty."

    if max_size_bytes is None:
        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    encoded_bytes = code.encode("utf-8", errors="replace")
    if len(encoded_bytes) > max_size_bytes:
        return False, f"Source code size ({len(encoded_bytes)} bytes) exceeds limit ({max_size_bytes} bytes)."

    # Binary heuristic: check for null bytes
    if "\0" in code:
        return False, "Uploaded file appears to be a binary executable, not C/C++ source code."

    # Minimum threshold check: needs some characters
    if len(code.strip()) < 5:
        return False, "Input code is too brief to analyze meaningfully."

    return True, ""


def validate_log_content(log_text: str, max_size_bytes: Optional[int] = None) -> Tuple[bool, str]:
    """Validates compiler or runtime log payload."""
    if not log_text or not log_text.strip():
        return False, "Log content cannot be empty."

    if max_size_bytes is None:
        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if len(log_text.encode("utf-8", errors="replace")) > max_size_bytes:
        return False, f"Log size exceeds maximum allowed size ({max_size_bytes} bytes)."

    if "\0" in log_text:
        return False, "Log file contains binary content."

    return True, ""
