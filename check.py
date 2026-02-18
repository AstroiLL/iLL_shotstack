#!/usr/bin/env python3
"""Fast-Clip Script Checker: Validate Shotstack-compatible JSON scripts."""

import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass


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

        required = ["name", "timeline", "output"]
        for field in required:
            if field not in self.data:
                self.add_result(
                    field,
                    "ERROR",
                    f"Missing required field: '{field}'",
                    f"Add '{field}' to your script",
                )

    def check_timeline(self):
        """Check timeline structure."""
        if self.data is None:
            return

        timeline = self.data.get("timeline")
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

        src = asset.get("src")
        if not src:
            self.add_result(f"{prefix}.asset.src", "ERROR", "Missing asset source")

        clip_type = asset.get("type")
        if clip_type not in ("video", "image"):
            self.add_result(
                f"{prefix}.asset.type",
                "ERROR",
                f"Invalid type: '{clip_type}'",
                "Use 'video' or 'image'",
            )

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

        output = self.data.get("output")
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

        timeline = self.data.get("timeline", {})
        tracks = timeline.get("tracks", [])
        if not tracks:
            return

        clips = tracks[0].get("clips", [])
        for i, clip in enumerate(clips):
            asset = clip.get("asset", {})
            src = asset.get("src", "")

            # Extract resource name from template
            if src.startswith("{{") and src.endswith("}}"):
                resource = src[2:-2].split("/")[-1]
            else:
                resource = src.split("/")[-1]

            if resource:
                resource_path = resources_path / resource
                if not resource_path.exists():
                    self.add_result(
                        f"clip[{i}].resource",
                        "WARNING",
                        f"Resource not found: {resource}",
                        f"Place {resource} in {resources_dir}/",
                    )

    def run_checks(self) -> Tuple[bool, List[CheckResult]]:
        """Run all checks and return results."""
        if not self.load_script():
            return False, self.results

        self.check_required_fields()
        self.check_timeline()
        self.check_output()
        self.check_resources()

        return not self.has_errors, self.results

    def print_report(self):
        """Print formatted check report."""
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
    script_path: Path, verbose: bool = False
) -> Tuple[bool, List[CheckResult]]:
    """Check a script file."""
    checker = ScriptChecker(script_path, verbose)
    is_valid, results = checker.run_checks()
    checker.print_report()
    return is_valid, results


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Fast-Clip Script Checker")
        print("")
        print("Usage: python check.py <script.json> [options]")
        print("")
        print("Options:")
        print("  -v, --verbose    Show detailed output")
        print("  -h, --help       Show this help")
        print("")
        print("Examples:")
        print("  python check.py script.json")
        print("  python check.py script.json -v")
        sys.exit(0)

    script_path = Path(args[0])
    verbose = "-v" in args or "--verbose" in args

    is_valid, _ = check_script(script_path, verbose)
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
