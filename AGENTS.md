<!-- OPENSPEC:START -->
# OpenSpec Instructions

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning/proposals (proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, or architecture shifts
- Sounds ambiguous and you need the authoritative spec

Use it to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines
<!-- OPENSPEC:END -->

# AGENTS.md

Guidelines for AI coding agents working in this repository.

## Build, Lint, and Test Commands

```bash
# Install/sync dependencies
uv sync

# Convert MD to Shotstack JSON
uv run python convert_script.py script.md              # Convert to JSON
uv run python convert_script.py script.md output.json  # Custom output

# Validate Shotstack-native JSON
uv run python check.py script.json              # Validate script
uv run python check.py -v script.json           # Verbose validation

# Assemble video (needs SHOTSTACK_API_KEY in .env)
uv run python assemble.py script.json           # Assemble video
uv run python assemble.py script.json -v        # Verbose mode
uv run python assemble.py script.json -o ./out  # Custom output dir

# Quick build using shell script
./build.sh script.json                          # Quick build
./build.sh -v script.json                       # Verbose
./build.sh -o ./output script.json              # Custom output

# Type checking
uv run mypy .                                   # Check all files
uv run mypy convert_script.py                   # Check single file

# Linting and formatting
uv run ruff check .                             # Lint all files
uv run ruff check --fix .                       # Auto-fix issues
uv run ruff format .                            # Format all files

# Run individual Python files
uv run python convert_script.py script.md       # Run converter
uv run python check.py script.json              # Run validator
```

## Project Overview

Fast-Clip is a Python console utility for assembling video projects from fragments using the Shotstack API.

**Workflow:**
1. Create script in Markdown format with table-based timeline
2. Convert MD to Shotstack-native JSON using `convert_script.py`
3. Validate JSON using `check.py`
4. Assemble video using `assemble.py` (uploads to Shotstack, renders, downloads)

**Key Components:**
- `convert_script.py` - Converts Markdown scripts to Shotstack-native JSON
- `check.py` - Validates Shotstack-native JSON scripts
- `assemble.py` - Video assembly orchestrator CLI
- `fast_clip/uploader.py` - Shotstack file upload (Ingest API)
- `fast_clip/timeline_builder.py` - Replaces `{{placeholders}}` with URLs
- `fast_clip/shotstack_client.py` - Shotstack Edit API client
- `fast_clip/assembler.py` - Main assembly orchestrator

## Supported Shotstack Features

### Transitions (trans_in, trans_out)
fade, fadeFast, fadeSlow, slideLeft, slideRight, slideUp, slideDown, slideLeftFast, slideRightFast, wipeLeft, wipeRight, wipeLeftFast, wipeRightFast, carouselLeft, carouselRight, carouselUpFast, shuffleTopRight, shuffleLeftBottom, reveal, revealFast, revealSlow, zoom, zoomFast, zoomSlow

### Effects
effect: zoomIn, zoomOut, kenBurns

### Filters
filter: boost, greyscale, contrast, muted, negative, darken, lighten

### Aspect Ratios
aspect_ratio: 9:16, 16:9, 1:1, 4:5, 4:3

## Code Style Guidelines

### Imports
Order: standard library, third-party, local. Use specific imports, avoid `*`.

```python
import json
import re
from pathlib import Path
from typing import List, Optional, Tuple, Any, Dict
```

### Formatting
- ruff formatter (PEP 8 compliant)
- Max line length: 100 characters
- 4 spaces indentation
- f-strings for interpolation
- Trailing commas in multi-line collections

### Type Hints
Use for all parameters and return values. Use `Path` for file paths.

```python
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class CheckResult:
    field: str
    status: str
    message: str
    suggestion: Optional[str] = None

def validate(data: Dict[str, Any]) -> List[Tuple[str, str, Optional[str]]]:
    pass
```

### Naming Conventions
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`
- Module names: `snake_case`

### Error Handling
Use specific exceptions, descriptive messages, context managers. Return error tuples: `(status, message, suggestion)`.

```python
def load_script(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(f"Script not found: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}") from e
```

### Documentation
Google-style docstrings with Args, Returns, Raises sections.

```python
def validate_clip(clip: Dict[str, Any], index: int) -> List[Tuple[str, str, Optional[str]]]:
    """Validate a single timeline clip.

    Args:
        clip: Clip dictionary from timeline.tracks[].clips[]
        index: Clip index for error messages

    Returns:
        List of (status, message, suggestion) tuples
    """
```

### Project Structure
```
fast_clip/
├── __init__.py
├── check/              # Script validation (Shotstack-native JSON)
│   ├── __init__.py
│   ├── __main__.py
│   ├── checker.py
│   └── validator.py
├── uploader.py         # Shotstack file upload
├── timeline_builder.py # Replace {{}} placeholders with URLs
├── shotstack_client.py # Shotstack API client
└── assembler.py        # Video assembly orchestrator

Root scripts:
├── check.py            # Validate Shotstack-native JSON
├── convert_script.py   # MD → Shotstack JSON converter
├── assemble.py         # Build video from script
└── check_json.py       # Legacy JSON validator (deprecated)
```

### Validation Patterns
Use constants for valid Shotstack values. Return structured error tuples. Distinguish ERROR vs WARNING.

```python
VALID_TRANSITIONS = {
    "fade", "fadefast", "fadeslow",
    "slideleft", "slideright", "slideup", "slidedown",
    "zoom", "zoomfast", "kenburns",
}
VALID_EFFECTS = {"zoomin", "zoomout", "kenburns"}
VALID_FILTERS = {"boost", "greyscale", "contrast", "muted"}

def check_transition(trans: str) -> Tuple[str, str, Optional[str]]:
    if trans.lower() not in VALID_TRANSITIONS:
        return ("WARNING", f"Unknown transition: '{trans}'",
                f"Use: {', '.join(sorted(VALID_TRANSITIONS))}")
    return ("OK", f"Transition: '{trans}'", None)
```

## Notes
- Python 3.13+ (see pyproject.toml)
- Dependencies: pydantic, requests, python-dotenv, mypy, ruff
- Use `pathlib.Path` for cross-platform file paths
- Scripts are now in Shotstack-native JSON format (converted from MD)
- Shotstack API used for cloud video processing
- Placeholders use `{{resources_dir/filename}}` format
- Requires `SHOTSTACK_API_KEY` in `.env` file
- Supports all Shotstack transitions, effects, and filters
