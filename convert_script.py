#!/usr/bin/env python3
"""Fast-Clip Script Converter: Convert MD to native Shotstack JSON format."""

import json
import re
import sys
from pathlib import Path
from typing import Optional


# Valid Shotstack values
VALID_TRANSITIONS = {
    "fade",
    "fadefast",
    "fadeslow",
    "slideleft",
    "slideright",
    "slideup",
    "slidedown",
    "slideleftfast",
    "sliderightfast",
    "slideupfast",
    "slidedownfast",
    "wipeleft",
    "wiperight",
    "wipeleftfast",
    "wiperightfast",
    "carouselleft",
    "carouselright",
    "carouselupfast",
    "shuffletopright",
    "shuffleleftbottom",
    "reveal",
    "revealfast",
    "revealslow",
    "zoom",
    "zoomfast",
    "zoomslow",
}
VALID_EFFECTS = {"zoomin", "zoomout", "kenburns"}
VALID_FILTERS = {
    "boost",
    "greyscale",
    "contrast",
    "muted",
    "negative",
    "darken",
    "lighten",
}
VALID_ASPECT_RATIOS = {"9:16", "16:9", "1:1", "4:5", "4:3"}


def parse_duration(duration_str: str) -> float:
    """Parse duration string to seconds."""
    duration_str = duration_str.strip().lower()
    if duration_str.endswith("s"):
        return float(duration_str[:-1])
    elif duration_str.endswith("ms"):
        return float(duration_str[:-2]) / 1000
    return float(duration_str)


def parse_time(time_str: str) -> float:
    """Parse time string to seconds."""
    time_str = time_str.strip()
    parts = time_str.split(":")
    if len(parts) == 2:  # MM:SS
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    elif len(parts) == 3:  # HH:MM:SS
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    else:
        raise ValueError(f"Invalid time format: {time_str}. Use MM:SS or HH:MM:SS")


def md_to_shotstack(md_path: Path) -> dict:
    """Convert markdown script to native Shotstack JSON."""
    content = md_path.read_text(encoding="utf-8")

    # Parse headers
    name_match = re.search(r"##\s*name:\s*(.+)", content)
    resources_match = re.search(r"##\s*resources_dir:\s*(.+)", content)
    soundtrack_match = re.search(r"##\s*soundtrack:\s*(.+)", content)
    soundtrack_vol_match = re.search(r"##\s*soundtrack_volume:\s*(.+)", content)
    background_match = re.search(r"##\s*background:\s*(.+)", content)
    output_format_match = re.search(r"##\s*output_format:\s*(.+)", content)
    resolution_match = re.search(r"##\s*resolution:\s*(.+)", content)
    aspect_match = re.search(r"##\s*aspect_ratio:\s*(.+)", content)
    fps_match = re.search(r"##\s*fps:\s*(.+)", content)
    thumbnail_match = re.search(r"##\s*thumbnail_capture:\s*(.+)", content)

    if name_match is None or resources_match is None:
        raise ValueError("Missing required headers: name, resources_dir")

    name = name_match.group(1).strip()
    resources_dir = resources_match.group(1).strip()

    # Parse soundtrack
    soundtrack: Optional[dict] = None
    if soundtrack_match:
        soundtrack = {
            "src": f"{{{resources_dir}/{soundtrack_match.group(1).strip()}}}",
            "effect": "fadeIn",
        }
        if soundtrack_vol_match:
            soundtrack["volume"] = float(soundtrack_vol_match.group(1).strip())

    # Parse table
    clips = []
    lines = content.split("\n")
    in_table = False

    for line in lines:
        line = line.strip()
        if line.startswith("| # "):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|") and not line.startswith("|---"):
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            if len(cells) >= 9:
                try:
                    clip = build_clip(cells, resources_dir)
                    clips.append(clip)
                except (ValueError, IndexError) as e:
                    print(f"Warning: Skipping invalid row: {line} ({e})")
                    continue

    # Build timeline
    timeline: dict = {"tracks": [{"clips": clips}]}
    if soundtrack:
        timeline["soundtrack"] = soundtrack
    if background_match:
        timeline["background"] = background_match.group(1).strip()

    # Build output
    output = {
        "format": output_format_match.group(1).strip() if output_format_match else "mp4"
    }
    if resolution_match:
        output["resolution"] = resolution_match.group(1).strip()
    if aspect_match:
        aspect = aspect_match.group(1).strip()
        if aspect in VALID_ASPECT_RATIOS:
            output["aspectRatio"] = aspect
    if fps_match:
        output["fps"] = int(fps_match.group(1).strip())
    if thumbnail_match:
        output["thumbnail"] = {"capture": int(thumbnail_match.group(1).strip())}

    return {
        "name": name,
        "resourcesDir": resources_dir,
        "timeline": timeline,
        "output": output,
    }


def build_clip(cells: list, resources_dir: str) -> dict:
    """Build a Shotstack clip from table cells."""
    # cells: [#, Resource, Trim, Duration, Trans In, Effect, Filter, Trans Out, Volume, Description]
    resource = cells[1]
    trim_str = cells[2]
    duration_str = cells[3]
    trans_in = cells[4].lower() if cells[4] else None
    effect = cells[5].lower() if cells[5] else None
    filter_name = cells[6].lower() if cells[6] else None
    trans_out = cells[7].lower() if cells[7] else None
    volume_str = cells[8] if len(cells) > 8 else "1.0"

    clip: dict = {
        "asset": {
            "type": "video"
            if resource.endswith((".mp4", ".avi", ".mov", ".mkv"))
            else "image",
            "src": f"{{{resources_dir}/{resource}}}",
        },
        "start": "auto",
        "length": parse_duration(duration_str),
    }

    # Add trim for video
    if resource.endswith((".mp4", ".avi", ".mov", ".mkv")) and trim_str:
        clip["asset"]["trim"] = parse_time(trim_str)

    # Add volume
    if volume_str:
        clip["asset"]["volume"] = float(volume_str)

    # Add transitions
    transition = {}
    if trans_in and trans_in in VALID_TRANSITIONS:
        transition["in"] = trans_in
    if trans_out and trans_out in VALID_TRANSITIONS:
        transition["out"] = trans_out
    if transition:
        clip["transition"] = transition

    # Add effect
    if effect and effect in VALID_EFFECTS:
        clip["effect"] = effect

    # Add filter
    if filter_name and filter_name in VALID_FILTERS:
        clip["filter"] = filter_name

    return clip


def convert_file(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """Convert MD file to Shotstack JSON."""
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix != ".md":
        raise ValueError(f"Only .md files supported. Got: {input_path.suffix}")

    # MD to Shotstack JSON
    shotstack_data = md_to_shotstack(input_path)

    if output_path is None:
        output_path = input_path.with_suffix(".json")

    output_path.write_text(
        json.dumps(shotstack_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Converted: {input_path} -> {output_path}")
    print(f"Name: {shotstack_data['name']}")
    print(f"Resources: {shotstack_data['resourcesDir']}")
    print(f"Clips: {len(shotstack_data['timeline']['tracks'][0]['clips'])}")

    return output_path


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python convert_script.py <input.md> [output.json]")
        print("       python convert_script.py script.md")
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
