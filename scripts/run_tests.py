"""
CodeSecure AI — Test Suite Runner
Executes all unit, security, RAG, and evaluation tests.
Supports pytest when installed, falling back cleanly to Python unittest runner.
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if __name__ == "__main__":
    print("=" * 60)
    print("  CodeSecure AI — Executing Comprehensive Test Suite")
    print("=" * 60)

    try:
        import pytest
        print("[+] Pytest detected. Running tests via pytest...\n")
        exit_code = pytest.main(["-v", "tests"])
        sys.exit(exit_code)
    except ImportError:
        print("[*] Pytest not installed in current environment. Using standard unittest runner...\n")
        loader = unittest.TestLoader()
        start_dir = str(Path(__file__).resolve().parent.parent / "tests")
        suite = loader.discover(start_dir, pattern="test_*.py")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
