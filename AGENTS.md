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

# Run individual scripts
uv run python check.py script.json              # Validate JSON script
uv run python check.py -v script.json           # Verbose validation
uv run python convert_script.py script.md       # Convert MD to JSON
uv run python convert_script.py script.json     # Convert JSON to MD
uv run python assemble.py script.json           # Assemble video (needs SHOTSTACK_API_KEY)
uv run python assemble.py script.json -v        # Verbose mode
uv run python assemble.py script.json -o ./out  # Custom output dir

# Type checking
uv run mypy .                                   # Check all files
uv run mypy fast_clip/check/validator.py        # Check single file

# Linting and formatting
uv run ruff check .                             # Lint all files
uv run ruff check --fix .                       # Auto-fix issues
uv run ruff format .                            # Format all files

# Run individual Python files
uv run python fast_clip/check/validator.py      # Run module directly
uv run python -m fast_clip.check                # Run as module
```

## Project Overview

Fast-Clip is a Python console utility for assembling video projects from fragments using the Shotstack API. JSON scripts define the assembly sequence.

**Key Components:**
- `fast_clip/check/` - Script validation (validator.py, checker.py)
- `convert_script.py` - Markdown/JSON format conversion
- `assemble.py` - Video assembly orchestrator
- `fast_clip/uploader.py` - Shotstack file upload
- `fast_clip/timeline_builder.py` - Script to Shotstack format conversion
- `fast_clip/shotstack_client.py` - Shotstack API client

## Code Style Guidelines

### Imports
Order: standard library, third-party, local. Use specific imports, avoid `*`.

```python
import json
from pathlib import Path
from typing import List, Optional, Tuple, Any

from pydantic import BaseModel, Field
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
def validate_item(item: Dict[str, Any], index: int) -> List[Tuple[str, str, Optional[str]]]:
    """Validate a single timeline item.

    Args:
        item: Timeline item dictionary
        index: Item index for error messages

    Returns:
        List of (status, message, suggestion) tuples
    """
```

### Project Structure
```
fast_clip/
├── __init__.py
├── check/              # Script validation
│   ├── __init__.py
│   ├── __main__.py
│   ├── checker.py
│   └── validator.py
├── uploader.py         # Shotstack file upload
├── timeline_builder.py # Convert scripts to Shotstack format
├── shotstack_client.py # Shotstack API client
└── assembler.py        # Video assembly orchestrator

Root scripts:
├── check.py            # Validate JSON scripts
├── convert_script.py   # MD/JSON converter
├── assemble.py         # Build video from script
└── check_json.py       # JSON validator
```

### Validation Patterns
Use constants for valid values. Return structured error tuples. Distinguish ERROR vs WARNING.

```python
SUPPORTED_FORMATS = {"mp4", "avi", "mov", "mkv"}
VALID_EFFECTS = {"fade_in", "fade_out", "slide_in", "slide_out"}

def check_format(fmt: str) -> Tuple[str, str, Optional[str]]:
    if fmt.lower() not in SUPPORTED_FORMATS:
        return ("WARNING", f"Unsupported format: '{fmt}'",
                f"Use: {', '.join(SUPPORTED_FORMATS)}")
    return ("OK", f"Format: '{fmt}'", None)
```

## Notes
- Python 3.13+ (see pyproject.toml)
- Dependencies: pydantic, requests, python-dotenv, mypy, ruff
- Use `pathlib.Path` for cross-platform file paths
- Scripts define video assembly sequences in JSON format
- Shotstack API used for cloud video processing
- No external test suite configured - test manually with sample scripts
- Requires `SHOTSTACK_API_KEY` in `.env` file
- Supports effects: fade_in, fade_out, slide_in, slide_out, cross_fade_in, cross_fade_out
