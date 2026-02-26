"""
JSON structure validator for Shotstack Template.
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base import BaseValidator, ValidationResult, ValidationLevel, ValidationReport
from .models import ShotstackTemplate
from .constants import (
    REQUIRED_TOP_LEVEL_FIELDS,
    REQUIRED_TIMELINE_FIELDS,
    PLACEHOLDER_PATTERN,
    VALIDATION_MESSAGES,
)
import re


class JsonValidator(BaseValidator):
    """Validator for JSON structure and required fields."""

    def __init__(self, strict_mode: bool = False):
        super().__init__(strict_mode)

    def validate(self, data: Dict[str, Any]) -> ValidationReport:
        """Validate the entire JSON structure."""
        results = []

        # Validate JSON syntax
        results.extend(self._validate_json_syntax(data))

        # Validate required top-level fields
        results.extend(self._validate_required_fields(data))

        # Validate template structure
        if "template" in data:
            results.extend(self._validate_template_structure(data["template"]))

        # Validate merge array
        if "merge" in data:
            results.extend(
                self._validate_merge_array(data["merge"], data.get("template", {}))
            )

        # Validate output structure
        if "output" in data:
            results.extend(self._validate_output_structure(data["output"]))

        return ValidationReport.from_results(results)

    def _validate_json_syntax(self, data: Any) -> List[ValidationResult]:
        """Validate that data is proper JSON-serializable."""
        results = []

        try:
            json.dumps(data)
        except (TypeError, ValueError) as e:
            results.append(
                self._create_result(
                    status="ERROR",
                    message=VALIDATION_MESSAGES["invalid_json"].format(error=str(e)),
                    level=ValidationLevel.ERROR,
                )
            )

        return results

    def _validate_required_fields(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate required top-level fields."""
        results = []

        for field in REQUIRED_TOP_LEVEL_FIELDS:
            if field not in data:
                results.append(
                    self._create_result(
                        status="ERROR",
                        message=VALIDATION_MESSAGES["missing_required_field"].format(
                            field=field
                        ),
                        level=ValidationLevel.ERROR,
                        field=field,
                    )
                )

        return results

    def _validate_template_structure(
        self, template: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate template structure."""
        results = []

        if not isinstance(template, dict):
            results.append(
                self._create_result(
                    status="ERROR",
                    message="Template must be a dictionary",
                    level=ValidationLevel.ERROR,
                    field="template",
                )
            )
            return results

        # Validate timeline
        if "timeline" not in template:
            results.append(
                self._create_result(
                    status="ERROR",
                    message=VALIDATION_MESSAGES["missing_required_field"].format(
                        field="template.timeline"
                    ),
                    level=ValidationLevel.ERROR,
                    field="template.timeline",
                )
            )
        else:
            results.extend(self._validate_timeline_structure(template["timeline"]))

        return results

    def _validate_timeline_structure(
        self, timeline: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate timeline structure."""
        results = []

        if not isinstance(timeline, dict):
            results.append(
                self._create_result(
                    status="ERROR",
                    message="Timeline must be a dictionary",
                    level=ValidationLevel.ERROR,
                    field="template.timeline",
                )
            )
            return results

        # Validate required timeline fields
        for field in REQUIRED_TIMELINE_FIELDS:
            if field not in timeline:
                results.append(
                    self._create_result(
                        status="ERROR",
                        message=VALIDATION_MESSAGES["missing_required_field"].format(
                            field=f"template.timeline.{field}"
                        ),
                        level=ValidationLevel.ERROR,
                        field=f"template.timeline.{field}",
                    )
                )

        # Validate tracks structure
        if "tracks" in timeline:
            results.extend(self._validate_tracks_structure(timeline["tracks"]))

        return results

    def _validate_tracks_structure(self, tracks: Any) -> List[ValidationResult]:
        """Validate tracks structure."""
        results = []

        if not isinstance(tracks, list):
            results.append(
                self._create_result(
                    status="ERROR",
                    message="Tracks must be a list",
                    level=ValidationLevel.ERROR,
                    field="template.timeline.tracks",
                )
            )
            return results

        if not tracks:
            results.append(
                self._create_result(
                    status="ERROR",
                    message=VALIDATION_MESSAGES["empty_template"],
                    level=ValidationLevel.ERROR,
                    field="template.timeline.tracks",
                )
            )

        for i, track in enumerate(tracks):
            results.extend(self._validate_single_track(track, i))

        return results

    def _validate_single_track(self, track: Any, index: int) -> List[ValidationResult]:
        """Validate a single track."""
        results = []

        if not isinstance(track, dict):
            results.append(
                self._create_result(
                    status="ERROR",
                    message=f"Track {index} must be a dictionary",
                    level=ValidationLevel.ERROR,
                    field=f"template.timeline.tracks[{index}]",
                )
            )
            return results

        if "clips" not in track:
            results.append(
                self._create_result(
                    status="ERROR",
                    message=f"Track {index} missing 'clips' field",
                    level=ValidationLevel.ERROR,
                    field=f"template.timeline.tracks[{index}].clips",
                )
            )
            return results

        if not isinstance(track["clips"], list):
            results.append(
                self._create_result(
                    status="ERROR",
                    message=f"Track {index} clips must be a list",
                    level=ValidationLevel.ERROR,
                    field=f"template.timeline.tracks[{index}].clips",
                )
            )
        else:
            for j, clip in enumerate(track["clips"]):
                results.extend(self._validate_clip(clip, index, j))

        return results

    def _validate_clip(
        self, clip: Any, track_index: int, clip_index: int
    ) -> List[ValidationResult]:
        """Validate a single clip."""
        results = []

        if not isinstance(clip, dict):
            results.append(
                self._create_result(
                    status="ERROR",
                    message=f"Clip [{track_index}][{clip_index}] must be a dictionary",
                    level=ValidationLevel.ERROR,
                    field=f"template.timeline.tracks[{track_index}].clips[{clip_index}]",
                )
            )
            return results

        # Check for asset
        if "asset" not in clip:
            results.append(
                self._create_result(
                    status="ERROR",
                    message=f"Clip [{track_index}][{clip_index}] missing 'asset' field",
                    level=ValidationLevel.ERROR,
                    field=f"template.timeline.tracks[{track_index}].clips[{clip_index}].asset",
                )
            )

        # Check for start and length
        for field in ["start", "length"]:
            if field not in clip:
                results.append(
                    self._create_result(
                        status="ERROR",
                        message=f"Clip [{track_index}][{clip_index}] missing '{field}' field",
                        level=ValidationLevel.ERROR,
                        field=f"template.timeline.tracks[{track_index}].clips[{clip_index}].{field}",
                    )
                )
            elif not isinstance(clip[field], (int, float)) or clip[field] < 0:
                results.append(
                    self._create_result(
                        status="ERROR",
                        message=f"Clip [{track_index}][{clip_index}] field '{field}' must be a non-negative number",
                        level=ValidationLevel.ERROR,
                        field=f"template.timeline.tracks[{track_index}].clips[{clip_index}].{field}",
                    )
                )

        return results

    def _validate_merge_array(
        self, merge: Any, template: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate merge array structure."""
        results = []

        if not isinstance(merge, list):
            results.append(
                self._create_result(
                    status="ERROR",
                    message="Merge must be a list",
                    level=ValidationLevel.ERROR,
                    field="merge",
                )
            )
            return results

        if not merge:
            results.append(
                self._create_result(
                    status="ERROR",
                    message=VALIDATION_MESSAGES["empty_merge"],
                    level=ValidationLevel.ERROR,
                    field="merge",
                )
            )
            return results

        # Validate each merge entry
        for i, entry in enumerate(merge):
            results.extend(self._validate_merge_entry(entry, i))

        # Check for placeholders without merge entries
        results.extend(self._validate_placeholders(template, merge))

        return results

    def _validate_merge_entry(self, entry: Any, index: int) -> List[ValidationResult]:
        """Validate a single merge entry."""
        results = []

        if not isinstance(entry, dict):
            results.append(
                self._create_result(
                    status="ERROR",
                    message=f"Merge entry {index} must be a dictionary",
                    level=ValidationLevel.ERROR,
                    field=f"merge[{index}]",
                )
            )
            return results

        # Check required fields
        for field in ["find", "replace"]:
            if field not in entry:
                results.append(
                    self._create_result(
                        status="ERROR",
                        message=f"Merge entry {index} missing '{field}' field",
                        level=ValidationLevel.ERROR,
                        field=f"merge[{index}].{field}",
                    )
                )
            elif not isinstance(entry[field], str):
                results.append(
                    self._create_result(
                        status="ERROR",
                        message=f"Merge entry {index} field '{field}' must be a string",
                        level=ValidationLevel.ERROR,
                        field=f"merge[{index}].{field}",
                    )
                )

        return results

    def _validate_placeholders(
        self, template: Dict[str, Any], merge: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """Validate that all placeholders have corresponding merge entries."""
        results = []

        # Extract all placeholder patterns from template
        template_str = json.dumps(template)
        placeholders = re.findall(PLACEHOLDER_PATTERN, template_str)

        # Get all find values from merge array
        merge_find_values = {
            entry.get("find", "") for entry in merge if isinstance(entry, dict)
        }

        # Check each placeholder
        for placeholder in placeholders:
            if placeholder not in merge_find_values:
                level = (
                    ValidationLevel.WARNING
                    if not self.strict_mode
                    else ValidationLevel.ERROR
                )
                results.append(
                    self._create_result(
                        status="WARNING" if not self.strict_mode else "ERROR",
                        message=VALIDATION_MESSAGES["placeholder_no_merge"].format(
                            value=placeholder
                        ),
                        level=level,
                        field="merge",
                    )
                )

        return results

    def _validate_output_structure(
        self, output: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate output structure."""
        results = []

        if not isinstance(output, dict):
            results.append(
                self._create_result(
                    status="ERROR",
                    message="Output must be a dictionary",
                    level=ValidationLevel.ERROR,
                    field="output",
                )
            )
            return results

        # Validate common output fields
        if "format" in output and not isinstance(output["format"], str):
            results.append(
                self._create_result(
                    status="ERROR",
                    message="Output format must be a string",
                    level=ValidationLevel.ERROR,
                    field="output.format",
                )
            )

        if "fps" in output:
            if not isinstance(output["fps"], (int, float)) or output["fps"] <= 0:
                results.append(
                    self._create_result(
                        status="ERROR",
                        message="Output fps must be a positive number",
                        level=ValidationLevel.ERROR,
                        field="output.fps",
                    )
                )

        return results

    def validate_file(self, file_path: Path) -> ValidationReport:
        """Validate a JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self.validate(data)
        except FileNotFoundError:
            return ValidationReport.from_results(
                [
                    self._create_result(
                        status="ERROR",
                        message=f"File not found: {file_path}",
                        level=ValidationLevel.ERROR,
                    )
                ]
            )
        except json.JSONDecodeError as e:
            return ValidationReport.from_results(
                [
                    self._create_result(
                        status="ERROR",
                        message=f"Invalid JSON in {file_path}: {str(e)}",
                        level=ValidationLevel.ERROR,
                    )
                ]
            )
