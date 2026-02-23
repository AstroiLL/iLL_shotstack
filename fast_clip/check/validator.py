"""Validation utilities for Fast-Clip scripts."""

from typing import Dict, List, Optional, Tuple, Any


# Supported values
SUPPORTED_FORMATS = {"mp4", "avi", "mov", "mkv"}
SUPPORTED_RESOLUTIONS = {"2160p", "1440p", "1080p", "720p", "480p"}
SUPPORTED_ORIENTATIONS = {"landscape", "portrait", "square"}
VALID_EFFECTS = {
    "fade_in",
    "fade_out",
    "slide_in",
    "slide_out",
    "cross_fade_in",
    "cross_fade_out",
}
VALID_SLIDE_DIRECTIONS = {"left", "right", "top", "bottom"}


def parse_time(time_str: str) -> float:
    """Parse time string to seconds.

    Supports formats: MM:SS, HH:MM:SS

    Args:
        time_str: Time string like "00:05" or "01:30:00"

    Returns:
        Time in seconds as float

    Raises:
        ValueError: If format is invalid
    """
    parts = time_str.split(":")
    if len(parts) == 2:  # MM:SS
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    elif len(parts) == 3:  # HH:MM:SS
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    else:
        raise ValueError(f"Invalid time format: {time_str}. Use MM:SS or HH:MM:SS")


def validate_timeline_item(
    item: Dict[str, Any], index: int
) -> List[Tuple[str, str, Optional[str]]]:
    """Validate a single timeline item.

    Args:
        item: Timeline item dictionary
        index: Item index for error messages

    Returns:
        List of (status, message, suggestion) tuples
    """
    errors = []

    # Check required fields
    required = ["id", "resource", "time_start", "time_end"]
    for field in required:
        if field not in item:
            errors.append(
                (
                    "ERROR",
                    f"Required field '{field}' is missing",
                    f"Add '{field}' to timeline item[{index}]",
                )
            )

    # Check id
    if "id" in item:
        if not isinstance(item["id"], int):
            errors.append(
                (
                    "ERROR",
                    f"timeline[{index}].id: Expected integer",
                    "Change to an integer",
                )
            )
        elif item["id"] != index + 1:
            errors.append(
                (
                    "WARNING",
                    f"timeline[{index}].id: Expected {index + 1}, got {item['id']}",
                    f"Change id to {index + 1}",
                )
            )

    # Check resource
    if "resource" in item:
        if not isinstance(item["resource"], str):
            errors.append(
                (
                    "ERROR",
                    f"timeline[{index}].resource: Expected string",
                    "Change to a string",
                )
            )
        elif not item["resource"].strip():
            errors.append(
                (
                    "ERROR",
                    f"timeline[{index}].resource: Cannot be empty",
                    "Provide a filename",
                )
            )

    # Check time fields
    for time_field in ["time_start", "time_end"]:
        if time_field in item:
            value = item[time_field]
            if not isinstance(value, str):
                errors.append(
                    (
                        "ERROR",
                        f"timeline[{index}].{time_field}: Expected string",
                        "Use format MM:SS",
                    )
                )
            else:
                try:
                    parse_time(value)
                except ValueError:
                    errors.append(
                        (
                            "ERROR",
                            f"timeline[{index}].{time_field}: Invalid format '{value}'",
                            "Use MM:SS or HH:MM:SS",
                        )
                    )

    # Check time consistency
    if "time_start" in item and "time_end" in item:
        try:
            start = parse_time(item["time_start"])
            end = parse_time(item["time_end"])
            if start >= end:
                errors.append(
                    (
                        "ERROR",
                        f"timeline[{index}]: time_start >= time_end",
                        "Ensure time_start < time_end",
                    )
                )
        except ValueError:
            pass

    # Check effects
    for effect_field, duration_field in [
        ("start_effect", "start_duration"),
        ("end_effect", "end_duration"),
    ]:
        effect = item.get(effect_field)
        duration = item.get(duration_field)

        if effect is not None:
            if effect not in VALID_EFFECTS:
                errors.append(
                    (
                        "WARNING",
                        f"timeline[{index}].{effect_field}: Unknown effect '{effect}'",
                        f"Use: {', '.join(VALID_EFFECTS)}",
                    )
                )

            if duration is None:
                errors.append(
                    (
                        "WARNING",
                        f"timeline[{index}]: {effect_field} without {duration_field}",
                        f"Add {duration_field} or remove {effect_field}",
                    )
                )

        if duration is not None and not isinstance(duration, str):
            errors.append(
                (
                    "ERROR",
                    f"timeline[{index}].{duration_field}: Expected string",
                    "Use format like '3s'",
                )
            )

    # Check slide_direction for slide effects
    slide_direction = item.get("slide_direction")
    if slide_direction is not None:
        if slide_direction not in VALID_SLIDE_DIRECTIONS:
            errors.append(
                (
                    "ERROR",
                    f"timeline[{index}].slide_direction: Invalid direction '{slide_direction}'",
                    f"Use: {', '.join(VALID_SLIDE_DIRECTIONS)}",
                )
            )

    # Validate slide effects require direction
    start_effect = item.get("start_effect")
    end_effect = item.get("end_effect")

    if start_effect == "slide_in" and not slide_direction:
        errors.append(
            (
                "ERROR",
                f"timeline[{index}].start_effect: slide_in requires slide_direction",
                f"Add slide_direction: {', '.join(VALID_SLIDE_DIRECTIONS)}",
            )
        )

    if end_effect == "slide_out" and not slide_direction:
        errors.append(
            (
                "ERROR",
                f"timeline[{index}].end_effect: slide_out requires slide_direction",
                f"Add slide_direction: {', '.join(VALID_SLIDE_DIRECTIONS)}",
            )
        )

    return errors


def validate_script_config(
    data: Dict[str, Any],
) -> List[Tuple[str, str, Optional[str]]]:
    """Validate script configuration.

    Args:
        data: Script configuration dictionary

    Returns:
        List of (status, message, suggestion) tuples
    """
    errors = []

    # Check for template-based structure or legacy structure
    if "template" in data:
        # Template-based structure validation
        template = data.get("template", {})

        # Check required fields in template
        if "timeline" not in template:
            errors.append(
                (
                    "ERROR",
                    "Required field 'template.timeline' is missing",
                    "Add 'timeline' to template",
                )
            )

        # Check for output in template
        if "output" not in template:
            errors.append(
                (
                    "WARNING",
                    "Field 'template.output' is missing",
                    "Add 'output' to template for better control",
                )
            )

        # Check merge array
        if "merge" not in data:
            errors.append(
                (
                    "WARNING",
                    "Field 'merge' is missing",
                    "Add 'merge' array for template substitutions",
                )
            )
    else:
        # Legacy structure validation
        required = ["name", "resources_dir", "timeline", "result_file"]
        for field in required:
            if field not in data:
                errors.append(
                    (
                        "ERROR",
                        f"Required field '{field}' is missing",
                        f"Add '{field}' to script",
                    )
                )

    # Check name
    if "name" in data:
        if not isinstance(data["name"], str):
            errors.append(
                ("ERROR", "Field 'name': Expected string", "Change to a string")
            )
        elif not data["name"].strip():
            errors.append(
                ("ERROR", "Field 'name': Cannot be empty", "Provide a project name")
            )

    # Check resources_dir
    if "resources_dir" in data:
        if not isinstance(data["resources_dir"], str):
            errors.append(
                (
                    "ERROR",
                    "Field 'resources_dir': Expected string",
                    "Change to a string",
                )
            )

    # Check result_file
    if "result_file" in data:
        if not isinstance(data["result_file"], str):
            errors.append(
                ("ERROR", "Field 'result_file': Expected string", "Change to a string")
            )
        elif not data["result_file"].endswith((".mp4", ".avi", ".mov", ".mkv")):
            errors.append(
                (
                    "WARNING",
                    "Field 'result_file': No video extension",
                    "Add .mp4, .avi, .mov, or .mkv",
                )
            )

    # Check timeline
    if "timeline" in data:
        if not isinstance(data["timeline"], list):
            errors.append(
                ("ERROR", "Field 'timeline': Expected array", "Change to an array")
            )
        elif len(data["timeline"]) == 0:
            errors.append(
                ("ERROR", "Field 'timeline': Cannot be empty", "Add at least one item")
            )
        elif len(data["timeline"]) > 10:
            errors.append(
                (
                    "ERROR",
                    f"Field 'timeline': Too many items ({len(data['timeline'])}, max 10)",
                    "Remove some items",
                )
            )
        else:
            # Validate each timeline item
            for i, item in enumerate(data["timeline"]):
                if not isinstance(item, dict):
                    errors.append(
                        (
                            "ERROR",
                            f"timeline[{i}]: Expected object",
                            "Change to an object",
                        )
                    )
                else:
                    item_errors = validate_timeline_item(item, i)
                    errors.extend(item_errors)

    # Check optional fields
    if "output_format" in data and data["output_format"] is not None:
        fmt = data["output_format"].lower()
        if fmt not in SUPPORTED_FORMATS:
            errors.append(
                (
                    "WARNING",
                    f"Field 'output_format': Unsupported format '{fmt}'",
                    f"Use: {', '.join(sorted(SUPPORTED_FORMATS))}",
                )
            )

    if "resolution" in data and data["resolution"] is not None:
        res = data["resolution"].lower()
        if res not in SUPPORTED_RESOLUTIONS:
            errors.append(
                (
                    "WARNING",
                    f"Field 'resolution': Unsupported resolution '{res}'",
                    f"Use: {', '.join(sorted(SUPPORTED_RESOLUTIONS))}",
                )
            )

    if "orientation" in data and data["orientation"] is not None:
        orient = data["orientation"].lower()
        if orient not in SUPPORTED_ORIENTATIONS:
            errors.append(
                (
                    "WARNING",
                    f"Field 'orientation': Unsupported orientation '{orient}'",
                    f"Use: {', '.join(sorted(SUPPORTED_ORIENTATIONS))}",
                )
            )

    return errors
