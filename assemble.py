#!/usr/bin/env python3
"""Fast-Clip Video Assembler CLI."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fast_clip.assembler import VideoAssembler


def print_usage():
    """Print usage information."""
    print("Usage: python assemble.py <script.json> [options]")
    print("")
    print("Options:")
    print("  -o, --output <dir>    Output directory (default: current)")
    print("  -v, --verbose         Verbose output")
    print("  -h, --help            Show this help")
    print("")
    print("Environment:")
    print("  SHOTSTACK_API_KEY     Shotstack API key (required)")
    print("")
    print("Examples:")
    print("  python assemble.py script_video_01.json")
    print("  python assemble.py script_video_01.json -v")
    print("  python assemble.py script_video_01.json -o ./output -v")


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

    # Create assembler and run
    print("🎬 Fast-Clip Video Assembler")
    print(f"   Script: {script_path}")
    if output_dir:
        print(f"   Output: {output_dir}")
    print("")

    assembler = VideoAssembler(api_key)
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
