#!/usr/bin/env python3
"""
Migration script for transitioning from legacy check_json.py to new check.py.

This script provides guidance for users upgrading from the old validation system
to the new modular validation framework.
"""

import sys
from pathlib import Path


def print_migration_info():
    """Print migration information."""
    print("=" * 70)
    print("Fast-Clip Validation System Migration Guide")
    print("=" * 70)
    print()

    print("OVERVIEW")
    print("-" * 70)
    print("The validation system has been upgraded with:")
    print("  • Comprehensive JSON structure validation")
    print("  • Media file availability checking")
    print("  • Shotstack SDK field validation")
    print("  • Integrated validation in converter and assembler")
    print("  • Performance optimizations for large projects")
    print()

    print("CHANGES")
    print("-" * 70)
    print("Old command: python check_json.py script.json")
    print("New command: python check.py script.json")
    print()

    print("COMMAND MAPPING")
    print("-" * 70)
    commands = [
        (
            "python check_json.py script.json",
            "python check.py script.json",
            "Basic validation",
        ),
        (
            "python check_json.py -v script.json",
            "python check.py -v script.json",
            "Verbose mode",
        ),
        ("N/A", "python check.py -q script.json", "Quiet mode (exit code only)"),
        ("N/A", "python check.py --strict script.json", "Strict validation mode"),
        (
            "N/A",
            "python check.py --skip-validate script.json",
            "Skip comprehensive validation",
        ),
    ]
    for old, new, description in commands:
        print(f"  {old:40} → {new}")
        print(f"  {description:37} ({description})")
        print()

    print("NEW FEATURES")
    print("-" * 70)
    features = [
        ("File Validation", "Checks media file availability and permissions"),
        (
            "Field Validation",
            "Validates transitions, effects, filters against Shotstack SDK",
        ),
        ("Template Validation", "Validates Shotstack Template JSON structure"),
        ("Merge Validation", "Checks placeholder syntax and merge array structure"),
        ("Performance", "Parallel file checking for large projects"),
    ]
    for feature, description in features:
        print(f"  • {feature:20} {description}")
    print()

    print("CONFIGURATION")
    print("-" * 70)
    print("You can customize validation behavior via:")
    print("  1. Configuration file: .validation.toml")
    print("  2. Environment variables: VALIDATION_*")
    print("  3. Command-line flags (highest priority)")
    print()
    print("Example .validation.toml:")
    print("  [validation]")
    print("  strict_mode = false")
    print("  max_workers = 8")
    print("  parallel_threshold = 5")
    print("  enable_cache = true")
    print()

    print("INTEGRATION")
    print("-" * 70)
    print("Validation is now integrated into:")
    print("  • convert_script.py - Validates JSON after conversion")
    print("  • assemble.py - Validates JSON before assembly")
    print()
    print("Both tools respect --skip-validate flag for quick operations.")
    print()

    print("BACKWARD COMPATIBILITY")
    print("-" * 70)
    print("The old check_json.py is still available for compatibility.")
    print("It wraps the new validation system internally.")
    print()
    print("Note: check_json.py will be deprecated in a future release.")
    print()

    print("NEXT STEPS")
    print("-" * 70)
    steps = [
        "1. Update your scripts to use 'python check.py' instead of 'python check_json.py'",
        "2. Review validation output for new warnings and suggestions",
        "3. Create .validation.toml for project-specific settings (optional)",
        "4. Consider adding validation to CI/CD pipelines",
    ]
    for step in steps:
        print(f"  {step}")
    print()

    print("=" * 70)
    print("For more information, see: README.md")
    print("=" * 70)


def check_files():
    """Check if migration files exist."""
    print("CHECKING FILES...")
    print("-" * 70)

    files = [
        ("check.py", "New validation script"),
        ("check_json.py", "Legacy wrapper (still functional)"),
        ("fast_clip/check/validation/", "New validation modules"),
        (".validation.toml.example", "Example configuration file"),
    ]

    for file_path, description in files:
        path = Path(file_path)
        status = "✓" if path.exists() else "✗"
        print(f"  {status} {file_path:40} {description}")

    print()
    print("=" * 70)


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("Usage: python migrate_validation.py")
        print()
        print("This script provides information about migrating from the old")
        print("check_json.py to the new modular validation system.")
        sys.exit(0)

    print_migration_info()
    print()
    check_files()

    print()
    print("Migration script completed successfully!")
    print("Update your workflows to use the new check.py script.")
    sys.exit(0)


if __name__ == "__main__":
    main()
