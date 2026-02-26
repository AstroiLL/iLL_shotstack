"""
Field validator for Shotstack SDK compliance.
"""

import re
from typing import Dict, Any, List, Set, Optional
from pydantic import ValidationError

from .base import BaseValidator, ValidationResult, ValidationLevel, ValidationReport
from .constants import (
    VALID_TRANSITIONS,
    VALID_EFFECTS,
    VALID_FILTERS,
    VALID_ASPECT_RATIOS,
    VALIDATION_MESSAGES,
)


class FieldValidator(BaseValidator):
    """Validator for Shotstack SDK field compliance."""

    def __init__(self, strict_mode: bool = False):
        super().__init__(strict_mode)

    def validate(self, data: Dict[str, Any]) -> ValidationReport:
        """Validate all fields in the template."""
        results = []

        if "template" in data:
            template = data["template"]
            results.extend(self._validate_template_fields(template))

        return ValidationReport.from_results(results)

    def _validate_template_fields(
        self, template: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate fields in template."""
        results = []

        if "timeline" in template:
            timeline = template["timeline"]
            if "tracks" in timeline:
                for i, track in enumerate(timeline["tracks"]):
                    if "clips" in track:
                        for j, clip in enumerate(track["clips"]):
                            results.extend(self._validate_clip_fields(clip, i, j))

        return results

    def _validate_clip_fields(
        self, clip: Dict[str, Any], track_index: int, clip_index: int
    ) -> List[ValidationResult]:
        """Validate fields in a clip."""
        results = []
        field_prefix = f"template.timeline.tracks[{track_index}].clips[{clip_index}]"

        # Validate transition fields
        if "transition" in clip:
            results.extend(
                self._validate_transition_fields(
                    clip["transition"], f"{field_prefix}.transition"
                )
            )

        # Validate effect field
        if "effect" in clip:
            results.extend(
                self._validate_effect_field(clip["effect"], f"{field_prefix}.effect")
            )

        # Validate filter field
        if "filter" in clip:
            results.extend(
                self._validate_filter_field(clip["filter"], f"{field_prefix}.filter")
            )

        return results

    def _validate_transition_fields(
        self, transition: Any, field_path: str
    ) -> List[ValidationResult]:
        """Validate transition fields."""
        results = []

        if not isinstance(transition, dict):
            results.append(
                self._create_result(
                    status="ERROR",
                    message=f"Transition must be a dictionary",
                    level=ValidationLevel.ERROR,
                    field=field_path,
                )
            )
            return results

        # Check 'in' transition
        if "in" in transition and transition["in"]:
            result = self._check_transition_value(transition["in"], f"{field_path}.in")
            if result:
                results.append(result)

        # Check 'out' transition
        if "out" in transition and transition["out"]:
            result = self._check_transition_value(
                transition["out"], f"{field_path}.out"
            )
            if result:
                results.append(result)

        return results

    def _check_transition_value(
        self, value: Any, field_path: str
    ) -> Optional[ValidationResult]:
        """Check a single transition value."""
        if not isinstance(value, str):
            return self._create_result(
                status="ERROR",
                message=f"Transition value must be a string",
                level=ValidationLevel.ERROR,
                field=field_path,
            )

        if value.lower() not in VALID_TRANSITIONS:
            level = (
                ValidationLevel.WARNING
                if not self.strict_mode
                else ValidationLevel.ERROR
            )
            return self._create_result(
                status="WARNING" if not self.strict_mode else "ERROR",
                message=VALIDATION_MESSAGES["invalid_transition"].format(
                    value=value, options=", ".join(sorted(VALID_TRANSITIONS))
                ),
                suggestion=f"Use one of: {', '.join(sorted(VALID_TRANSITIONS))}",
                level=level,
                field=field_path,
            )

        return None

    def _validate_effect_field(
        self, effect: Any, field_path: str
    ) -> List[ValidationResult]:
        """Validate effect field."""
        results = []

        if not isinstance(effect, str):
            results.append(
                self._create_result(
                    status="ERROR",
                    message="Effect value must be a string",
                    level=ValidationLevel.ERROR,
                    field=field_path,
                )
            )
            return results

        if effect.lower() not in VALID_EFFECTS:
            level = (
                ValidationLevel.WARNING
                if not self.strict_mode
                else ValidationLevel.ERROR
            )
            results.append(
                self._create_result(
                    status="WARNING" if not self.strict_mode else "ERROR",
                    message=VALIDATION_MESSAGES["invalid_effect"].format(
                        value=effect, options=", ".join(sorted(VALID_EFFECTS))
                    ),
                    suggestion=f"Use one of: {', '.join(sorted(VALID_EFFECTS))}",
                    level=level,
                    field=field_path,
                )
            )

        return results

    def _validate_filter_field(
        self, filter_value: Any, field_path: str
    ) -> List[ValidationResult]:
        """Validate filter field."""
        results = []

        if not isinstance(filter_value, str):
            results.append(
                self._create_result(
                    status="ERROR",
                    message="Filter value must be a string",
                    level=ValidationLevel.ERROR,
                    field=field_path,
                )
            )
            return results

        if filter_value.lower() not in VALID_FILTERS:
            level = (
                ValidationLevel.WARNING
                if not self.strict_mode
                else ValidationLevel.ERROR
            )
            results.append(
                self._create_result(
                    status="WARNING" if not self.strict_mode else "ERROR",
                    message=VALIDATION_MESSAGES["invalid_filter"].format(
                        value=filter_value, options=", ".join(sorted(VALID_FILTERS))
                    ),
                    suggestion=f"Use one of: {', '.join(sorted(VALID_FILTERS))}",
                    level=level,
                    field=field_path,
                )
            )

        return results

    def validate_aspect_ratio(
        self, aspect_ratio: Any, field_path: str = "output.aspect_ratio"
    ) -> List[ValidationResult]:
        """Validate aspect ratio field."""
        results = []

        if not isinstance(aspect_ratio, str):
            results.append(
                self._create_result(
                    status="ERROR",
                    message="Aspect ratio must be a string",
                    level=ValidationLevel.ERROR,
                    field=field_path,
                )
            )
            return results

        if aspect_ratio not in VALID_ASPECT_RATIOS:
            level = (
                ValidationLevel.WARNING
                if not self.strict_mode
                else ValidationLevel.ERROR
            )
            results.append(
                self._create_result(
                    status="WARNING" if not self.strict_mode else "ERROR",
                    message=VALIDATION_MESSAGES["invalid_aspect_ratio"].format(
                        value=aspect_ratio,
                        options=", ".join(sorted(VALID_ASPECT_RATIOS)),
                    ),
                    suggestion=f"Use one of: {', '.join(sorted(VALID_ASPECT_RATIOS))}",
                    level=level,
                    field=field_path,
                )
            )

        return results

    def get_valid_values_summary(self) -> Dict[str, Set[str]]:
        """Get summary of all valid values for reference."""
        return {
            "transitions": VALID_TRANSITIONS.copy(),
            "effects": VALID_EFFECTS.copy(),
            "filters": VALID_FILTERS.copy(),
            "aspect_ratios": VALID_ASPECT_RATIOS.copy(),
        }
