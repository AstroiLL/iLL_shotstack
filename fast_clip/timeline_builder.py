"""Timeline builder for Fast-Clip - converts scripts to Shotstack format."""

from typing import Any


class TimelineBuilder:
    """Builds Shotstack timeline from Fast-Clip scripts."""

    # Effect mappings
    EFFECT_MAP = {
        "fade_in": {"in": "fade"},
        "fade_out": {"out": "fade"},
        "slide_in": {"in": "slideUp"},  # default direction
        "slide_out": {"out": "slideDown"},  # default direction
    }

    # Resolution mappings
    RESOLUTION_MAP = {
        "2160p": {"width": 3840, "height": 2160},
        "1440p": {"width": 2560, "height": 1440},
        "1080p": {"width": 1920, "height": 1080},
        "720p": {"width": 1280, "height": 720},
        "480p": {"width": 854, "height": 480},
    }

    # Orientation aspect ratios
    ORIENTATION_MAP = {
        "landscape": (16, 9),
        "portrait": (9, 16),
        "square": (1, 1),
    }

    def __init__(self, script_data: dict[str, Any]):
        self.script = script_data
        self.clips: list[dict] = []
        self.uploaded_urls: dict[str, str] = {}  # resource_name -> url

    def set_uploaded_files(self, uploaded_files: dict[str, str]):
        """Set mapping of uploaded files to their URLs.

        Args:
            uploaded_files: Dict mapping resource name to URL
        """
        self.uploaded_urls = uploaded_files

    @staticmethod
    def parse_time(time_str: str) -> int:
        """Parse time string to seconds.

        Supports formats: MM:SS, HH:MM:SS

        Args:
            time_str: Time string like "00:05" or "01:30:00"

        Returns:
            Time in seconds
        """
        parts = time_str.split(":")
        if len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            raise ValueError(f"Invalid time format: {time_str}")

    @staticmethod
    def parse_duration(duration_str: str) -> float:
        """Parse duration string to seconds.

        Args:
            duration_str: Duration like "3s"

        Returns:
            Duration in seconds
        """
        if duration_str.endswith("s"):
            return float(duration_str[:-1])
        return float(duration_str)

    def _build_clip(self, item: dict, index: int) -> dict:
        """Build a single clip from timeline item.

        Args:
            item: Timeline item from script
            index: Clip index

        Returns:
            Shotstack clip dict
        """
        resource = item["resource"]

        # Get URL for uploaded file
        if resource not in self.uploaded_urls:
            raise ValueError(f"File not uploaded: {resource}")

        url = self.uploaded_urls[resource]

        # Parse time
        time_start = self.parse_time(item["time_start"])
        time_end = self.parse_time(item["time_end"])
        duration = time_end - time_start

        # Build clip
        clip: dict = {
            "asset": {
                "type": "video",
                "src": url,
                "trim": time_start,
            },
            "start": "auto",  # Sequential placement
            "length": duration,
        }

        # Add transitions (effects)
        transition = {}

        start_effect = item.get("start_effect")

        if start_effect and start_effect in self.EFFECT_MAP:
            effect_config = self.EFFECT_MAP[start_effect]
            if "in" in effect_config:
                transition["in"] = effect_config["in"]

        end_effect = item.get("end_effect")

        if end_effect and end_effect in self.EFFECT_MAP:
            effect_config = self.EFFECT_MAP[end_effect]
            if "out" in effect_config:
                transition["out"] = effect_config["out"]

        if transition:
            clip["transition"] = transition

        return clip

    def build_timeline(self) -> dict:
        """Build Shotstack timeline.

        Returns:
            Shotstack timeline dict
        """
        timeline_items = self.script.get("timeline", [])

        clips = []
        for i, item in enumerate(timeline_items):
            clip = self._build_clip(item, i)
            clips.append(clip)

        return {"tracks": [{"clips": clips}]}

    def build_output(self) -> dict:
        """Build Shotstack output configuration.

        Returns:
            Shotstack output dict
        """
        # Get resolution
        resolution = self.script.get("resolution", "1080p")
        orientation = self.script.get("orientation", "landscape")
        output_format = self.script.get("output_format", "mp4")

        # Calculate dimensions based on resolution and orientation
        if resolution in self.RESOLUTION_MAP:
            base_dims = self.RESOLUTION_MAP[resolution]
            base_width, base_height = base_dims["width"], base_dims["height"]
        else:
            # Default to 1080p
            base_width, base_height = 1920, 1080

        # Apply orientation
        if orientation == "portrait":
            width, height = min(base_width, base_height), max(base_width, base_height)
        elif orientation == "square":
            min_dim = min(base_width, base_height)
            width, height = min_dim, min_dim
        else:  # landscape
            width, height = max(base_width, base_height), min(base_width, base_height)

        return {"format": output_format, "size": {"width": width, "height": height}}

    def build(self) -> dict:
        """Build complete Shotstack edit data.

        Returns:
            Complete Shotstack edit dict
        """
        return {"timeline": self.build_timeline(), "output": self.build_output()}
