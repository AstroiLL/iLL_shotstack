"""
Base validation classes and data structures.
"""

from enum import Enum
from typing import List, Optional, Any, Dict
from dataclasses import dataclass


class ValidationLevel(Enum):
    """Validation error levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    status: str  # OK, ERROR, WARNING
    message: str
    suggestion: Optional[str] = None
    level: ValidationLevel = ValidationLevel.ERROR
    field: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ValidationReport:
    """Complete validation report for a template."""

    is_valid: bool
    results: List[ValidationResult]
    total_errors: int
    total_warnings: int

    @classmethod
    def from_results(cls, results: List[ValidationResult]) -> "ValidationReport":
        """Create report from validation results."""
        errors = [r for r in results if r.level == ValidationLevel.ERROR]
        warnings = [r for r in results if r.level == ValidationLevel.WARNING]

        is_valid = len(errors) == 0

        return cls(
            is_valid=is_valid,
            results=results,
            total_errors=len(errors),
            total_warnings=len(warnings),
        )


class BaseValidator:
    """Base class for all validators."""

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self._file_cache: Dict[str, bool] = {}

    def validate(self, data: Any):
        """Validate the given data."""
        raise NotImplementedError("Subclasses must implement validate method")

    def _create_result(
        self,
        status: str,
        message: str,
        suggestion: Optional[str] = None,
        level: ValidationLevel = ValidationLevel.ERROR,
        field: Optional[str] = None,
        line_number: Optional[int] = None,
    ) -> ValidationResult:
        """Create a validation result."""
        return ValidationResult(
            status=status,
            message=message,
            suggestion=suggestion,
            level=level,
            field=field,
            line_number=line_number,
        )
