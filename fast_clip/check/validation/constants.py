"""
Constants for valid Shotstack field values.
"""

# Valid transitions (case-insensitive)
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

# Valid effects (case-insensitive)
VALID_EFFECTS = {"zoomin", "zoomout", "kenburns"}

# Valid filters (case-insensitive)
VALID_FILTERS = {
    "boost",
    "greyscale",
    "contrast",
    "muted",
    "negative",
    "darken",
    "lighten",
}

# Valid aspect ratios
VALID_ASPECT_RATIOS = {"9:16", "16:9", "1:1", "4:5", "4:3"}

# Required top-level fields in Shotstack Template
REQUIRED_TOP_LEVEL_FIELDS = {"template", "output", "merge"}

# Required fields in template.timeline
REQUIRED_TIMELINE_FIELDS = {"tracks"}

# Valid asset types
VALID_ASSET_TYPES = {"video", "image", "audio", "text", "title", "html"}

# Placeholder pattern for merge functionality
PLACEHOLDER_PATTERN = r"\{\{([^}]+)\}\}"

# Validation messages
VALIDATION_MESSAGES = {
    "missing_required_field": "Missing required field: '{field}'",
    "invalid_transition": "Invalid transition: '{value}'. Valid options: {options}",
    "invalid_effect": "Invalid effect: '{value}'. Valid options: {options}",
    "invalid_filter": "Invalid filter: '{value}'. Valid options: {options}",
    "invalid_aspect_ratio": "Invalid aspect ratio: '{value}'. Valid options: {options}",
    "file_not_found": "Media file not found: '{path}'",
    "file_not_accessible": "Media file not accessible: '{path}' (permission denied)",
    "invalid_json": "Invalid JSON syntax: {error}",
    "empty_template": "Template cannot be empty",
    "empty_merge": "Merge array cannot be empty",
    "invalid_placeholder": "Invalid placeholder syntax: '{value}'. Use format: {{field}}",
    "placeholder_no_merge": "No merge entry found for placeholder: '{value}'",
}
