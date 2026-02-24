#!/usr/bin/env python3
"""Fast-Clip Script Checker: Validate Shotstack-compatible JSON scripts."""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass


# Regex pattern for placeholder detection
PLACEHOLDER_PATTERN = re.compile(r"\{\{([^}]+)\}\}")

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
VALID_FORMATS = {"mp4", "mov", "webm", "gif"}


@dataclass
class CheckResult:
    """Result of a single check."""

    field: str
    status: str  # "OK", "WARNING", "ERROR"
    message: str
    suggestion: Optional[str] = None


class ScriptChecker:
    """Checker for Fast-Clip JSON scripts."""

    def __init__(self, script_path: Path, verbose: bool = False, quiet: bool = False):
        self.script_path = Path(script_path)
        self.verbose = verbose
        self.quiet = quiet
        self.script_dir = self.script_path.parent
        self.data: Optional[dict] = None
        self.results: List[CheckResult] = []
        self.has_errors = False
        self.has_warnings = False

    def log(self, message: str):
        """Print message if verbose mode is enabled and not quiet."""
        if self.verbose and not self.quiet:
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

    def find_placeholders_in_template(self, obj: Any, path: str = "") -> Dict[str, str]:
        """Recursively scan template for placeholders and return {placeholder: path} mapping."""
        placeholders = {}

        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    matches = PLACEHOLDER_PATTERN.findall(value)
                    for match in matches:
                        placeholder = f"{{{{{match}}}}}"
                        placeholders[placeholder] = f"template.{current_path}"
                elif isinstance(value, (dict, list)):
                    placeholders.update(
                        self.find_placeholders_in_template(value, current_path)
                    )
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                if isinstance(item, str):
                    matches = PLACEHOLDER_PATTERN.findall(item)
                    for match in matches:
                        placeholder = f"{{{{{match}}}}}"
                        placeholders[placeholder] = f"template.{current_path}"
                elif isinstance(item, (dict, list)):
                    placeholders.update(
                        self.find_placeholders_in_template(item, current_path)
                    )

        return placeholders

    def extract_unique_placeholders(self, obj: Any) -> Set[str]:
        """Extract all unique placeholder names from template values."""
        placeholders = set()

        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    matches = PLACEHOLDER_PATTERN.findall(value)
                    placeholders.update(matches)
                elif isinstance(value, (dict, list)):
                    placeholders.update(self.extract_unique_placeholders(value))
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, str):
                    matches = PLACEHOLDER_PATTERN.findall(item)
                    placeholders.update(matches)
                elif isinstance(item, (dict, list)):
                    placeholders.update(self.extract_unique_placeholders(item))

        return placeholders

    def load_script(self) -> bool:
        """Load and parse JSON script."""
        self.log(f"Loading: {self.script_path}")

        if not self.script_path.exists():
            self.add_result(
                "file",
                "ERROR",
                f"File not found: {self.script_path}",
                "Check file path and try again",
            )
            return False

        try:
            with open(self.script_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            self.add_result("file", "OK", "JSON loaded successfully")
            return True
        except json.JSONDecodeError as e:
            self.add_result("file", "ERROR", f"Invalid JSON: {e}")
            return False
        except Exception as e:
            self.add_result("file", "ERROR", f"Failed to read file: {e}")
            return False

    def check_required_fields(self):
        """Check that required fields are present."""
        if self.data is None:
            return

        # Support both flat structure and template-wrapped structure
        required = ["name"]
        for field in required:
            if field not in self.data:
                self.add_result(
                    field,
                    "ERROR",
                    f"Missing required field: '{field}'",
                    f"Add '{field}' to your script",
                )

        # Check for timeline and output (can be flat or in template)
        has_timeline = "timeline" in self.data or (
            "template" in self.data and "timeline" in self.data.get("template", {})
        )
        has_output = "output" in self.data or (
            "template" in self.data and "output" in self.data.get("template", {})
        )

        if not has_timeline:
            self.add_result(
                "timeline",
                "ERROR",
                "Missing required field: 'timeline'",
                "Add 'timeline' to your script or inside 'template'",
            )

        if not has_output:
            self.add_result(
                "output",
                "ERROR",
                "Missing required field: 'output'",
                "Add 'output' to your script or inside 'template'",
            )

    def check_timeline(self):
        """Check timeline structure."""
        if self.data is None:
            return

        # Support both flat structure and template-wrapped structure
        timeline = self.data.get("timeline") or self.data.get("template", {}).get(
            "timeline"
        )
        if not timeline:
            return

        if not isinstance(timeline, dict):
            self.add_result("timeline", "ERROR", "Timeline must be an object")
            return

        tracks = timeline.get("tracks")
        if not tracks or not isinstance(tracks, list):
            self.add_result(
                "timeline.tracks", "ERROR", "Timeline must have tracks array"
            )
            return

        if len(tracks) == 0:
            self.add_result("timeline.tracks", "ERROR", "At least one track required")
            return

        clips = tracks[0].get("clips", [])
        if not clips:
            self.add_result(
                "timeline.clips", "ERROR", "Track must have at least one clip"
            )
            return

        if len(clips) > 10:
            self.add_result(
                "timeline.clips",
                "WARNING",
                f"Many clips ({len(clips)}). Consider fewer for better performance",
            )

        for i, clip in enumerate(clips):
            self.check_clip(clip, i)

    def check_clip(self, clip: dict, index: int):
        """Check a single clip."""
        prefix = f"clip[{index}]"

        # Check asset
        asset = clip.get("asset")
        if not asset:
            self.add_result(f"{prefix}.asset", "ERROR", "Missing asset")
            return

        # Text clips don't require src field
        if asset.get("type") != "text":
            src = asset.get("src")
            if not src:
                self.add_result(f"{prefix}.asset.src", "ERROR", "Missing asset source")

        clip_type = asset.get("type")
        if clip_type not in ("video", "image", "audio", "text"):
            self.add_result(
                f"{prefix}.asset.type",
                "ERROR",
                f"Invalid type: '{clip_type}'",
                "Use 'video', 'image', 'audio', or 'text'",
            )

        # Skip detailed checks for audio and text clips
        if clip_type == "audio":
            # Check audio-specific properties
            if "volume" in asset:
                volume = asset["volume"]
                if not isinstance(volume, (int, float)) or volume < 0 or volume > 2:
                    self.add_result(
                        f"{prefix}.asset.volume",
                        "WARNING",
                        f"Invalid volume: {volume}",
                        "Use 0.0-2.0 range",
                    )
            return

        # Text clips don't have src, they have text field
        if clip_type == "text":
            if "text" not in asset:
                self.add_result(
                    f"{prefix}.asset.text",
                    "ERROR",
                    "Missing text content for text clip",
                )
            return

        # Check transitions
        transition = clip.get("transition")
        if transition:
            trans_in = transition.get("in", "").lower()
            trans_out = transition.get("out", "").lower()

            if trans_in and trans_in not in VALID_TRANSITIONS:
                self.add_result(
                    f"{prefix}.transition.in",
                    "WARNING",
                    f"Unknown transition: '{trans_in}'",
                    f"Valid: {', '.join(sorted(VALID_TRANSITIONS))[:50]}...",
                )

            if trans_out and trans_out not in VALID_TRANSITIONS:
                self.add_result(
                    f"{prefix}.transition.out",
                    "WARNING",
                    f"Unknown transition: '{trans_out}'",
                    f"Valid: {', '.join(sorted(VALID_TRANSITIONS))[:50]}...",
                )

        # Check effect
        effect = clip.get("effect", "").lower()
        if effect and effect not in VALID_EFFECTS:
            self.add_result(
                f"{prefix}.effect",
                "WARNING",
                f"Unknown effect: '{effect}'",
                f"Valid: {', '.join(VALID_EFFECTS)}",
            )

        # Check filter
        filter_name = clip.get("filter", "").lower()
        if filter_name and filter_name not in VALID_FILTERS:
            self.add_result(
                f"{prefix}.filter",
                "WARNING",
                f"Unknown filter: '{filter_name}'",
                f"Valid: {', '.join(VALID_FILTERS)}",
            )

        # Check for overlay (text)
        asset = clip.get("asset", {})
        overlay = asset.get("overlay")
        if overlay:
            overlay_type = overlay.get("type", "")
            if overlay_type != "title":
                self.add_result(
                    f"{prefix}.asset.overlay.type",
                    "WARNING",
                    f"Unsupported overlay type: '{overlay_type}'",
                    "Use 'title' for text overlays",
                )

            text = overlay.get("text", "")
            if not text:
                self.add_result(
                    f"{prefix}.asset.overlay.text",
                    "WARNING",
                    "Overlay text is empty",
                    "Add text content for the overlay",
                )

        # Check length
        length = clip.get("length")
        if length is None:
            self.add_result(f"{prefix}.length", "ERROR", "Missing clip length")
        elif length <= 0:
            self.add_result(f"{prefix}.length", "ERROR", f"Invalid length: {length}")

    def check_output(self):
        """Check output configuration."""
        if self.data is None:
            return

        # Support both flat structure and template-wrapped structure
        output = self.data.get("output") or self.data.get("template", {}).get("output")
        if not output:
            return

        # Check format
        fmt = output.get("format", "").lower()
        if fmt and fmt not in VALID_FORMATS:
            self.add_result(
                "output.format",
                "WARNING",
                f"Unknown format: '{fmt}'",
                f"Valid: {', '.join(VALID_FORMATS)}",
            )

        # Check aspect ratio
        aspect = output.get("aspectRatio", "")
        if aspect and aspect not in VALID_ASPECT_RATIOS:
            self.add_result(
                "output.aspectRatio",
                "WARNING",
                f"Unknown aspect ratio: '{aspect}'",
                f"Valid: {', '.join(VALID_ASPECT_RATIOS)}",
            )

        # Check fps
        fps = output.get("fps")
        if fps and (fps < 1 or fps > 60):
            self.add_result(
                "output.fps",
                "WARNING",
                f"Unusual FPS: {fps}",
                "Typical values: 24, 25, 30, 60",
            )

    def check_resources(self):
        """Check that referenced resources exist."""
        if self.data is None:
            return

        resources_dir = self.data.get("resourcesDir", ".")
        resources_path = self.script_dir / resources_dir

        if not resources_path.exists():
            self.add_result(
                "resourcesDir",
                "ERROR",
                f"Resources directory not found: {resources_dir}",
                "Check directory path",
            )
            return

        # Support both flat structure and template-wrapped structure
        timeline = self.data.get("timeline") or self.data.get("template", {}).get(
            "timeline", {}
        )
        tracks = timeline.get("tracks", [])
        if not tracks:
            return

        # Check all tracks for resources
        for track_idx, track in enumerate(tracks):
            clips = track.get("clips", [])
            for i, clip in enumerate(clips):
                asset = clip.get("asset", {})
                src = asset.get("src", "")
                clip_type = asset.get("type", "")

                # Skip text clips - they don't have src
                if clip_type == "text":
                    continue

                # Extract resource name from template or direct path
                if src.startswith("{{") and src.endswith("}}"):
                    resource = src[2:-2].split("/")[-1]
                elif src.startswith("{") and src.endswith("}"):
                    resource = src[1:-1].split("/")[-1]
                else:
                    resource = src.split("/")[-1]

                if resource:
                    resource_path = resources_path / resource
                    if not resource_path.exists():
                        clip_prefix = f"track{track_idx}.clip[{i}]"
                        if clip_type == "audio":
                            clip_prefix = f"audio.track{track_idx}.clip[{i}]"

                        self.add_result(
                            f"{clip_prefix}.resource",
                            "WARNING",
                            f"Resource not found: {resource}",
                            f"Place {resource} in {resources_dir}/",
                        )

    def check_invalid_placeholder_syntax(self, obj: Any, path: str = ""):
        """Check for invalid placeholder syntax and report warnings."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    self._check_string_for_invalid_placeholders(
                        value, f"template.{current_path}"
                    )
                elif isinstance(value, (dict, list)):
                    self.check_invalid_placeholder_syntax(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                if isinstance(item, str):
                    self._check_string_for_invalid_placeholders(
                        item, f"template.{current_path}"
                    )
                elif isinstance(item, (dict, list)):
                    self.check_invalid_placeholder_syntax(item, current_path)

    def _check_string_for_invalid_placeholders(self, value: str, path: str):
        """Check a string value for invalid placeholder syntax."""
        import re

        # Pattern for valid placeholders (already captured by main regex)
        valid_pattern = r"\{\{([^}]+)\}\}"

        # Pattern for single braces: {field}
        single_brace_pattern = r"(?<!\{)\{([^{}]+)\}(?!\})"

        # Pattern for mismatched opening: {{field} or {{field (no closing)
        mismatched_open_pattern = r"\{\{([^{}]*)\}(?!\})"

        # Pattern for mismatched closing: {field}}
        mismatched_close_pattern = r"(?<!\{)\{([^{}]*)\}\}"

        # Check for single braces (not part of valid {{ }})
        for match in re.finditer(single_brace_pattern, value):
            self.add_result(
                path,
                "WARNING",
                f"Invalid placeholder syntax: '{{{match.group(1)}}}' - use double braces '{{{{{match.group(1)}}}}}'",
                "Valid placeholder format is {{field}}",
            )

        # Check for mismatched braces - opening (with single closing brace)
        for match in re.finditer(mismatched_open_pattern, value):
            inner = match.group(1)
            if inner:
                self.add_result(
                    path,
                    "WARNING",
                    f"Mismatched braces: '{{{{{inner}}}' - missing closing brace",
                    "Use matching braces: {{field}}",
                )

        # Check for cases like {{field without any closing
        if "{{" in value:
            # Remove valid placeholders first
            temp = re.sub(valid_pattern, "", value)
            # Check for remaining {{ patterns
            for match in re.finditer(r"\{\{([^{}]*)$", temp):
                inner = match.group(1)
                self.add_result(
                    path,
                    "WARNING",
                    f"Mismatched braces: '{{{{{inner}' - missing closing braces",
                    "Use matching braces: {{field}}",
                )
            # Check for {{text}} where text contains invalid characters
            for match in re.finditer(r"\{\{([^{}]*)\}\}", temp):
                inner = match.group(1)
                if inner and inner.strip():
                    # This is actually valid, but let's check if it was removed above
                    pass

        # Check for mismatched braces - closing
        for match in re.finditer(mismatched_close_pattern, value):
            inner = match.group(1)
            if inner:
                self.add_result(
                    path,
                    "WARNING",
                    f"Mismatched braces: '{{{inner}}}' - missing opening brace",
                    "Use matching braces: {{field}}",
                )

        # Check for empty placeholders {{}}
        if "{{}}" in value:
            self.add_result(
                path,
                "WARNING",
                "Empty placeholder: '{{}}' - provide a field name",
                "Use format: {{field_name}}",
            )

    def check_template_structure(self):
        """Check that template field structure is valid."""
        if self.data is None:
            return

        template = self.data.get("template")
        if template is None:
            return

        # Validate template is an object (dict)
        if not isinstance(template, dict):
            self.add_result(
                "template",
                "ERROR",
                "Template field must be an object",
                "Use a JSON object for the template field",
            )
            return

        # Check for placeholders in template
        placeholders = self.find_placeholders_in_template(template)
        if placeholders:
            self.log(f"Found {len(placeholders)} placeholder(s) in template")
            for placeholder, path in placeholders.items():
                self.log(f"  {placeholder} at {path}")

        # Check for invalid placeholder syntax
        self.check_invalid_placeholder_syntax(template)

    def check_merge_array(self):
        """Check that merge array is valid and matches placeholders."""
        if self.data is None:
            return

        template = self.data.get("template")
        if template is None or not isinstance(template, dict):
            return

        # Extract placeholders from template
        placeholder_names = self.extract_unique_placeholders(template)

        if not placeholder_names:
            # No placeholders found, no need for merge array
            return

        # Check for merge array
        merge = self.data.get("merge")
        if merge is None:
            self.add_result(
                "merge",
                "ERROR",
                f"Template has {len(placeholder_names)} placeholder(s) but no merge array",
                "Add a 'merge' array to provide replacement values for placeholders",
            )
            return

        if not isinstance(merge, list):
            self.add_result(
                "merge", "ERROR", "Merge field must be an array", "Use a JSON array"
            )
            return

        if len(merge) == 0:
            self.add_result(
                "merge",
                "ERROR",
                f"Merge array is empty but template has {len(placeholder_names)} placeholder(s)",
                "Add merge entries for each placeholder",
            )
            return

        # Validate each merge entry and build set of find values
        merge_find_values = set()
        for i, entry in enumerate(merge):
            if not isinstance(entry, dict):
                self.add_result(
                    f"merge[{i}]",
                    "ERROR",
                    f"Merge entry {i} must be an object",
                    "Each merge entry should be a JSON object",
                )
                continue

            # Check required fields
            if "find" not in entry:
                self.add_result(
                    f"merge[{i}].find",
                    "ERROR",
                    f"Merge entry {i} missing required 'find' field",
                    "Add 'find' field with the placeholder name (without braces)",
                )
            else:
                find_value = entry.get("find")
                merge_find_values.add(find_value)
                if find_value == "":
                    self.add_result(
                        f"merge[{i}].find",
                        "WARNING",
                        f"Merge entry {i} has empty 'find' value",
                        "Provide a placeholder name",
                    )

            if "replace" not in entry:
                self.add_result(
                    f"merge[{i}].replace",
                    "ERROR",
                    f"Merge entry {i} missing required 'replace' field",
                    "Add 'replace' field with the replacement value",
                )

        # Check that all placeholders have corresponding merge entries
        for placeholder_name in placeholder_names:
            if placeholder_name not in merge_find_values:
                # Find where this placeholder is used
                placeholder = f"{{{{{placeholder_name}}}}}"
                paths = self.find_placeholders_in_template(template)
                path = paths.get(placeholder, "unknown location")
                self.add_result(
                    "merge.missing",
                    "ERROR",
                    f"Placeholder '{placeholder_name}' at {path} has no matching merge entry",
                    f"Add a merge entry with find: '{placeholder_name}'",
                )

    def run_checks(self) -> Tuple[bool, List[CheckResult]]:
        """Run all checks and return results."""
        if not self.load_script():
            return False, self.results

        self.check_required_fields()
        self.check_timeline()
        self.check_output()
        self.check_resources()
        self.check_template_structure()
        self.check_merge_array()

        return not self.has_errors, self.results

    def print_report(self):
        """Print formatted check report."""
        # Skip all output if quiet mode is enabled
        if self.quiet:
            return

        print(f"\n{'=' * 60}")
        print(f"Script: {self.script_path}")
        print(f"{'=' * 60}")

        # Group by status
        errors = [r for r in self.results if r.status == "ERROR"]
        warnings = [r for r in self.results if r.status == "WARNING"]
        ok = [r for r in self.results if r.status == "OK"]

        if errors:
            print(f"\n❌ ERRORS ({len(errors)}):")
            for r in errors:
                print(f"  ✗ {r.field}: {r.message}")
                if r.suggestion:
                    print(f"    → {r.suggestion}")

        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for r in warnings:
                print(f"  ! {r.field}: {r.message}")
                if r.suggestion:
                    print(f"    → {r.suggestion}")

        if self.verbose and ok:
            print(f"\n✓ OK ({len(ok)}):")
            for r in ok[:10]:  # Limit OK messages
                print(f"  ✓ {r.field}: {r.message}")
            if len(ok) > 10:
                print(f"  ... and {len(ok) - 10} more")

        print(f"\n{'=' * 60}")
        if self.has_errors:
            print("RESULT: ❌ FAILED (fix errors before proceeding)")
        elif self.has_warnings:
            print("RESULT: ⚠️  PASSED WITH WARNINGS")
        else:
            print("RESULT: ✓ ALL CHECKS PASSED")
        print(f"{'=' * 60}\n")


def check_script(
    script_path: Path, verbose: bool = False, quiet: bool = False
) -> Tuple[bool, List[CheckResult]]:
    """Check a script file."""
    checker = ScriptChecker(script_path, verbose, quiet)
    is_valid, results = checker.run_checks()
    checker.print_report()
    return is_valid, results


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Fast-Clip Script Checker")
        print("")
        print("Usage: python check.py [options] <script.json>")
        print("")
        print("Options:")
        print("  -v, --verbose    Show detailed output")
        print("  -q, --quiet      Suppress all output (exit code only)")
        print("  -h, --help       Show this help")
        print("")
        print("Examples:")
        print("  python check.py script.json")
        print("  python check.py -v script.json")
        print("  python check.py -q script.json")
        sys.exit(0)

    # Parse flags
    verbose = "-v" in args or "--verbose" in args
    quiet = "-q" in args or "--quiet" in args

    # Remove flags from args to get script path
    args = [a for a in args if a not in ("-v", "--verbose", "-q", "--quiet")]

    if not args:
        print("Error: No script file specified")
        sys.exit(1)

    script_path = Path(args[0])

    # Quiet mode overrides verbose
    if quiet:
        verbose = False

    is_valid, _ = check_script(script_path, verbose, quiet)
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
