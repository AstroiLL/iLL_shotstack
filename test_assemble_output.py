#!/usr/bin/env python3
"""Test assemble.py default output behavior."""

import json
from pathlib import Path
import tempfile
import shutil

# Create a test project
test_project_dir = Path(tempfile.mkdtemp())
print(f"Created test project: {test_project_dir}")

# Create script
script_data = {
    "name": "test-video",
    "resourcesDir": "resources",
    "template": {
        "timeline": {
            "tracks": [
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "video",
                                "src": "{{resources/video.mp4}}",
                            },
                            "start": 0.0,
                            "length": 5.0,
                        }
                    ]
                }
            ]
        }
    },
    "output": {"format": "mp4", "resolution": "sd", "aspectRatio": "9:16", "fps": 30},
    "merge": [],
}

script_path = test_project_dir / "test-video.json"
with open(script_path, "w") as f:
    json.dump(script_data, f, indent=2)

# Create resources directory
resources_dir = test_project_dir / "resources"
resources_dir.mkdir()

# Create a dummy video file
dummy_video = resources_dir / "video.mp4"
dummy_video.touch()
print(f"Created dummy video: {dummy_video}")

# Check output directory before running
print(f"\nBefore running assemble:")
print(f"  Output directory exists: {(test_project_dir / 'output').exists()}")
print(f"  Video file exists: {dummy_video.exists()}")

print(f"\nTest project structure:")
for item in test_project_dir.rglob("*"):
    if item.is_file():
        print(f"  {item.relative_to(test_project_dir)}")

# Cleanup
shutil.rmtree(test_project_dir)
print(f"\n✓ Test complete")
