#!/usr/bin/env python3
"""Test data generator for various validation scenarios."""

import json
from pathlib import Path
from typing import Dict, Any, List


def generate_valid_template() -> Dict[str, Any]:
    """Generate a valid Shotstack template."""
    return {
        "template": {
            "timeline": {
                "tracks": [
                    {
                        "clips": [
                            {
                                "asset": {"type": "video", "src": "{{video.mp4}}"},
                                "start": 0.0,
                                "length": 5.0,
                                "transition": {"in": "fade", "out": "slideLeft"},
                                "effect": "zoomIn",
                            }
                        ]
                    }
                ]
            }
        },
        "output": {"format": "mp4", "aspectRatio": "16:9"},
        "merge": [{"find": "video.mp4", "replace": ""}],
    }


def generate_invalid_json_syntax() -> Dict[str, Any]:
    """Generate data with invalid JSON syntax."""
    return {
        "template": {
            "timeline": {
                "tracks": [
                    {
                        "clips": [
                            {
                                "asset": {"type": "video", "src": "{{video.mp4}}"},
                                "start": float(
                                    "inf"
                                ),  # This will cause JSON serialization issues
                                "length": 5.0,
                            }
                        ]
                    }
                ]
            }
        },
        "output": {"format": "mp4"},
        "merge": [],
    }


def generate_missing_required_fields() -> Dict[str, Any]:
    """Generate template missing required fields."""
    return {
        "template": {
            "timeline": {
                # Missing tracks
            }
        },
        "output": {"format": "mp4"},
        # Missing merge array
    }


def generate_invalid_transitions() -> Dict[str, Any]:
    """Generate template with invalid transitions."""
    return {
        "template": {
            "timeline": {
                "tracks": [
                    {
                        "clips": [
                            {
                                "asset": {"type": "video", "src": "{{video.mp4}}"},
                                "start": 0.0,
                                "length": 5.0,
                                "transition": {
                                    "in": "invalidTransition",
                                    "out": "anotherInvalid",
                                },
                            }
                        ]
                    }
                ]
            }
        },
        "output": {"format": "mp4"},
        "merge": [{"find": "video.mp4", "replace": ""}],
    }


def generate_invalid_effects() -> Dict[str, Any]:
    """Generate template with invalid effects."""
    return {
        "template": {
            "timeline": {
                "tracks": [
                    {
                        "clips": [
                            {
                                "asset": {"type": "video", "src": "{{video.mp4}}"},
                                "start": 0.0,
                                "length": 5.0,
                                "effect": "invalidEffect",
                            }
                        ]
                    }
                ]
            }
        },
        "output": {"format": "mp4"},
        "merge": [{"find": "video.mp4", "replace": ""}],
    }


def generate_invalid_filters() -> Dict[str, Any]:
    """Generate template with invalid filters."""
    return {
        "template": {
            "timeline": {
                "tracks": [
                    {
                        "clips": [
                            {
                                "asset": {"type": "video", "src": "{{video.mp4}}"},
                                "start": 0.0,
                                "length": 5.0,
                                "filter": "invalidFilter",
                            }
                        ]
                    }
                ]
            }
        },
        "output": {"format": "mp4"},
        "merge": [{"find": "video.mp4", "replace": ""}],
    }


def generate_invalid_aspect_ratios() -> Dict[str, Any]:
    """Generate template with invalid aspect ratios."""
    return {
        "template": {
            "timeline": {
                "tracks": [
                    {
                        "clips": [
                            {
                                "asset": {"type": "video", "src": "{{video.mp4}}"},
                                "start": 0.0,
                                "length": 5.0,
                            }
                        ]
                    }
                ]
            }
        },
        "output": {
            "format": "mp4",
            "aspectRatio": "16:10",  # Invalid aspect ratio
        },
        "merge": [{"find": "video.mp4", "replace": ""}],
    }


def generate_malformed_placeholders() -> Dict[str, Any]:
    """Generate template with malformed placeholder syntax."""
    return {
        "template": {
            "timeline": {
                "tracks": [
                    {
                        "clips": [
                            {
                                "asset": {
                                    "type": "video",
                                    "src": "{video.mp4}",  # Single braces
                                },
                                "start": 0.0,
                                "length": 5.0,
                            }
                        ]
                    }
                ]
            }
        },
        "output": {"format": "mp4"},
        "merge": [{"find": "video.mp4", "replace": ""}],
    }


def generate_missing_merge_entries() -> Dict[str, Any]:
    """Generate template with placeholders but missing merge entries."""
    return {
        "template": {
            "timeline": {
                "tracks": [
                    {
                        "clips": [
                            {
                                "asset": {"type": "video", "src": "{{video.mp4}}"},
                                "start": 0.0,
                                "length": 5.0,
                            }
                        ]
                    }
                ]
            }
        },
        "output": {"format": "mp4"},
        "merge": [
            {"find": "other_file.mp4", "replace": ""}  # Missing video.mp4 entry
        ],
    }


def generate_empty_merge_array() -> Dict[str, Any]:
    """Generate template with placeholders but empty merge array."""
    return {
        "template": {
            "timeline": {
                "tracks": [
                    {
                        "clips": [
                            {
                                "asset": {"type": "video", "src": "{{video.mp4}}"},
                                "start": 0.0,
                                "length": 5.0,
                            }
                        ]
                    }
                ]
            }
        },
        "output": {"format": "mp4"},
        "merge": [],  # Empty but has placeholders
    }


def generate_complex_template() -> Dict[str, Any]:
    """Generate a complex template with multiple tracks and clips."""
    return {
        "template": {
            "timeline": {
                "tracks": [
                    {
                        "clips": [
                            {
                                "asset": {"type": "video", "src": "{{intro.mp4}}"},
                                "start": 0.0,
                                "length": 3.0,
                                "transition": {"in": "fadeFast"},
                            },
                            {
                                "asset": {"type": "image", "src": "{{title.png}}"},
                                "start": 3.0,
                                "length": 2.0,
                                "filter": "contrast",
                            },
                        ]
                    },
                    {
                        "clips": [
                            {
                                "asset": {"type": "video", "src": "{{main_video.mp4}}"},
                                "start": 5.0,
                                "length": 10.0,
                                "effect": "kenBurns",
                            }
                        ]
                    },
                    {
                        "clips": [
                            {
                                "asset": {
                                    "type": "audio",
                                    "src": "{{background_music.mp3}}",
                                },
                                "start": 0.0,
                                "length": 15.0,
                            }
                        ]
                    },
                ]
            }
        },
        "output": {"format": "mp4", "aspectRatio": "16:9", "fps": 30.0},
        "merge": [
            {"find": "intro.mp4", "replace": ""},
            {"find": "title.png", "replace": ""},
            {"find": "main_video.mp4", "replace": ""},
            {"find": "background_music.mp3", "replace": ""},
        ],
    }


def save_test_data(output_dir: Path):
    """Save all test data to files."""
    test_cases = {
        "valid_template.json": generate_valid_template(),
        "invalid_json_syntax.json": generate_invalid_json_syntax(),
        "missing_required_fields.json": generate_missing_required_fields(),
        "invalid_transitions.json": generate_invalid_transitions(),
        "invalid_effects.json": generate_invalid_effects(),
        "invalid_filters.json": generate_invalid_filters(),
        "invalid_aspect_ratios.json": generate_invalid_aspect_ratios(),
        "malformed_placeholders.json": generate_malformed_placeholders(),
        "missing_merge_entries.json": generate_missing_merge_entries(),
        "empty_merge_array.json": generate_empty_merge_array(),
        "complex_template.json": generate_complex_template(),
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    for filename, data in test_cases.items():
        file_path = output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Created test file: {file_path}")

    return output_dir


if __name__ == "__main__":
    # Generate test data in tests/data directory
    output_dir = Path(__file__).parent / "data"
    save_test_data(output_dir)
    print(f"\nTest data saved to: {output_dir}")
    print("Use these files to test validation functionality.")
