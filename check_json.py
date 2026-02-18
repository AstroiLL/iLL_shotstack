#!/usr/bin/env python3
"""Fast-Clip Script Checker - Interactive CLI wrapper."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fast_clip.check import check_script


def main():
    """Main entry point."""
    verbose = False
    script_path = None

    # Parse arguments
    for arg in sys.argv[1:]:
        if arg == "-v" or arg == "--verbose":
            verbose = True
        elif arg.startswith("-"):
            print(f"Unknown option: {arg}")
            print("Usage: python check_json.py [-v] <script.json>")
            sys.exit(2)
        else:
            script_path = arg

    if not script_path:
        print("Usage: python check_json.py [-v] <script.json>")
        print("")
        print("Options:")
        print("  -v, --verbose    Show detailed check results")
        print("")
        print("Examples:")
        print("  python check_json.py script.json          # Silent mode")
        print("  python check_json.py -v script.json       # Verbose mode")
        sys.exit(2)

    is_valid, results = check_script(Path(script_path), verbose)

    # In silent mode with errors, show summary
    if not verbose and not is_valid:
        errors = [r for r in results if r.status == "ERROR"]
        print(f"\n✗ Validation failed: {len(errors)} error(s) found")
        print(f"\nUse -v flag for details: python check_json.py -v {script_path}")
    elif not verbose and is_valid:
        print("✓ Validation passed")

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
