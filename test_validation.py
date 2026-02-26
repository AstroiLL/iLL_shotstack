#!/usr/bin/env python3
"""Test script for resource directory validation from different working directories."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fast_clip.check.checker import ScriptChecker


def test_from_project_dir():
    """Test validation from project directory (with relative path)."""
    print("=" * 60)
    print("Test 1: From project directory (using relative path)")
    print("=" * 60)

    script_path = Path("/tmp/test_project/test-project.json")
    checker = ScriptChecker(script_path, verbose=True)

    is_valid, results = checker.check_all(), checker.results
    print(f"\nValid: {is_valid}")
    print(f"Results count: {len(results)}")


def test_from_parent_dir():
    """Test validation from parent directory (with absolute path)."""
    print("\n" + "=" * 60)
    print("Test 2: From parent directory (using absolute path)")
    print("=" * 60)

    script_path = Path("/tmp/test_project/test-project.json")
    checker = ScriptChecker(script_path, verbose=True)

    is_valid, results = checker.check_all(), checker.results
    print(f"\nValid: {is_valid}")
    print(f"Results count: {len(results)}")


def test_resources_validation():
    """Test that resources directory is resolved correctly."""
    print("\n" + "=" * 60)
    print("Test 3: Resources directory validation")
    print("=" * 60)

    # Change to test project directory
    import os

    os.chdir("/tmp/test_project")

    # Test with relative path
    script_path = Path("test-project.json")
    checker = ScriptChecker(script_path, verbose=True)

    is_valid, results = checker.check_all(), checker.results
    print(f"\nValid: {is_valid}")
    print(f"Results count: {len(results)}")


if __name__ == "__main__":
    test_from_project_dir()
    test_from_parent_dir()
    test_resources_validation()
