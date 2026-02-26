#!/usr/bin/env python3
"""Unit tests for validation modules."""

import pytest
from pathlib import Path
from typing import Dict, Any

from fast_clip.check.validation import (
    JsonValidator,
    FileChecker,
    FieldValidator,
    ValidationLevel,
    ValidationReport,
)


class TestJsonValidator:
    """Test cases for JsonValidator."""

    def test_valid_template_structure(self):
        """Test validation of valid template structure."""
        validator = JsonValidator()

        valid_data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {"type": "video", "src": "test.mp4"},
                                    "start": 0.0,
                                    "length": 5.0,
                                }
                            ]
                        }
                    ]
                }
            },
            "output": {"format": "mp4"},
            "merge": [{"find": "test.mp4", "replace": ""}],
        }

        report = validator.validate(valid_data)
        assert report.is_valid
        assert report.total_errors == 0

    def test_missing_required_fields(self):
        """Test detection of missing required fields."""
        validator = JsonValidator()

        invalid_data = {
            "template": {"timeline": {"tracks": []}},
            "output": {"format": "mp4"},
            # Missing merge array
        }

        report = validator.validate(invalid_data)
        assert not report.is_valid
        assert report.total_errors > 0

        # Check for specific errors
        error_messages = [
            r.message for r in report.results if r.level == ValidationLevel.ERROR
        ]
        assert any("merge array cannot be empty" in msg for msg in error_messages)

    def test_invalid_json_syntax(self):
        """Test handling of invalid JSON syntax."""
        validator = JsonValidator()

        # Test with data that would cause JSON serialization issues
        invalid_data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {
                                        "type": "video",
                                        "src": float("inf"),
                                    },  # Invalid for JSON
                                    "start": 0.0,
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

        report = validator.validate(invalid_data)
        assert not report.is_valid

        # Should catch JSON serialization error
        error_messages = [
            r.message for r in report.results if r.level == ValidationLevel.ERROR
        ]
        assert len(error_messages) > 0

    def test_placeholder_validation(self):
        """Test placeholder syntax validation."""
        validator = JsonValidator()

        # Valid placeholders
        valid_data = {
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
            "merge": [{"find": "video.mp4", "replace": ""}],
        }

        report = validator.validate(valid_data)
        assert report.is_valid

        # Invalid placeholder syntax
        invalid_data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {
                                        "type": "video",
                                        "src": "{video.mp4}",
                                    },  # Single braces
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

        report = validator.validate(invalid_data)
        # Should have warnings for invalid placeholder syntax
        warning_messages = [
            r.message for r in report.results if r.level == ValidationLevel.WARNING
        ]
        assert any("placeholder" in msg.lower() for msg in warning_messages)


class TestFileChecker:
    """Test cases for FileChecker."""

    def test_existing_files_validation(self):
        """Test validation of existing files."""
        # Create a temporary file for testing
        test_file = Path("/tmp/test_video.mp4")
        test_file.write_text("dummy content")

        try:
            checker = FileChecker(script_path=Path("/tmp"))

            data = {
                "template": {
                    "timeline": {
                        "tracks": [
                            {
                                "clips": [
                                    {
                                        "asset": {
                                            "type": "video",
                                            "src": "test_video.mp4",
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
                "merge": [{"find": "test_video.mp4", "replace": str(test_file)}],
            }

            report = checker.validate(data)
            assert report.is_valid

        finally:
            # Clean up
            if test_file.exists():
                test_file.unlink()

    def test_missing_files_validation(self):
        """Test validation of missing files."""
        checker = FileChecker(script_path=Path("/tmp"))

        data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {
                                        "type": "video",
                                        "src": "nonexistent.mp4",
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
            "merge": [{"find": "nonexistent.mp4", "replace": ""}],
        }

        report = checker.validate(data)
        # Should have warnings for missing files
        assert report.total_warnings > 0

        warning_messages = [
            r.message for r in report.results if r.level == ValidationLevel.WARNING
        ]
        assert any("not found" in msg for msg in warning_messages)

    def test_file_caching(self):
        """Test file checking caching functionality."""
        checker = FileChecker(script_path=Path("/tmp"))

        # Create a temporary file
        test_file = Path("/tmp/cache_test.mp4")
        test_file.write_text("dummy content")

        try:
            data = {
                "template": {
                    "timeline": {
                        "tracks": [
                            {
                                "clips": [
                                    {
                                        "asset": {
                                            "type": "video",
                                            "src": "cache_test.mp4",
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
                "merge": [{"find": "cache_test.mp4", "replace": str(test_file)}],
            }

            # First validation should check file
            report1 = checker.validate(data)
            assert report1.total_warnings == 0

            # Second validation should use cache
            report2 = checker.validate(data)
            assert report2.total_warnings == 0

        finally:
            if test_file.exists():
                test_file.unlink()


class TestFieldValidator:
    """Test cases for FieldValidator."""

    def test_valid_transitions(self):
        """Test validation of valid transition values."""
        validator = FieldValidator()

        data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {"type": "video", "src": "test.mp4"},
                                    "start": 0.0,
                                    "length": 5.0,
                                    "transition": {"in": "fade", "out": "slideLeft"},
                                }
                            ]
                        }
                    ]
                }
            },
            "output": {"format": "mp4"},
            "merge": [],
        }

        report = validator.validate(data)
        assert report.is_valid

    def test_invalid_transitions(self):
        """Test validation of invalid transition values."""
        validator = FieldValidator()

        data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {"type": "video", "src": "test.mp4"},
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
            "merge": [],
        }

        report = validator.validate(data)
        # Should have warnings for invalid transitions
        assert report.total_warnings > 0

        warning_messages = [
            r.message for r in report.results if r.level == ValidationLevel.WARNING
        ]
        assert any("transition" in msg.lower() for msg in warning_messages)

    def test_valid_effects(self):
        """Test validation of valid effect values."""
        validator = FieldValidator()

        data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {"type": "video", "src": "test.mp4"},
                                    "start": 0.0,
                                    "length": 5.0,
                                    "effect": "zoomIn",
                                }
                            ]
                        }
                    ]
                }
            },
            "output": {"format": "mp4"},
            "merge": [],
        }

        report = validator.validate(data)
        assert report.is_valid

    def test_invalid_effects(self):
        """Test validation of invalid effect values."""
        validator = FieldValidator()

        data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {"type": "video", "src": "test.mp4"},
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
            "merge": [],
        }

        report = validator.validate(data)
        # Should have warnings for invalid effects
        assert report.total_warnings > 0

        warning_messages = [
            r.message for r in report.results if r.level == ValidationLevel.WARNING
        ]
        assert any("effect" in msg.lower() for msg in warning_messages)

    def test_valid_aspect_ratios(self):
        """Test validation of valid aspect ratio values."""
        validator = FieldValidator()

        for ratio in ["9:16", "16:9", "1:1", "4:5", "4:3"]:
            data = {
                "template": {"timeline": {"tracks": []}},
                "output": {"aspectRatio": ratio},
                "merge": [],
            }

            report = validator.validate_aspect_ratio(ratio)
            error_count = len(
                [r for r in report.results if r.level == ValidationLevel.ERROR]
            )
            warning_count = len(
                [r for r in report.results if r.level == ValidationLevel.WARNING]
            )
            assert error_count == 0
            assert warning_count == 0

    def test_invalid_aspect_ratios(self):
        """Test validation of invalid aspect ratio values."""
        validator = FieldValidator()

        data = {
            "template": {"timeline": {"tracks": []}},
            "output": {"aspectRatio": "16:10"},  # Invalid aspect ratio
            "merge": [],
        }

        report = validator.validate_aspect_ratio("16:10")
        # Should have warnings for invalid aspect ratio
        assert report.total_warnings > 0

        warning_messages = [
            r.message for r in report.results if r.level == ValidationLevel.WARNING
        ]
        assert any("aspect ratio" in msg.lower() for msg in warning_messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
