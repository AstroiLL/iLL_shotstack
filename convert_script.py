#!/usr/bin/env python3
"""Fast-Clip Script Converter: Convert MD to native Shotstack JSON format."""

import json
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List


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


def parse_new_table(content: str, resources_dir: str) -> tuple[List[dict], List[dict]]:
    """Parse new table format with text, descriptions, and sound effects."""
    clips = []
    sound_effects = []
    lines = content.split("\n")
    in_table = False
    start_time = 0.0

    for line in lines:
        line = line.strip()
        if "| #" in line and ("Text" in line or "Description" in line):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|") and not line.startswith("|---"):
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            if len(cells) >= 8:
                try:
                    # cells: [#, Text, Description, Clip, Timing, Duration, Effect, Music effect, Sound effect]
                    text = cells[1]
                    description = cells[2]
                    clip_file = cells[3]
                    timing_str = cells[4]
                    duration_str = cells[5]
                    effect = cells[6].lower() if cells[6] else None
                    sound_effect = (
                        cells[8].lower() if cells[8] else None
                    )  # New: add sound effects
                    sound_effect = (
                        cells[8].lower() if len(cells) > 8 and cells[8] else None
                    )

                    # Build main video clip with text overlay
                    clip = build_clip_with_text(
                        clip_file,
                        timing_str,
                        duration_str,
                        effect or "",
                        text,
                        description,
                        resources_dir,
                        start_time,
                        sound_effects,
                    )
                    clips.append(clip)

                    # Build sound effect clip if specified
                    if sound_effect and sound_effect != "":
                        sound_clip = build_sound_effect_clip(
                            sound_effect,
                            timing_str,
                            duration_str,
                            resources_dir,
                            start_time,
                        )
                        sound_effects.append(sound_clip)

                    # Update start time for next clip
                    duration = parse_duration(duration_str)
                    start_time += duration

                except (ValueError, IndexError) as e:
                    print(f"Warning: Skipping invalid row: {line} ({e})")
                    continue

    return clips, sound_effects


def build_output_config(
    output_format_match, resolution_match, aspect_match, fps_match, thumbnail_match
) -> Dict[str, Any]:
    """Build output configuration with optimized settings for Reels."""
    output = {
        "format": output_format_match.group(1).strip()
        if output_format_match
        else "mp4",
        "resolution": "hd",  # Default to HD for better quality
    }

    if resolution_match:
        resolution = resolution_match.group(1).strip()
        # Map common resolutions to Shotstack format
        if resolution in ["480p", "sd"]:
            output["resolution"] = "sd"
        elif resolution in ["720p", "hd"]:
            output["resolution"] = "hd"
        elif resolution in ["1080p", "fhd"]:
            output["resolution"] = "fhd"
        else:
            output["resolution"] = resolution

    if aspect_match:
        aspect = aspect_match.group(1).strip()
        if aspect in VALID_ASPECT_RATIOS:
            output["aspectRatio"] = aspect
        # Default to 9:16 for Reels
        elif aspect == "9:16":
            output["aspectRatio"] = "9:16"
        else:
            output["aspectRatio"] = "9:16"  # Reels default

    if fps_match:
        output["fps"] = int(fps_match.group(1).strip())
    else:
        output["fps"] = 30  # Default for Reels

    if thumbnail_match:
        output["thumbnail"] = {"capture": int(thumbnail_match.group(1).strip())}

    return output


def build_clip_with_text(
    clip_file: str,
    timing_str: str,
    duration_str: str,
    effect: str,
    text: str,
    description: str,
    resources_dir: str,
    start_time: float,
    sound_effects: Optional[list] = None,
) -> Dict[str, Any]:
    """Build video clip with text overlay for new format."""
    duration = parse_duration(duration_str)

    # Determine media type
    media_type = (
        "video" if clip_file.endswith((".mp4", ".avi", ".mov", ".mkv")) else "image"
    )

    # In script_content.md, clip_file contains just filename (no path)
    # Always add resources_dir for Shotstack format
    src = f"{{{{{resources_dir}/{clip_file}}}}}"

    clip: Dict[str, Any] = {
        "asset": {
            "type": media_type,
            "src": src,
        },
        "start": start_time,
        "length": duration,
        "fit": "cover",  # Best for Reels
    }

    # Add trim for video files
    if media_type == "video" and timing_str:
        try:
            trim_start = parse_timing_start(timing_str)
            if trim_start is not None:
                clip["asset"]["trim"] = trim_start
        except ValueError:
            pass  # Skip trim if timing format is invalid

    # Add transitions and effects (optimized for Reels per 2-Stage.md)
    transition = {}

    if effect and effect.lower():
        if effect.lower() in ["fadein", "fade"]:
            transition["in"] = "fadeFast"
        elif effect.lower() in ["fadeout"]:
            transition["out"] = "fadeFast"
        elif effect.lower() == "zoomin":
            transition["in"] = "zoom"
            clip["effect"] = "zoomIn"
        elif effect.lower() == "zoomout":
            transition["out"] = "zoom"
            clip["effect"] = "zoomOut"
        elif effect.lower() in ["fade"]:
            transition["in"] = "fadeFast"

    if transition:
        clip["transition"] = transition

    # Add text overlay if text is provided
    if text and text.strip():
        clip["asset"]["overlay"] = {
            "type": "title",
            "text": text.strip(),
            "style": "minimal",
            "position": "bottom",
            "size": "small",
        }

    return clip


def build_sound_effect_clip(
    sound_effect: str,
    timing_str: str,
    duration_str: str,
    resources_dir: str,
    start_time: float,
) -> Dict[str, Any]:
    """Build sound effect clip."""
    duration = parse_duration(duration_str)

    # In script_content.md, sound_effect contains just filename (no path)
    # Always add resources_dir for Shotstack format
    src = f"{{{{{resources_dir}/{sound_effect}}}}}"

    return {
        "asset": {
            "type": "audio",
            "src": src,
            "volume": 0.7,  # Default volume for sound effects
        },
        "start": start_time,
        "length": duration,
    }


def parse_timing_start(timing_str: str) -> Optional[float]:
    """Parse start time from timing string like '0:00:000-0:01:800'."""
    if "-" in timing_str:
        start_part = timing_str.split("-")[0]
        return parse_time(start_part)
    return None


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

    # Parse table with new format: Text, Description, Clip, Timing, Duration, Effect, Music effect, Sound effect
    clips, sound_effects = parse_new_table(content, resources_dir)

    # Build timeline with multiple tracks
    tracks = []

    # Main video track
    if clips:
        tracks.append({"clips": clips})

    # Sound effects track
    if sound_effects:
        tracks.append({"clips": sound_effects})

    timeline: dict = {"tracks": tracks}
    if soundtrack:
        timeline["soundtrack"] = soundtrack
    if background_match:
        timeline["background"] = background_match.group(1).strip()

    # Build output with optimized settings for Reels
    output = build_output_config(
        output_format_match, resolution_match, aspect_match, fps_match, thumbnail_match
    )

    # Generate merge fields for all assets - simple approach
    merge_fields = []

    # Add video clips to merge
    for clip in clips:
        src = clip["asset"]["src"]
        if src.startswith("{{") and src.endswith("}}"):
            # Extract template variable from {{Content/filename}}
            template_var = src[2:-2]  # Remove {{}}
            merge_fields.append({"find": template_var, "replace": ""})

    # Add sound effects to merge
    for audio in sound_effects:
        src = audio["asset"]["src"]
        if src.startswith("{{") and src.endswith("}}"):
            template_var = src[2:-2]
            merge_fields.append({"find": template_var, "replace": ""})

    return {
        "name": name,
        "resourcesDir": resources_dir,  # Add resourcesDir to main level
        "template": {
            "timeline": timeline,
            "output": output,
        },
        "merge": merge_fields,
    }


def build_clip(cells: List[str], resources_dir: str) -> dict:
    """Build a Shotstack clip from old format table cells."""
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

    # Generate output path with index if file exists
    if output_path is None:
        output_path = input_path.with_suffix(".json")

    # If output file exists, create new with index
    counter = 1
    original_output_path = output_path
    while output_path.exists():
        stem = original_output_path.stem
        suffix = original_output_path.suffix
        parent = original_output_path.parent
        output_path = parent / f"{stem}_{counter}{suffix}"
        counter += 1

    output_path.write_text(
        json.dumps(shotstack_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Converted: {input_path} -> {output_path}")
    print(f"Name: {shotstack_data.get('name', 'Unknown')}")
    print(f"Resources: {shotstack_data.get('resourcesDir', 'Unknown')}")

    # Count video clips (not audio)
    video_clips_count = 0
    timeline = shotstack_data.get("timeline", {})
    tracks = timeline.get("tracks", [])
    for track in tracks:
        clips = track.get("clips", [])
        for clip in clips:
            asset = clip.get("asset", {})
            if asset.get("type") != "audio":
                video_clips_count += 1
                break

    print(f"Clips: {video_clips_count}")

    return output_path


def json_to_md(json_path: Path) -> Path:
    """Convert Shotstack JSON back to markdown format."""
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    if json_path.suffix != ".json":
        raise ValueError(f"Only .json files supported. Got: {json_path.suffix}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract headers
    name = data.get("name", "Untitled")
    resources_dir = data.get("resourcesDir", ".")

    # Extract timeline data (handle both old format and template format)
    if "template" in data:
        timeline = data.get("template", {}).get("timeline", {})
    else:
        timeline = data.get("timeline", {})
    soundtrack = timeline.get("soundtrack", {})
    background = timeline.get("background", "#000000")

    # Extract output settings
    output = data.get("output", {})
    output_format = output.get("format", "mp4")
    resolution = output.get("resolution", "hd")
    aspect_ratio = output.get("aspectRatio", "9:16")
    fps = output.get("fps", 30)
    thumbnail = output.get("thumbnail", {}).get("capture", 1)

    # Build markdown content
    lines = [
        f"## name: {name}",
        f"## resources_dir: {resources_dir}",
    ]

    # Add soundtrack if present
    if soundtrack:
        src = soundtrack.get("src", "")
        if src.startswith("{{") and src.endswith("}}"):
            # Extract filename from {{resources_dir/filename}}
            filename = src[2:-2].split("/", 1)[1] if "/" in src[2:-2] else src[2:-2]
            lines.append(f"## soundtrack: {filename}")

        volume = soundtrack.get("volume")
        if volume is not None:
            lines.append(f"## soundtrack_volume: {volume}")

    lines.append(f"## background: {background}")
    lines.append("")

    # Build table header
    lines.extend(
        [
            "| # |             Text            |    Description     |     Clip     |     Timing      |Duration|Effect |Music effect|   Sound effect   |",
            "|---|-----------------------------|--------------------|--------------|-----------------|--------|-------|------------|------------------|",
        ]
    )

    # Extract clips from tracks
    tracks = timeline.get("tracks", [])
    video_clips = []
    audio_clips = []

    for track in tracks:
        clips = track.get("clips", [])
        for clip in clips:
            asset = clip.get("asset", {})
            # Default to video type if type not specified
            asset_type = asset.get("type", "video")
            if asset_type == "audio":
                audio_clips.append(clip)
            else:
                video_clips.append(clip)

    # Match video clips with sound effects based on timing
    row_num = 1
    for i, clip in enumerate(video_clips):
        asset = clip.get("asset", {})
        if asset.get("type") != "audio":  # Only process video clips
            src = asset.get("src", "")

        # Extract clip info
        src = asset.get("src", "")
        if src.startswith("{{") and src.endswith("}}"):
            video_filename = (
                src[2:-2].split("/", 1)[1] if "/" in src[2:-2] else src[2:-2]
            )
        elif src.startswith("{") and src.endswith("}"):
            video_filename = (
                src[1:-1].split("/", 1)[1] if "/" in src[1:-1] else src[1:-1]
            )
        else:
            video_filename = src

        # Extract text overlay
        overlay = asset.get("overlay", {})
        text = overlay.get("text", "") if overlay else ""

        # Generate description from filename or overlay
        description = overlay.get("text", "") if overlay else video_filename

        # Calculate timing
        start = clip.get("start", 0)
        length = clip.get("length", 0)

        # Format timing as MM:SS:mmm-MM:SS:mmm
        start_str = format_time_with_ms(start)
        end_str = format_time_with_ms(start + length)
        timing = f"{start_str}-{end_str}"

        # Format duration
        duration = format_duration(length)

        # Extract effects
        transition = clip.get("transition", {})
        effect = ""
        if transition.get("in") == "fadeFast" or transition.get("in") == "fade":
            effect = "FadeIn"
        elif transition.get("out") == "fadeFast" or transition.get("out") == "fade":
            effect = "FadeOut"
        elif clip.get("effect") == "zoomIn":
            effect = "ZoomIn"
        elif clip.get("effect") == "zoomOut":
            effect = "ZoomOut"

        # Find matching sound effect
        sound_effect = ""
        if audio_clips and len(audio_clips) > 0:
            # Try to match by exact timing first
            for audio_clip in audio_clips:
                audio_start = audio_clip.get("start", 0)
                if abs(start - audio_start) < 0.1:
                    audio_src = audio_clip.get("asset", {}).get("src", "")
                    if audio_src.startswith("{{") and audio_src.endswith("}}"):
                        filename = (
                            audio_src[2:-2].split("/", 1)[1]
                            if "/" in audio_src[2:-2]
                            else audio_src[2:-2]
                        )
                    elif audio_src.startswith("{") and audio_src.endswith("}"):
                        filename = (
                            audio_src[1:-1].split("/", 1)[1]
                            if "/" in audio_src[1:-1]
                            else audio_src[1:-1]
                        )
                    else:
                        filename = ""

                    # Check if filename matches what we expect from MD table
                    expected_filenames = [
                        "clic.wav",
                        "whoosh.wav",
                        "camera-shutter.wav",
                    ]
                    if filename in expected_filenames:
                        sound_effect = filename
                        break

        # Build table row with proper spacing to match header
        text_field = f"{text:<29}"
        desc_field = f"{description:<20}"
        clip_field = f"{video_filename:<14}"
        timing_field = f"{timing:<17}"
        dur_field = f"{duration:<8}"
        effect_field = f"{effect:<7}"
        music_field = f"{'':12}"
        sound_field = f"{sound_effect:<17}"

        row = f"| {row_num} |{text_field}|{desc_field}|{clip_field}|{timing_field}|{dur_field}|{effect_field}|{music_field}|{sound_field}|"
        lines.append(row)
        row_num += 1

    lines.extend(
        [
            "",
            f"## output_format: {output_format}",
            f"## resolution: {resolution}",
            f"## aspect_ratio: {aspect_ratio}",
            f"## fps: {fps}",
            f"## thumbnail_capture: {thumbnail}",
        ]
    )

    # Write markdown file with indexing if file exists
    output_path = json_path.with_suffix(".md")
    counter = 1
    original_output_path = output_path
    while output_path.exists():
        stem = original_output_path.stem
        suffix = original_output_path.suffix
        parent = original_output_path.parent
        output_path = parent / f"{stem}_{counter}{suffix}"
        counter += 1

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Converted: {json_path} -> {output_path}")
    return output_path


def format_time_with_ms(seconds: float) -> str:
    """Format time as MM:SS:mmm."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{minutes:02d}:{secs:02d}:{ms:03d}"


def format_duration(seconds: float) -> str:
    """Format duration as X.Xs."""
    return f"{seconds:.1f}s"


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python convert_script.py <input> [output]")
        print("       python convert_script.py script.md")
        print("       python convert_script.py script.json")
        print("       python convert_script.py script.md output.json")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    try:
        # Auto-detect format based on file extension
        if input_file.suffix == ".md":
            # Convert MD to JSON
            result = convert_file(input_file, output_file)
            print(f"Success! Output: {result}")
        elif input_file.suffix == ".json":
            # Convert JSON to MD
            result = json_to_md(input_file)
            print(f"Success! Output: {result}")
        else:
            print(f"Error: Unsupported file format '{input_file.suffix}'")
            print("Supported formats: .md, .json")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
