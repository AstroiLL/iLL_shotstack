#!/usr/bin/env python3
"""Fast-Clip Script Converter: Convert between MD and JSON formats."""

import json
import re
import sys
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

# Import check module
from fast_clip.check import check_script


class TimelineItem(BaseModel):
    """Single timeline item."""

    id: int
    resource: str
    time_start: str
    time_end: str
    start_effect: Optional[str] = None
    start_duration: Optional[str] = None
    effect_during: Optional[str] = None
    end_effect: Optional[str] = None
    end_duration: Optional[str] = None
    description: Optional[str] = None


class ScriptConfig(BaseModel):
    """Video assembly script configuration."""

    name: str
    resources_dir: str
    timeline: List[TimelineItem]
    result_file: str
    output_format: Optional[str] = None
    resolution: Optional[str] = "1080p"
    orientation: Optional[str] = "landscape"


def parse_time_to_str(seconds: int) -> str:
    """Convert seconds to MM:SS format."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def parse_md_time(time_str: str) -> tuple[str, str]:
    """Parse time from markdown format."""
    time_str = time_str.strip()
    if " - " in time_str:
        parts = time_str.split(" - ")
        return parts[0].strip(), parts[1].strip()
    return time_str, time_str


def parse_md_duration(duration_str: str) -> Optional[str]:
    """Parse duration from markdown format."""
    duration_str = duration_str.strip()
    if not duration_str or duration_str == "":
        return None
    match = re.match(r"(\d+)\s*sec", duration_str)
    if match:
        return f"{match.group(1)}s"
    return duration_str if duration_str else None


def parse_md_effect(effect_str: str) -> Optional[str]:
    """Parse effect name from markdown format."""
    effect_str = effect_str.strip().lower()
    if not effect_str or effect_str == "":
        return None
    return effect_str.replace(" ", "_")


def md_to_json(md_path: Path) -> ScriptConfig:
    """Convert markdown script to JSON configuration."""
    content = md_path.read_text(encoding="utf-8")

    # Parse headers
    name_match = re.search(r"##\s*name:\s*(.+)", content)
    resources_match = re.search(r"##\s*resources_dir:\s*(.+)", content)
    result_match = re.search(r"##\s*result_file:\s*(.+)", content)
    output_format_match = re.search(r"##\s*output_format:\s*(.+)", content)
    resolution_match = re.search(r"##\s*resolution:\s*(.+)", content)
    orientation_match = re.search(r"##\s*orientation:\s*(.+)", content)

    if not all([name_match, resources_match, result_match]):
        raise ValueError("Missing required headers in markdown file")

    assert (
        name_match is not None
        and resources_match is not None
        and result_match is not None
    )
    name = name_match.group(1).strip()
    resources_dir = resources_match.group(1).strip()
    result_file = result_match.group(1).strip()
    output_format = (
        output_format_match.group(1).strip() if output_format_match else None
    )
    resolution = resolution_match.group(1).strip() if resolution_match else "1080p"
    orientation = (
        orientation_match.group(1).strip() if orientation_match else "landscape"
    )

    # Parse table
    timeline = []
    lines = content.split("\n")
    in_table = False

    for line in lines:
        line = line.strip()
        if line.startswith("| # "):
            in_table = True
            continue
        if in_table and line.startswith("| ---"):
            continue
        if in_table and line.startswith("|") and not line.startswith("| ---"):
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            if len(cells) >= 8:
                try:
                    time_start, time_end = parse_md_time(cells[2])
                    timeline.append(
                        TimelineItem(
                            id=int(cells[0]),
                            resource=cells[1],
                            time_start=time_start,
                            time_end=time_end,
                            start_effect=parse_md_effect(cells[3]),
                            start_duration=parse_md_duration(cells[4]),
                            effect_during=parse_md_effect(cells[5])
                            if cells[5]
                            else None,
                            end_effect=parse_md_effect(cells[6]),
                            end_duration=parse_md_duration(cells[7]),
                            description=cells[8]
                            if len(cells) > 8 and cells[8]
                            else None,
                        )
                    )
                except (ValueError, IndexError):
                    print(f"Warning: Skipping invalid row: {line}")
                    continue

    return ScriptConfig(
        name=name,
        resources_dir=resources_dir,
        timeline=timeline,
        result_file=result_file,
        output_format=output_format,
        resolution=resolution,
        orientation=orientation,
    )


def json_to_md(config: ScriptConfig) -> str:
    """Convert JSON configuration to markdown format."""
    lines = []

    # Headers
    lines.append(f"## name: {config.name}")
    lines.append(f"## resources_dir: {config.resources_dir}")
    lines.append("")

    # Optional headers
    if config.output_format:
        lines.append(f"## output_format: {config.output_format}")
    if config.resolution and config.resolution != "1080p":
        lines.append(f"## resolution: {config.resolution}")
    if config.orientation and config.orientation != "landscape":
        lines.append(f"## orientation: {config.orientation}")
    if (
        config.output_format
        or (config.resolution and config.resolution != "1080p")
        or (config.orientation and config.orientation != "landscape")
    ):
        lines.append("")

    # Table header
    lines.append(
        "| # | Resources | Time | Start_Effect | Start_Duration | Effect_During | End_Effect | End_Duration | Description"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")

    # Table rows
    for item in config.timeline:
        time_range = f"{item.time_start} - {item.time_end}"
        start_effect = (item.start_effect or "").replace("_", " ")
        start_duration = (item.start_duration or "").replace("s", " sec")
        effect_during = (item.effect_during or "").replace("_", " ")
        end_effect = (item.end_effect or "").replace("_", " ")
        end_duration = (item.end_duration or "").replace("s", " sec")
        description = item.description or ""

        lines.append(
            f"| {item.id} | {item.resource} | {time_range} | {start_effect} | "
            f"{start_duration} | {effect_during} | {end_effect} | {end_duration} | {description}"
        )

    lines.append("")
    lines.append(f"## result_file: {config.result_file}")
    lines.append("")

    return "\n".join(lines)


def convert_file(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """Convert file between MD and JSON formats."""
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix == ".md":
        # MD to JSON
        config = md_to_json(input_path)
        if output_path is None:
            output_path = input_path.with_suffix(".json")
        output_path.write_text(
            json.dumps(config.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Converted: {input_path} -> {output_path}")

    elif input_path.suffix == ".json":
        # Validate JSON before conversion
        print(f"Validating: {input_path}")
        is_valid, results = check_script(input_path, verbose=False)

        if not is_valid:
            print("\n✗ Validation failed with errors:")
            for result in results:
                if result.status == "ERROR":
                    print(f"  ✗ {result.field}: {result.message}")
                    if result.suggestion:
                        print(f"    → {result.suggestion}")
            print("\nPlease fix the errors before converting.")
            raise ValueError("Script validation failed")

        warnings = [r for r in results if r.status == "WARNING"]
        if warnings:
            print(f"⚠ Validation passed with {len(warnings)} warning(s)")
        else:
            print("✓ Validation passed")

        # JSON to MD
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        config = ScriptConfig(**data)
        if output_path is None:
            output_path = input_path.with_suffix(".md")
        output_path.write_text(json_to_md(config), encoding="utf-8")
        print(f"Converted: {input_path} -> {output_path}")

    else:
        raise ValueError(
            f"Unsupported file format: {input_path.suffix}. Use .md or .json"
        )

    return output_path


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python convert_script.py <input_file> [output_file]")
        print("       python convert_script.py script.md")
        print("       python convert_script.py script.json")
        print("       python convert_script.py script.md output.json")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    try:
        result = convert_file(input_file, output_file)
        print(f"Success! Output: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
