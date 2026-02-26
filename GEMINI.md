# GEMINI.md - Fast-Clip Context

## Project Overview
Fast-Clip is a Python-based automation tool for creating videos using the **Shotstack API**. It allows users to define a video timeline in a human-readable **Markdown** table or a **Shotstack-native JSON** template. The tool handles the entire lifecycle: converting scripts, validating resources, uploading assets to the Shotstack Ingest API, and triggering/polling the final render.

### Core Technologies
- **Language:** Python 3.13+
- **Environment Management:** [uv](https://github.com/astral-sh/uv)
- **API Integration:** Shotstack Edit & Ingest APIs
- **Libraries:** `pydantic` (validation), `requests` (HTTP), `python-dotenv` (config), `ruff` (linting/formatting), `mypy` (type checking)

---

## Building and Running

### Setup
1.  **Install dependencies:**
    ```bash
    uv sync
    ```
2.  **Configure API Key:**
    Copy `.env.example` to `.env` and set `SHOTSTACK_API_KEY`.

### Key Commands
- **Convert Script:**
  ```bash
  # MD -> JSON or JSON -> MD (auto-detected)
  uv run python convert_script.py <script_file>
  ```
- **Validate Script:**
  ```bash
  uv run python check.py <json_file>
  ```
- **Assemble/Render Video:**
  ```bash
  # Using Python directly
  uv run python assemble.py <json_file>
  
  # Using shell wrapper
  ./build.sh <json_file>
  ```
- **Development & QA:**
  ```bash
  uv run mypy .             # Type checking
  uv run ruff check .       # Linting
  uv run ruff format .      # Formatting
  ```

---

## Project Structure & Architecture

### Layout
- `fast_clip/`: Core library package.
    - `check/`: Validation logic and CLI entry point for checking.
    - `assembler.py`: High-level orchestrator for the assembly process.
    - `shotstack_client.py`: Low-level Shotstack API client.
    - `uploader.py`: Handles asset staging via Shotstack Ingest API.
    - `timeline_builder.py`: Manages Template + Merge field logic.
- Root scripts (`convert_script.py`, `check.py`, `assemble.py`): CLI entry points.
- `Content/`: Default directory for local media assets.

### Data Flow
1.  **Scripting:** User writes a Markdown table.
2.  **Conversion:** `convert_script.py` generates a Shotstack-native JSON with `{{placeholders}}` for local files.
3.  **Validation:** `check.py` verifies JSON structure and local file existence.
4.  **Assembly:** `assemble.py` uploads local files, replaces `{{placeholders}}` with signed URLs, and submits the render to Shotstack.
5.  **Output:** Ready video is downloaded to the `output/` directory.

---

## Development Conventions

### Coding Standards
- **Linter/Formatter:** `ruff` is strictly enforced (100 char limit, PEP 8).
- **Type Safety:** Mandatory type hints for all functions/methods. Verified with `mypy`.
- **Documentation:** Use **Google-style** docstrings.
- **Naming:** `snake_case` for variables/functions, `PascalCase` for classes.
- **Tooling:** Always use `uv run` to ensure the correct environment and dependencies.

### Best Practices
- **Quiet/Verbose Modes:** All CLI tools should support `-q/--quiet` and `-v/--verbose` flags for better automation and debugging.
- **Resource Management:** Local files are looked up relative to the script's location or defined `resources_dir`.
- **API Safety:** Never log or commit the `SHOTSTACK_API_KEY`.

---

## Current Limitations
- **Text Overlays:** Not supported via `asset.overlay` (requires separate title clips).
- **Thumbnails:** `thumbnail_capture` is currently disabled due to Shotstack API validation issues.
- **Timeline Size:** Limited to 10 clips per timeline for stability.
