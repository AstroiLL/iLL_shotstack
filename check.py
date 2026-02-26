#!/usr/bin/env python3
"""Fast-Clip Script Checker: Validate Shotstack-compatible JSON scripts."""

import json
import sys
from pathlib import Path
from typing import Tuple, Optional

from fast_clip.check.validation import (
    JsonValidator,
    FileChecker,
    FieldValidator,
    ValidationResult,
    ValidationReport,
    ValidationLevel,
)


# Legacy support - keep the old interface
class ScriptChecker:
    """Legacy ScriptChecker for backward compatibility."""

    def __init__(self, script_path: Path, verbose: bool = False, quiet: bool = False):
        self.script_path = Path(script_path)
        self.verbose = verbose
        self.quiet = quiet
        self.script_dir = self.script_path.parent

        # Initialize new validators
        self.json_validator = JsonValidator(strict_mode=False)
        self.file_checker = FileChecker(strict_mode=False, script_path=script_path)
        self.field_validator = FieldValidator(strict_mode=False)

        # Legacy compatibility
        self.results = []
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
        # Convert legacy format to new ValidationResult
        level = (
            ValidationLevel.ERROR
            if status == "ERROR"
            else (
                ValidationLevel.WARNING if status == "WARNING" else ValidationLevel.INFO
            )
        )

        validation_result = ValidationResult(
            status=status,
            message=message,
            suggestion=suggestion,
            level=level,
            field=field,
        )

        self.results.append(validation_result)
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

    def run_checks(self) -> Tuple[bool, list]:
        """Run all checks using new validation framework."""
        if not self.load_script():
            return False, self.results

        # Run comprehensive validation using new modules
        json_report = self.json_validator.validate(self.data)
        file_report = self.file_checker.validate(self.data)
        field_report = self.field_validator.validate(self.data)

        # Convert all validation results to legacy format
        all_results = []
        for report in [json_report, file_report, field_report]:
            for result in report.results:
                # Convert ValidationResult to legacy CheckResult format
                status = (
                    "ERROR"
                    if result.level == ValidationLevel.ERROR
                    else (
                        "WARNING" if result.level == ValidationLevel.WARNING else "OK"
                    )
                )

                legacy_result = {
                    "field": result.field or "unknown",
                    "status": status,
                    "message": result.message,
                    "suggestion": result.suggestion,
                }
                all_results.append(legacy_result)

                # Update legacy flags
                if status == "ERROR":
                    self.has_errors = True
                elif status == "WARNING":
                    self.has_warnings = True

        self.results = all_results
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
        errors = [r for r in self.results if r["status"] == "ERROR"]
        warnings = [r for r in self.results if r["status"] == "WARNING"]
        ok = [r for r in self.results if r["status"] == "OK"]

        if errors:
            print(f"\n❌ ERRORS ({len(errors)}):")
            for r in errors:
                print(f"  ✗ {r['field']}: {r['message']}")
                if r.get("suggestion"):
                    print(f"    → {r['suggestion']}")

        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for r in warnings:
                print(f"  ! {r['field']}: {r['message']}")
                if r.get("suggestion"):
                    print(f"    → {r['suggestion']}")

        if self.verbose and ok:
            print(f"\n✓ OK ({len(ok)}):")
            for r in ok[:10]:  # Limit OK messages
                print(f"  ✓ {r['field']}: {r['message']}")
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
    script_path: Path,
    verbose: bool = False,
    quiet: bool = False,
    skip_validate: bool = False,
    strict_mode: bool = False,
) -> Tuple[bool, list]:
    """Check a script file using new validation framework."""
    if skip_validate:
        # Skip validation mode - just check JSON syntax
        checker = ScriptChecker(script_path, verbose, quiet)
        if checker.load_script():
            checker.add_result("validation", "OK", "Validation skipped by user request")
            return True, checker.results
        else:
            return False, checker.results

    # Initialize validators with appropriate settings
    json_validator = JsonValidator(strict_mode=strict_mode)
    file_checker = FileChecker(strict_mode=strict_mode, script_path=script_path)
    field_validator = FieldValidator(strict_mode=strict_mode)

    # Load JSON
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return False, [
            {
                "field": "file",
                "status": "ERROR",
                "message": f"File not found: {script_path}",
                "suggestion": "Check file path and try again",
            }
        ]
    except json.JSONDecodeError as e:
        return False, [
            {
                "field": "file",
                "status": "ERROR",
                "message": f"Invalid JSON: {e}",
                "suggestion": "Fix JSON syntax errors",
            }
        ]

    # Run validation
    json_report = json_validator.validate(data)
    file_report = file_checker.validate(data)
    field_report = field_validator.validate(data)

    # Combine results
    all_results = []
    for report in [json_report, file_report, field_report]:
        for result in report.results:
            status = (
                "ERROR"
                if result.level == ValidationLevel.ERROR
                else ("WARNING" if result.level == ValidationLevel.WARNING else "OK")
            )

            all_results.append(
                {
                    "field": result.field or "unknown",
                    "status": status,
                    "message": result.message,
                    "suggestion": result.suggestion,
                }
            )

    # Report results
    if not quiet:
        print(f"\n{'=' * 60}")
        print(f"Script: {script_path}")
        print(f"{'=' * 60}")

        errors = [r for r in all_results if r["status"] == "ERROR"]
        warnings = [r for r in all_results if r["status"] == "WARNING"]

        if errors:
            print(f"\n❌ ERRORS ({len(errors)}):")
            for r in errors:
                print(f"  ✗ {r['field']}: {r['message']}")
                if r.get("suggestion"):
                    print(f"    → {r['suggestion']}")

        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for r in warnings:
                print(f"  ! {r['field']}: {r['message']}")
                if r.get("suggestion"):
                    print(f"    → {r['suggestion']}")

        print(f"\n{'=' * 60}")
        if errors:
            print("RESULT: ❌ FAILED (fix errors before proceeding)")
        elif warnings:
            print("RESULT: ⚠️  PASSED WITH WARNINGS")
        else:
            print("RESULT: ✓ ALL CHECKS PASSED")
        print(f"{'=' * 60}\n")

    errors = [r for r in all_results if r["status"] == "ERROR"]
    return len(errors) == 0, all_results


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
        print("  --skip-validate  Skip comprehensive validation (JSON syntax only)")
        print("  --strict         Enable strict validation mode")
        print("  -h, --help       Show this help")
        print("")
        print("Examples:")
        print("  python check.py script.json")
        print("  python check.py -v script.json")
        print("  python check.py --strict script.json")
        print("  python check.py --skip-validate script.json")
        sys.exit(0)

    # Parse flags
    verbose = "-v" in args or "--verbose" in args
    quiet = "-q" in args or "--quiet" in args
    skip_validate = "--skip-validate" in args
    strict_mode = "--strict" in args

    # Remove flags from args to get script path
    args = [
        a
        for a in args
        if a not in ("-v", "--verbose", "-q", "--quiet", "--skip-validate", "--strict")
    ]

    if not args:
        print("Error: No script file specified")
        sys.exit(1)

    script_path = Path(args[0])

    # Quiet mode overrides verbose
    if quiet:
        verbose = False

    is_valid, _ = check_script(script_path, verbose, quiet, skip_validate, strict_mode)
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
