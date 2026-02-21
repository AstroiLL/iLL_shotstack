"""Timeline builder for Fast-Clip - processes Shotstack-native JSON."""

import re
from typing import Any


class TimelineBuilder:
    """Processes Shotstack-native JSON and replaces resource placeholders with URLs."""

    def __init__(self, script_data: dict[str, Any]):
        self.script = script_data
        self.uploaded_urls: dict[str, str] = {}

    def update_script(self, new_script_data: dict[str, Any]):
        """Update the internal script data."""
        self.script = new_script_data

    def set_uploaded_files(self, uploaded_files: dict[str, str]):
        """Set mapping of uploaded files to their URLs.

        Args:
            uploaded_files: Dict mapping resource path to URL
        """
        self.uploaded_urls = uploaded_files

    def _resolve_placeholders(self, data: Any) -> Any:
        """Recursively resolve {{placeholder}} patterns in data."""
        if isinstance(data, str):
            # Match {{resources_dir/filename}} pattern
            match = re.match(r"^\{\{([^}]+)\}\}$", data)
            if match:
                resource_path = match.group(1)
                if resource_path in self.uploaded_urls:
                    return self.uploaded_urls[resource_path]
                # Allow template placeholders without uploaded URLs (for development)
                elif "/" in resource_path:
                    return data  # Keep as template placeholder
                else:
                    raise ValueError(f"Resource not uploaded: {resource_path}")
            return data
        elif isinstance(data, dict):
            return {k: self._resolve_placeholders(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._resolve_placeholders(item) for item in data]
        return data

    def build(self) -> dict:
        """Build complete Shotstack edit data with resolved URLs.

        Returns:
            Complete Shotstack edit dict with real URLs
        """
        # Deep copy and resolve all placeholders
        resolved = self._resolve_placeholders(self.script)

        # Handle case where timeline might be empty or missing
        if isinstance(resolved, dict) and "timeline" in resolved:
            timeline = resolved.get("timeline", {})
            if not timeline or not timeline.get("tracks"):
                # Return minimal valid structure
                resolved["timeline"] = {"tracks": []}

        # Remove our custom fields that Shotstack doesn't need
        if isinstance(resolved, dict):
            resolved.pop("name", None)
            # resourcesDir is needed for processing, but handle gracefully if missing
            if "resourcesDir" in resolved:
                resolved.pop("resourcesDir", None)

        return resolved
