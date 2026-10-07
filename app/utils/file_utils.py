"""
CodeSecure AI — File Utility Functions
Provides safe file I/O, hash calculation, and directory scanning.
"""

import hashlib
import os
from pathlib import Path
from typing import List, Optional, Tuple


def calculate_sha256(content: str) -> str:
    """Calculates SHA-256 hash of text content for auditing and deduplication."""
    return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()


def read_text_file_safe(file_path: Path, max_bytes: int = 2 * 1024 * 1024) -> Tuple[bool, str, Optional[str]]:
    """
    Safely reads text file with byte limits and UTF-8 validation.
    Returns (success, content_or_error_message, file_hash).
    """
    if not file_path.exists():
        return False, f"File does not exist: {file_path}", None
    if not file_path.is_file():
        return False, f"Path is not a regular file: {file_path}", None

    file_size = file_path.stat().st_size
    if file_size > max_bytes:
        return False, f"File size ({file_size} bytes) exceeds limit ({max_bytes} bytes)", None

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        content_hash = calculate_sha256(content)
        return True, content, content_hash
    except Exception as e:
        return False, f"Error reading file: {str(e)}", None


def list_files_recursive(directory: Path, allowed_extensions: List[str]) -> List[Path]:
    """Recursively lists files matching allowed extensions."""
    if not directory.exists() or not directory.is_dir():
        return []
    matches = []
    for root, _, files in os.walk(directory):
        for f in files:
            path = Path(root) / f
            if any(path.name.lower().endswith(ext.lower()) for ext in allowed_extensions):
                matches.append(path)
    return sorted(matches)
