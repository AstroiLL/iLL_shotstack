"""Script checker implementation."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from .validator import (
    validate_script_config,
)


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
        self.data: Optional[Dict[str, Any]] = None
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

    def check_resources_exist(self):
        """Check if resources directory and files exist."""
        if not self.data or "resources_dir" not in self.data:
            return

        resources_dir = self.script_dir / self.data["resources_dir"]
        if not resources_dir.exists():
            self.add_result(
                "Resources Directory",
                "ERROR",
                f"Directory not found: {resources_dir}",
                f"Create directory '{self.data['resources_dir']}' or update 'resources_dir' field",
            )
            return
        elif not resources_dir.is_dir():
            self.add_result(
                "Resources Directory",
                "ERROR",
                f"Not a directory: {resources_dir}",
                "Update 'resources_dir' to point to a valid directory",
            )
            return
        else:
            self.add_result("Resources Directory", "OK", f"Found: {resources_dir}")

        # Check individual video files
        if "timeline" in self.data and isinstance(self.data["timeline"], list):
            for i, item in enumerate(self.data["timeline"]):
                if isinstance(item, dict) and "resource" in item:
                    resource = item["resource"]
                    resource_path = resources_dir / resource
                    if not resource_path.exists():
                        self.add_result(
                            f"Timeline[{i}].resource",
                            "ERROR",
                            f"Video file not found: {resource}",
                            f"Add file to '{self.data['resources_dir']}' or update filename",
                        )
                    elif not resource_path.is_file():
                        self.add_result(
                            f"Timeline[{i}].resource",
                            "ERROR",
                            f"Not a file: {resource}",
                            "Update resource to point to a valid file",
                        )
                    else:
                        self.add_result(
                            f"Timeline[{i}].resource", "OK", f"Found: {resource}"
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

        # Validate script configuration
        validation_errors = validate_script_config(self.data)
        for status, message, suggestion in validation_errors:
            # Extract field name from message
            if ":" in message:
                field = message.split(":")[0]
            else:
                field = "Script"
            self.add_result(
                field,
                status,
                message.split(":", 1)[-1].strip() if ":" in message else message,
                suggestion,
            )

        if self.verbose:
            print("\n" + "-" * 60)
            print("Checking resources...")
            print("-" * 60)

        # Check resources
        self.check_resources_exist()

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


def check_script(
    script_path: Path, verbose: bool = False
) -> Tuple[bool, List[CheckResult]]:
    """Quick check function.

    Args:
        script_path: Path to JSON script
        verbose: Whether to print detailed output

    Returns:
        Tuple of (is_valid, results)
    """
    checker = ScriptChecker(script_path, verbose)
    is_valid = checker.check_all()
    return is_valid, checker.results
