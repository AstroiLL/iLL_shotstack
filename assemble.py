#!/usr/bin/env python3
"""Fast-Clip Video Assembler CLI."""

import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fast_clip.assembler import VideoAssembler
from fast_clip.check.validation import (
    JsonValidator,
    FileChecker,
    FieldValidator,
    ValidationLevel,
)


def print_usage():
    """Print usage information."""
    print("Usage: python assemble.py <script.json> [options]")
    print("")
    print("Options:")
    print("  -o, --output <dir>    Output directory or file path")
    print("                        (default: <script_dir>/output/<name>.mp4)")
    print("  -v, --verbose         Verbose output")
    print("  --skip-validate        Skip validation (not recommended)")
    print("  --strict              Enable strict validation mode")
    print("  -h, --help            Show this help")
    print("")
    print("Environment:")
    print("  SHOTSTACK_API_KEY     Shotstack API key (required)")
    print("")
    print("Examples:")
    print("  python assemble.py script_video_01.json")
    print("  python assemble.py script_video_01.json -v")
    print("  python assemble.py script_video_01.json -o ./output -v")
    print("  python assemble.py script_video_01.json -o ./output/custom_name.mp4 -v")


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Parse arguments
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print_usage()
        sys.exit(0)

    script_path = Path(args[0])

    output_dir = None
    verbose = False
    skip_validate = False
    strict_mode = False

    i = 1
    while i < len(args):
        if args[i] in ("-o", "--output"):
            if i + 1 >= len(args):
                print("Error: --output requires a directory")
                sys.exit(1)
            output_dir = Path(args[i + 1])
            i += 2
        elif args[i] in ("-v", "--verbose"):
            verbose = True
            i += 1
        elif args[i] == "--skip-validate":
            skip_validate = True
            i += 1
        elif args[i] == "--strict":
            strict_mode = True
            i += 1
        elif args[i] in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        else:
            print(f"Unknown option: {args[i]}")
            print_usage()
            sys.exit(1)

    # Check API key
    api_key = os.getenv("SHOTSTACK_API_KEY")
    if not api_key:
        print("❌ Error: SHOTSTACK_API_KEY not set")
        print("Please set your API key:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your API key to .env")
        print("  3. Or set environment variable: export SHOTSTACK_API_KEY=your_key")
        print("")
        print("Get your API key from: https://shotstack.io/")
        sys.exit(1)

    # Check script exists
    if not script_path.exists():
        print(f"❌ Error: Script not found: {script_path}")
        sys.exit(1)

    # Check file format
    if script_path.suffix == ".md":
        print("❌ Error: Markdown files are not supported directly.")
        print("   Please convert to JSON first:")
        print(f"   uv run python convert_script.py {script_path}")
        sys.exit(1)
    elif script_path.suffix != ".json":
        print(f"❌ Error: Unsupported file format '{script_path.suffix}'")
        print("   Supported formats: .json")
        sys.exit(1)

    # Create assembler and run
    print("🎬 Fast-Clip Video Assembler")
    print(f"   Script: {script_path}")
    if output_dir:
        print(f"   Output: {output_dir}")
    print("")

    # Validate script before assembly (unless skipped)
    if not skip_validate:
        print("🔍 Validating script...")

        # Load script data
        with open(script_path, "r") as f:
            script_data = json.load(f)

        # Initialize validators
        json_validator = JsonValidator(strict_mode=strict_mode)
        file_checker = FileChecker(strict_mode=strict_mode, script_path=script_path)
        field_validator = FieldValidator(strict_mode=strict_mode)

        # Run validation
        json_report = json_validator.validate(script_data)
        file_report = file_checker.validate(script_data)
        field_report = field_validator.validate(script_data)

        # Combine results and check for errors
        total_errors = (
            json_report.total_errors
            + file_report.total_errors
            + field_report.total_errors
        )
        total_warnings = (
            json_report.total_warnings
            + file_report.total_warnings
            + field_report.total_warnings
        )

        if total_errors > 0:
            print("❌ Validation FAILED - errors found:")
            all_results = (
                json_report.results + file_report.results + field_report.results
            )
            for result in all_results:
                if result.level == ValidationLevel.ERROR:
                    print(f"  ✗ {result.field or 'unknown'}: {result.message}")
                    if result.suggestion:
                        print(f"    → {result.suggestion}")
            print("")
            print("Fix errors before proceeding with assembly.")
            sys.exit(1)

        if total_warnings > 0:
            print("⚠️  Validation passed with warnings:")
            if verbose:
                all_results = (
                    json_report.results + file_report.results + field_report.results
                )
                for result in all_results:
                    if result.level == ValidationLevel.WARNING:
                        print(f"  ! {result.field or 'unknown'}: {result.message}")
                        if result.suggestion:
                            print(f"    → {result.suggestion}")
            print("")
        else:
            print("✅ Validation passed")
        print("")
    else:
        print("⚠️  Skipping validation (not recommended)")
        print("")

        # Load script data for assembler
        with open(script_path, "r") as f:
            script_data = json.load(f)

    assembler = VideoAssembler(api_key)

    if "template" in script_data:
        print("📋 Using template + merge workflow")
        result = assembler.assemble_with_template(
            script_path, output_dir, verbose=verbose
        )
    else:
        print("📋 Using direct workflow")
        result = assembler.assemble(script_path, output_dir, verbose=verbose)

    if result.success:
        print("")
        print("✅ Success!")
        print(f"   Output: {result.output_path}")
        print(f"   Render ID: {result.render_id}")
        sys.exit(0)
    else:
        print("")
        print(f"❌ Failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
