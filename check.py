#!/usr/bin/env python3
"""Fast-Clip Script Checker: Validate JSON scripts before processing."""

import json
import sys
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


# Constants from main.py
SUPPORTED_FORMATS = {"mp4", "avi", "mov", "mkv"}
RESOLUTIONS = {"2160p", "1440p", "1080p", "720p", "480p"}
ORIENTATIONS = {"landscape", "portrait", "square"}
VALID_EFFECTS = {"fade_in", "fade_out"}


@dataclass
class CheckResult:
    """Result of a single check."""

    field: str
    status: str  # "OK", "WARNING", "ERROR"
    message: str
    suggestion: Optional[str] = None


class ScriptChecker:
    """Checker for Fast-Clip JSON scripts."""

    def __init__(self, script_path: Path, verbose: bool = False):
        self.script_path = Path(script_path)
        self.verbose = verbose
        self.script_dir = self.script_path.parent
        self.data: Optional[dict] = None
        self.results: List[CheckResult] = []
        self.has_errors = False
        self.has_warnings = False

    def log(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(message)

    def add_result(
        self, field: str, status: str, message: str, suggestion: Optional[str] = None
    ):
        """Add check result and update error/warning flags."""
        self.results.append(CheckResult(field, status, message, suggestion))
        if status == "ERROR":
            self.has_errors = True
        elif status == "WARNING":
            self.has_warnings = True

        if self.verbose:
            icon = "✓" if status == "OK" else ("⚠" if status == "WARNING" else "✗")
            print(f"  {icon} {field}: {message}")
            if suggestion:
                print(f"    → {suggestion}")

    def check_file_exists(self) -> bool:
        """Check if script file exists."""
        if not self.script_path.exists():
            self.add_result(
                "File",
                "ERROR",
                f"Script file not found: {self.script_path}",
                "Check the file path and try again",
            )
            return False

        self.add_result("File", "OK", f"Found: {self.script_path}")
        return True

    def check_json_valid(self) -> bool:
        """Check if file is valid JSON."""
        try:
            with open(self.script_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            self.add_result("JSON", "OK", "Valid JSON format")
            return True
        except json.JSONDecodeError as e:
            self.add_result(
                "JSON", "ERROR", f"Invalid JSON: {e}", "Fix JSON syntax errors"
            )
            return False
        except Exception as e:
            self.add_result(
                "JSON",
                "ERROR",
                f"Cannot read file: {e}",
                "Check file permissions and encoding",
            )
            return False

    def check_required_fields(self):
        """Check presence of required fields."""
        required = ["name", "resources_dir", "timeline", "result_file"]

        for field in required:
            if field not in self.data:
                self.add_result(
                    f"Field '{field}'",
                    "ERROR",
                    f"Required field '{field}' is missing",
                    f"Add '{field}' to your script",
                )
            else:
                self.add_result(f"Field '{field}'", "OK", "Present")

    def check_field_types(self):
        """Check types of fields."""
        # Check name
        if "name" in self.data:
            if not isinstance(self.data["name"], str):
                self.add_result(
                    "Field 'name'",
                    "ERROR",
                    f"Expected string, got {type(self.data['name']).__name__}",
                    "Change to a string value",
                )
            elif not self.data["name"].strip():
                self.add_result(
                    "Field 'name'",
                    "ERROR",
                    "Cannot be empty string",
                    "Provide a non-empty project name",
                )
            else:
                self.add_result("Field 'name'", "OK", f"Value: '{self.data['name']}'")

        # Check resources_dir
        if "resources_dir" in self.data:
            if not isinstance(self.data["resources_dir"], str):
                self.add_result(
                    "Field 'resources_dir'",
                    "ERROR",
                    f"Expected string, got {type(self.data['resources_dir']).__name__}",
                    "Change to a string value",
                )
            else:
                self.add_result(
                    "Field 'resources_dir'",
                    "OK",
                    f"Value: '{self.data['resources_dir']}'",
                )

        # Check result_file
        if "result_file" in self.data:
            if not isinstance(self.data["result_file"], str):
                self.add_result(
                    "Field 'result_file'",
                    "ERROR",
                    f"Expected string, got {type(self.data['result_file']).__name__}",
                    "Change to a string value",
                )
            elif not self.data["result_file"].endswith(
                (".mp4", ".avi", ".mov", ".mkv")
            ):
                self.add_result(
                    "Field 'result_file'",
                    "WARNING",
                    f"No valid video extension: {self.data['result_file']}",
                    "Add .mp4, .avi, .mov, or .mkv extension",
                )
            else:
                self.add_result(
                    "Field 'result_file'", "OK", f"Value: '{self.data['result_file']}'"
                )

        # Check timeline
        if "timeline" in self.data:
            if not isinstance(self.data["timeline"], list):
                self.add_result(
                    "Field 'timeline'",
                    "ERROR",
                    f"Expected array, got {type(self.data['timeline']).__name__}",
                    "Change to an array of timeline items",
                )
            elif len(self.data["timeline"]) == 0:
                self.add_result(
                    "Field 'timeline'",
                    "ERROR",
                    "Timeline cannot be empty",
                    "Add at least one timeline item",
                )
            elif len(self.data["timeline"]) > 10:
                self.add_result(
                    "Field 'timeline'",
                    "ERROR",
                    f"Too many clips: {len(self.data['timeline'])} (max 10)",
                    "Remove some clips or split into multiple projects",
                )
            else:
                self.add_result(
                    "Field 'timeline'", "OK", f"{len(self.data['timeline'])} item(s)"
                )

    def check_optional_fields(self):
        """Check optional fields if present."""
        # Check output_format
        if "output_format" in self.data:
            fmt = self.data["output_format"]
            if fmt is None:
                self.add_result(
                    "Field 'output_format'", "OK", "Not specified (will use source)"
                )
            elif not isinstance(fmt, str):
                self.add_result(
                    "Field 'output_format'",
                    "ERROR",
                    f"Expected string, got {type(fmt).__name__}",
                    "Change to a string value or remove",
                )
            elif fmt.lower() not in SUPPORTED_FORMATS:
                self.add_result(
                    "Field 'output_format'",
                    "WARNING",
                    f"Unsupported format: '{fmt}'",
                    f"Use one of: {', '.join(sorted(SUPPORTED_FORMATS))}",
                )
            else:
                self.add_result("Field 'output_format'", "OK", f"Value: '{fmt}'")

        # Check resolution
        if "resolution" in self.data:
            res = self.data["resolution"]
            if res is None:
                self.add_result(
                    "Field 'resolution'", "OK", "Not specified (will use source)"
                )
            elif not isinstance(res, str):
                self.add_result(
                    "Field 'resolution'",
                    "ERROR",
                    f"Expected string, got {type(res).__name__}",
                    "Change to a string value or remove",
                )
            elif res.lower() not in RESOLUTIONS:
                self.add_result(
                    "Field 'resolution'",
                    "WARNING",
                    f"Unsupported resolution: '{res}'",
                    f"Use one of: {', '.join(sorted(RESOLUTIONS))}",
                )
            else:
                self.add_result("Field 'resolution'", "OK", f"Value: '{res}'")

        # Check orientation
        if "orientation" in self.data:
            orient = self.data["orientation"]
            if orient is None:
                self.add_result(
                    "Field 'orientation'",
                    "OK",
                    "Not specified (will detect from first clip)",
                )
            elif not isinstance(orient, str):
                self.add_result(
                    "Field 'orientation'",
                    "ERROR",
                    f"Expected string, got {type(orient).__name__}",
                    "Change to a string value or remove",
                )
            elif orient.lower() not in ORIENTATIONS:
                self.add_result(
                    "Field 'orientation'",
                    "WARNING",
                    f"Unsupported orientation: '{orient}'",
                    f"Use one of: {', '.join(sorted(ORIENTATIONS))}",
                )
            else:
                self.add_result("Field 'orientation'", "OK", f"Value: '{orient}'")

    def check_resources_directory(self):
        """Check if resources directory exists."""
        if "resources_dir" not in self.data:
            return

        resources_dir = self.script_dir / self.data["resources_dir"]
        if not resources_dir.exists():
            self.add_result(
                "Resources Directory",
                "ERROR",
                f"Directory not found: {resources_dir}",
                f"Create directory '{self.data['resources_dir']}' or update 'resources_dir' field",
            )
        elif not resources_dir.is_dir():
            self.add_result(
                "Resources Directory",
                "ERROR",
                f"Not a directory: {resources_dir}",
                "Update 'resources_dir' to point to a valid directory",
            )
        else:
            self.add_result("Resources Directory", "OK", f"Found: {resources_dir}")

    def check_timeline_items(self):
        """Check each timeline item."""
        if "timeline" not in self.data or not isinstance(self.data["timeline"], list):
            return

        resources_dir = None
        if "resources_dir" in self.data:
            resources_dir = self.script_dir / self.data["resources_dir"]

        for i, item in enumerate(self.data["timeline"]):
            prefix = f"Timeline[{i}]"

            # Check if item is a dict
            if not isinstance(item, dict):
                self.add_result(
                    prefix,
                    "ERROR",
                    f"Expected object, got {type(item).__name__}",
                    "Change to an object with timeline item fields",
                )
                continue

            # Check required fields in item
            item_required = ["id", "resource", "time_start", "time_end"]
            for field in item_required:
                if field not in item:
                    self.add_result(
                        f"{prefix}.{field}",
                        "ERROR",
                        f"Required field '{field}' is missing",
                        f"Add '{field}' to timeline item",
                    )

            # Check id
            if "id" in item:
                if not isinstance(item["id"], int):
                    self.add_result(
                        f"{prefix}.id",
                        "ERROR",
                        f"Expected integer, got {type(item['id']).__name__}",
                        "Change to an integer",
                    )
                elif item["id"] != i + 1:
                    self.add_result(
                        f"{prefix}.id",
                        "WARNING",
                        f"ID is {item['id']}, expected {i + 1} (sequential)",
                        f"Change id to {i + 1} for consistency",
                    )
                else:
                    self.add_result(f"{prefix}.id", "OK", f"Value: {item['id']}")

            # Check resource file
            if "resource" in item:
                resource = item["resource"]
                if not isinstance(resource, str):
                    self.add_result(
                        f"{prefix}.resource",
                        "ERROR",
                        f"Expected string, got {type(resource).__name__}",
                        "Change to a string filename",
                    )
                elif resources_dir and resources_dir.exists():
                    resource_path = resources_dir / resource
                    if not resource_path.exists():
                        self.add_result(
                            f"{prefix}.resource",
                            "ERROR",
                            f"File not found: {resource}",
                            f"Add file to '{self.data['resources_dir']}' or update filename",
                        )
                    else:
                        self.add_result(
                            f"{prefix}.resource", "OK", f"Found: {resource}"
                        )
                else:
                    self.add_result(
                        f"{prefix}.resource",
                        "OK",
                        f"Value: '{resource}' (cannot verify - directory not found)",
                    )

            # Check time fields
            self._check_time_field(prefix, item, "time_start")
            self._check_time_field(prefix, item, "time_end")

            # Check time consistency
            if "time_start" in item and "time_end" in item:
                try:
                    start = self._parse_time(item["time_start"])
                    end = self._parse_time(item["time_end"])
                    if start >= end:
                        self.add_result(
                            f"{prefix}.time",
                            "ERROR",
                            f"time_start ({item['time_start']}) >= time_end ({item['time_end']})",
                            "Ensure time_start is less than time_end",
                        )
                    else:
                        duration = end - start
                        self.add_result(
                            f"{prefix}.time", "OK", f"Duration: {duration}s"
                        )
                except:
                    pass  # Already reported parsing errors

            # Check effects
            self._check_effect(prefix, item, "start_effect", "start_duration")
            self._check_effect(prefix, item, "end_effect", "end_duration")

    def _parse_time(self, time_str: str) -> float:
        """Parse time string to seconds."""
        parts = time_str.split(":")
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            raise ValueError(f"Invalid time format: {time_str}")

    def _check_time_field(self, prefix: str, item: dict, field: str):
        """Check a time field."""
        if field not in item:
            return

        value = item[field]
        if not isinstance(value, str):
            self.add_result(
                f"{prefix}.{field}",
                "ERROR",
                f"Expected string, got {type(value).__name__}",
                "Use format MM:SS or HH:MM:SS",
            )
            return

        try:
            self._parse_time(value)
            self.add_result(f"{prefix}.{field}", "OK", f"Value: '{value}'")
        except ValueError:
            self.add_result(
                f"{prefix}.{field}",
                "ERROR",
                f"Invalid time format: '{value}'",
                "Use format MM:SS or HH:MM:SS (e.g., '00:05' or '01:30:00')",
            )

    def _check_effect(
        self, prefix: str, item: dict, effect_field: str, duration_field: str
    ):
        """Check effect and its duration."""
        effect = item.get(effect_field)
        duration = item.get(duration_field)

        if effect is None and duration is None:
            return  # No effect specified

        if effect is not None and effect not in VALID_EFFECTS:
            self.add_result(
                f"{prefix}.{effect_field}",
                "WARNING",
                f"Unknown effect: '{effect}'",
                f"Use one of: {', '.join(sorted(VALID_EFFECTS))}",
            )
        elif effect is not None:
            self.add_result(f"{prefix}.{effect_field}", "OK", f"Value: '{effect}'")

        if duration is not None:
            if not isinstance(duration, str):
                self.add_result(
                    f"{prefix}.{duration_field}",
                    "ERROR",
                    f"Expected string, got {type(duration).__name__}",
                    "Use format like '3s'",
                )
            elif not duration.endswith("s"):
                self.add_result(
                    f"{prefix}.{duration_field}",
                    "WARNING",
                    f"Duration should end with 's': '{duration}'",
                    "Change to format like '3s'",
                )
            else:
                try:
                    float(duration[:-1])
                    self.add_result(
                        f"{prefix}.{duration_field}", "OK", f"Value: '{duration}'"
                    )
                except ValueError:
                    self.add_result(
                        f"{prefix}.{duration_field}",
                        "ERROR",
                        f"Invalid duration: '{duration}'",
                        "Use format like '3s' (number followed by 's')",
                    )

        # Check if effect has duration
        if effect is not None and duration is None:
            self.add_result(
                f"{prefix}.{effect_field}",
                "WARNING",
                f"Effect '{effect}' specified without {duration_field}",
                f"Add {duration_field} (e.g., '3s') or remove {effect_field}",
            )

    def check_all(self) -> bool:
        """Run all checks. Return True if no errors."""
        if self.verbose:
            print(f"\nChecking script: {self.script_path}\n")
            print("=" * 60)

        # Basic checks
        if not self.check_file_exists():
            return False

        if not self.check_json_valid():
            return False

        if self.verbose:
            print("\n" + "-" * 60)
            print("Checking structure...")
            print("-" * 60)

        # Structure checks
        self.check_required_fields()
        self.check_field_types()
        self.check_optional_fields()

        if self.verbose:
            print("\n" + "-" * 60)
            print("Checking resources...")
            print("-" * 60)

        # Resource checks
        self.check_resources_directory()
        self.check_timeline_items()

        # Summary
        if self.verbose:
            print("\n" + "=" * 60)
            print("SUMMARY")
            print("=" * 60)

            errors = sum(1 for r in self.results if r.status == "ERROR")
            warnings = sum(1 for r in self.results if r.status == "WARNING")
            ok = sum(1 for r in self.results if r.status == "OK")

            print(f"  ✓ Passed: {ok}")
            print(f"  ⚠ Warnings: {warnings}")
            print(f"  ✗ Errors: {errors}")

            if errors > 0:
                print(f"\n  Result: FAILED - Fix {errors} error(s) before processing")
                return False
            elif warnings > 0:
                print(f"\n  Result: PASSED with {warnings} warning(s)")
                return True
            else:
                print("\n  Result: PASSED - Ready to process!")
                return True

        return not self.has_errors


def main():
    """Main entry point."""
    verbose = False
    script_path = None

    # Parse arguments
    for arg in sys.argv[1:]:
        if arg == "-v" or arg == "--verbose":
            verbose = True
        elif arg.startswith("-"):
            print(f"Unknown option: {arg}")
            print("Usage: python check.py [-v] <script.json>")
            sys.exit(2)
        else:
            script_path = arg

    if not script_path:
        print("Usage: python check.py [-v] <script.json>")
        print("")
        print("Options:")
        print("  -v, --verbose    Show detailed check results")
        print("")
        print("Examples:")
        print("  python check.py script.json          # Silent mode")
        print("  python check.py -v script.json       # Verbose mode")
        sys.exit(2)

    checker = ScriptChecker(script_path, verbose)
    is_valid = checker.check_all()

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
