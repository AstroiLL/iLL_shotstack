"""CLI for check module."""

import sys
from pathlib import Path

from .checker import check_script


def main():
    """Main entry point for check CLI."""
    verbose = False
    script_path = None

    # Parse arguments
    for arg in sys.argv[1:]:
        if arg == "-v" or arg == "--verbose":
            verbose = True
        elif arg.startswith("-"):
            print(f"Unknown option: {arg}")
            print("Usage: python -m fast_clip.check [-v] <script.json>")
            print("       fast-clip-check [-v] <script.json>")
            sys.exit(2)
        else:
            script_path = arg

    if not script_path:
        print("Usage: python -m fast_clip.check [-v] <script.json>")
        print("       fast-clip-check [-v] <script.json>")
        print("")
        print("Options:")
        print("  -v, --verbose    Show detailed check results")
        print("")
        print("Examples:")
        print("  python -m fast_clip.check script.json          # Silent mode")
        print("  python -m fast_clip.check -v script.json       # Verbose mode")
        print("  fast-clip-check script.json                    # Using entry point")
        sys.exit(2)

    is_valid, results = check_script(Path(script_path), verbose)

    # In silent mode, show errors only
    if not verbose and not is_valid:
        print(f"\nScript validation failed for: {script_path}")
        print("\nErrors found:")
        for result in results:
            if result.status == "ERROR":
                print(f"  ✗ {result.field}: {result.message}")
                if result.suggestion:
                    print(f"    → {result.suggestion}")
        print(
            f"\nUse -v flag for detailed output: python -m fast_clip.check -v {script_path}"
        )

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
