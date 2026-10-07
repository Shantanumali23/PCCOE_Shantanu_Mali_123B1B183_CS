"""
CodeSecure AI — Path Security Module
Prevents path traversal, symlink hijacking, and directory escaping.
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from app.config import settings
from app.utils.logging_utils import get_logger

logger = get_logger("path_security")


def resolve_safe_path(target_path_str: str, base_dir_str: Optional[str] = None) -> Tuple[bool, Optional[Path], str]:
    """
    Validates that a requested path strictly resides within the authorized base directory.
    Rejects:
    - Null bytes (\0)
    - Directory traversal sequences (../, ..\\)
    - Symlinks pointing outside the base directory
    - Absolute paths targeting arbitrary filesystem locations
    """
    if "\0" in target_path_str:
        return False, None, "Null byte detected in path."

    if base_dir_str is None:
        base_dir_str = settings.ALLOWED_REPOSITORIES_DIR

    base_path = Path(base_dir_str).resolve()
    # Ensure base directory exists
    base_path.mkdir(parents=True, exist_ok=True)

    try:
        # Resolve target relative to base if not absolute
        target_path = Path(target_path_str)
        if not target_path.is_absolute():
            candidate = (base_path / target_path).resolve()
        else:
            candidate = target_path.resolve()

        # Check path containment
        common = os.path.commonpath([str(base_path), str(candidate)])
        if os.path.abspath(common) != str(base_path):
            logger.warning(
                f"Path traversal blocked: candidate='{candidate}' outside base='{base_path}'"
            )
            return False, None, "Access denied: Path resides outside authorized directory."

        return True, candidate, ""
    except Exception as e:
        logger.error(f"Error resolving path '{target_path_str}': {e}")
        return False, None, f"Invalid path specification: {str(e)}"


def is_safe_path(target_path_str: str, base_dir_str: Optional[str] = None) -> bool:
    """Convenience boolean check for path safety."""
    is_valid, _, _ = resolve_safe_path(target_path_str, base_dir_str)
    return is_valid
