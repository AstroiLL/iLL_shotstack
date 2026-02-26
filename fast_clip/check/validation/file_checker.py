"""
File checker for media file availability validation.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from urllib.parse import urlparse

from .base import BaseValidator, ValidationResult, ValidationLevel, ValidationReport


class FileChecker(BaseValidator):
    """Validator for checking media file availability."""

    def __init__(
        self,
        strict_mode: bool = False,
        script_path: Optional[Path] = None,
        max_workers: Optional[int] = None,
    ):
        super().__init__(strict_mode)
        self.script_path = script_path
        self._thread_pool = None
        self._validation_cache: Dict[str, ValidationResult] = {}
        self._max_workers = max_workers or min(8, (os.cpu_count() or 4) * 2)
        self._parallel_threshold = 5
        self._base_dir_cache: Optional[Path] = None
        self._content_dir_cache: Optional[Path] = None

    def validate(self, data: Dict[str, Any]) -> ValidationReport:
        """Validate all media files in template."""
        results = []
        file_paths = self._extract_file_paths(data)

        # Early return if no files to check
        if not file_paths:
            return ValidationReport.from_results([])

        # Filter out cached results first
        uncached_paths = [p for p in file_paths if p not in self._validation_cache]
        cached_results = [
            self._validation_cache[p] for p in file_paths if p in self._validation_cache
        ]
        results.extend(cached_results)

        # Use parallel processing for projects above threshold
        if len(uncached_paths) > self._parallel_threshold:
            results.extend(self._validate_files_parallel(uncached_paths))
        else:
            for file_path in uncached_paths:
                results.extend(self._check_file_accessibility(file_path))

        return ValidationReport.from_results(results)

    def _extract_file_paths(self, data: Dict[str, Any]) -> List[str]:
        """Extract all file paths from template data."""
        file_paths = []

        def extract_from_dict(d):
            for key, value in d.items():
                if key == "src" and isinstance(value, str):
                    # Skip URLs, only check local files
                    if not urlparse(value).scheme:
                        file_paths.append(value)
                elif isinstance(value, dict):
                    extract_from_dict(value)
                elif isinstance(value, list):
                    # Use list comprehension for better performance
                    for item in value:
                        if isinstance(item, dict):
                            extract_from_dict(item)

        # Extract from template section
        if "template" in data:
            extract_from_dict(data["template"])

        # Use set for deduplication, then convert to list
        return list(dict.fromkeys(file_paths))

    def _check_file_accessibility(self, file_path: str) -> List[ValidationResult]:
        """Check if a single file is accessible."""
        results = []

        # Check cache first
        if file_path in self._validation_cache:
            return [self._validation_cache[file_path]]

        resolved_path = self._resolve_path(file_path)

        if resolved_path.exists():
            result = ValidationResult(
                status="OK",
                level=ValidationLevel.INFO,
                field="file_accessibility",
                message=f"File accessible: {file_path}",
                suggestion=f"resolved: {resolved_path}",
            )
        else:
            status = "ERROR" if self.strict_mode else "WARNING"
            level = (
                ValidationLevel.ERROR if self.strict_mode else ValidationLevel.WARNING
            )
            result = ValidationResult(
                status=status,
                level=level,
                field="file_accessibility",
                message=f"File not found: {file_path}",
                suggestion=f"attempted: {resolved_path}",
            )

        # Cache result
        self._validation_cache[file_path] = result
        results.append(result)

        return results

    def _validate_files_parallel(self, file_paths: List[str]) -> List[ValidationResult]:
        """Validate files in parallel for better performance."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Use dynamic number of workers based on file count and CPU cores
        workers = min(self._max_workers, len(file_paths))

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_path = {
                executor.submit(self._check_file_accessibility, path): path
                for path in file_paths
            }

            results = []
            for future in as_completed(future_to_path.keys()):
                results.extend(future.result())

        return results

    def _resolve_path(self, file_path: str) -> Path:
        """Resolve relative path based on script location."""
        path = Path(file_path)

        if path.is_absolute():
            return path

        # Use cached base directory
        if self._base_dir_cache is None:
            if self.script_path:
                if self.script_path.is_file():
                    self._base_dir_cache = self.script_path.parent
                else:
                    self._base_dir_cache = self.script_path
            else:
                self._base_dir_cache = Path.cwd()

        base_dir = self._base_dir_cache

        # Try to resolve relative to the script's directory
        resolved = base_dir / path

        # If not found, try resolving relative to a Content directory (cached)
        if not resolved.exists():
            if self._content_dir_cache is None:
                self._content_dir_cache = base_dir / "Content"
            content_path = self._content_dir_cache / path
            if content_path.exists():
                resolved = content_path

        return resolved.resolve()

    def clear_cache(self):
        """Clear file access cache."""
        self._validation_cache.clear()
