#!/bin/bash
# Fast-Clip Video Assembler - Quick start script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed"
    echo "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Show help
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Fast-Clip Video Assembler"
    echo ""
    echo "Usage:"
    echo "  ./build.sh <script.json>     Build video from script"
    echo "  ./build.sh -v <script.json>  Verbose mode"
    echo "  ./build.sh -o <dir> <script> Output directory"
    echo ""
    echo "Examples:"
    echo "  ./build.sh script_video_01.json"
    echo "  ./build.sh -v script_video_01.json"
    echo "  ./build.sh -o ./output script_video_01.json"
    exit 0
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    print_error ".env file not found"
    echo "Create .env file with your Shotstack API key:"
    echo "  cp .env.example .env"
    echo "  # Edit .env and add your API key"
    exit 1
fi

# Sync dependencies
print_info "Checking dependencies..."
uv sync --quiet

# Parse arguments
VERBOSE=""
OUTPUT=""
SCRIPT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -o|--output)
            OUTPUT="-o $2"
            shift 2
            ;;
        *.json)
            SCRIPT="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if script file provided
if [ -z "$SCRIPT" ]; then
    print_error "No script file provided"
    echo "Usage: ./build.sh <script.json>"
    echo "Use --help for more information"
    exit 1
fi

# Check if script exists
if [ ! -f "$SCRIPT" ]; then
    print_error "Script file not found: $SCRIPT"
    exit 1
fi

print_info "Building video from: $SCRIPT"

# Run assembly
if uv run python assemble.py "$SCRIPT" $VERBOSE $OUTPUT; then
    print_success "Video build completed!"
else
    print_error "Video build failed"
    exit 1
fi
