"""Video assembler for Fast-Clip - main orchestration module."""

import json
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from .uploader import ShotstackUploader
from .timeline_builder import TimelineBuilder
from .shotstack_client import ShotstackClient


@dataclass
class AssemblyResult:
    """Result of video assembly."""

    success: bool
    output_path: Optional[Path] = None
    render_id: Optional[str] = None
    error: Optional[str] = None


class VideoAssembler:
    """Main video assembler using Shotstack API."""

    def __init__(
        self,
        api_key: str,
        ingest_url: str = "https://api.shotstack.io/ingest/stage",
        edit_url: str = "https://api.shotstack.io/edit/stage",
    ):
        self.api_key = api_key
        self.uploader = ShotstackUploader(api_key, ingest_url)
        self.client = ShotstackClient(api_key, edit_url)

    def _extract_resources(self, script_data: dict) -> list[str]:
        """Extract resource paths from script clips.

        Args:
            script_data: Script data with timeline

        Returns:
            List of resource paths
        """
        resources = []
        timeline = script_data.get("timeline", {})
        tracks = timeline.get("tracks", [])

        for track in tracks:
            clips = track.get("clips", [])
            for clip in clips:
                asset = clip.get("asset", {})
                src = asset.get("src", "")
                # Extract {{resources_dir/filename}} pattern
                match = re.match(r"^\{\{([^}]+)\}\}$", src)
                if match:
                    resources.append(match.group(1))

        return resources

    def assemble(
        self,
        script_path: Path,
        output_dir: Optional[Path] = None,
        verbose: bool = False,
    ) -> AssemblyResult:
        """Assemble video from script.

        Args:
            script_path: Path to JSON script
            output_dir: Where to save output (default: current directory)
            verbose: Print progress

        Returns:
            AssemblyResult with status
        """
        script_path = Path(script_path)

        # Step 1: Load and validate script
        if verbose:
            print(f"📄 Loading script: {script_path}")

        try:
            with open(script_path, "r", encoding="utf-8") as f:
                script_data = json.load(f)
        except FileNotFoundError:
            return AssemblyResult(
                success=False, error=f"Script not found: {script_path}"
            )
        except json.JSONDecodeError as e:
            return AssemblyResult(success=False, error=f"Invalid JSON: {e}")

        # Step 2: Get resources directory
        script_dir = script_path.parent
        # Get resources_dir from template data or main script level
        template_data = (
            script_data.get("template", {}) if "template" in script_data else {}
        )
        resources_dir_name = script_data.get(
            "resourcesDir", template_data.get("resourcesDir", ".")
        )
        resources_dir = script_dir / resources_dir_name

        if not resources_dir.exists():
            return AssemblyResult(
                success=False, error=f"Resources directory not found: {resources_dir}"
            )

        # Step 3: Upload video files
        if verbose:
            print("📤 Uploading video files...")

        resource_paths = self._extract_resources(script_data)
        uploaded_files = {}

        for i, resource_path in enumerate(resource_paths):
            # resource_path is like "Video_01/clip_01.mp4"
            file_path = script_dir / resource_path

            if verbose:
                resource_name = Path(resource_path).name
                print(
                    f"   [{i + 1}/{len(resource_paths)}] Uploading {resource_name}..."
                )

            result = self.uploader.upload(file_path)

            if not result.success:
                return AssemblyResult(
                    success=False,
                    error=f"Failed to upload {resource_path}: {result.error}",
                )

            uploaded_files[resource_path] = result.url

            if verbose:
                print(f"      ✓ Uploaded (ID: {result.file_id})")

        # Step 4: Build timeline
        if verbose:
            print("🎬 Building timeline...")

        # Create complete data for TimelineBuilder
        builder = TimelineBuilder(script_data)
        builder.set_uploaded_files(uploaded_files)

        try:
            edit_data = builder.build()
            if not edit_data:
                edit_data = {"timeline": {"tracks": []}}
        except ValueError as e:
            return AssemblyResult(success=False, error=f"Timeline build failed: {e}")

        # Step 5: Render video
        if verbose:
            print("🚀 Submitting render job...")

        render_result = self.client.render(edit_data)

        if not render_result.success:
            return AssemblyResult(
                success=False, error=f"Render submission failed: {render_result.error}"
            )

        render_id = render_result.render_id

        if render_id is None:
            return AssemblyResult(success=False, error="Render ID is None")

        if verbose:
            print(f"   ✓ Render ID: {render_id}")
            print("⏳ Waiting for render to complete...")

        # Step 6: Wait for completion
        def status_callback(status: str, url: Optional[str]):
            if verbose and status:
                print(f"   Status: {status}")

        final_result = self.client.wait_for_render(
            render_id, callback=status_callback if verbose else None
        )

        if not final_result.success:
            return AssemblyResult(
                success=False,
                render_id=render_id,
                error=f"Render failed: {final_result.error}",
            )

        # Step 7: Download result
        if verbose:
            print("💾 Downloading video...")

        # Generate output path based on script name
        output_path = self._generate_output_path(script_path, output_dir)

        if final_result.url is None:
            return AssemblyResult(
                success=False,
                render_id=render_id,
                error="Download URL is None",
            )

        success = self.client.download(final_result.url, output_path)

        if not success:
            return AssemblyResult(
                success=False,
                render_id=render_id,
                error=f"Failed to download video from {final_result.url}",
            )

        if verbose:
            print(f"   ✓ Saved to: {output_path}")
            print("✅ Assembly complete!")

        return AssemblyResult(
            success=True, output_path=output_path, render_id=render_id
        )

    def _generate_output_path(
        self, script_path: Path, output_dir: Optional[Path] = None
    ) -> Path:
        """Generate output path based on script name with index support.

        Args:
            script_path: Path to input script
            output_dir: Output directory (default: current directory)

        Returns:
            Path for output video file
        """
        if output_dir is None:
            output_dir = Path.cwd()

        # Get base name from script (e.g., "hello.json" -> "hello")
        base_name = script_path.stem

        # Start with base name + .mp4
        output_path = output_dir / f"{base_name}.mp4"

        # If file exists, find next available index
        counter = 1
        original_path = output_path
        while output_path.exists():
            output_path = output_dir / f"{base_name}_{counter}.mp4"
            counter += 1

        return output_path

    def _verify_script(self, script_data: dict, script_path: Path) -> tuple[bool, str]:
        """Verify script structure and resources.

        Args:
            script_data: Loaded script data
            script_path: Path to script file

        Returns:
            (success, error_message)
        """
        errors = []

        # Check required fields
        if "template" not in script_data:
            errors.append("Missing required field: 'template'")
        else:
            template = script_data["template"]
            if "timeline" not in template:
                errors.append("Missing required field: 'template.timeline'")
            if "output" not in template:
                errors.append("Missing required field: 'template.output'")

        if "merge" not in script_data:
            errors.append("Missing required field: 'merge'")
        elif not isinstance(script_data["merge"], list):
            errors.append("Field 'merge' must be an array")
        elif len(script_data["merge"]) == 0:
            errors.append("Field 'merge' is empty - no resources to process")

        # Check resources directory
        script_dir = script_path.parent
        resources_dir_name = script_data.get("resourcesDir", ".")
        if "template" in script_data and isinstance(script_data["template"], dict):
            resources_dir_name = script_data["template"].get(
                "resourcesDir", resources_dir_name
            )
        resources_dir = script_dir / resources_dir_name

        if not resources_dir.exists():
            errors.append(f"Resources directory not found: {resources_dir}")
        elif not resources_dir.is_dir():
            errors.append(f"Resources path is not a directory: {resources_dir}")

        # Check all files from merge fields exist
        if "merge" in script_data and isinstance(script_data["merge"], list):
            missing_files = []
            invalid_extensions = []
            supported_video = {".mp4", ".mov", ".avi", ".mkv"}
            supported_audio = {".mp3", ".wav", ".aac", ".ogg"}
            supported_image = {".jpg", ".jpeg", ".png", ".gif"}
            supported = supported_video | supported_audio | supported_image

            for merge_field in script_data["merge"]:
                if isinstance(merge_field, dict):
                    find_value = merge_field.get("find", "")
                    if find_value and "/" in find_value:
                        filename = find_value.split("/")[-1]
                        file_path = resources_dir / filename

                        if not file_path.exists():
                            missing_files.append(filename)

                        # Check extension
                        ext = Path(filename).suffix.lower()
                        if ext and ext not in supported:
                            invalid_extensions.append(f"{filename} ({ext})")

            if missing_files:
                errors.append(
                    f"Missing files ({len(missing_files)}): {', '.join(missing_files[:5])}"
                )
                if len(missing_files) > 5:
                    errors.append(f"  ... and {len(missing_files) - 5} more")

            if invalid_extensions:
                errors.append(
                    f"Unsupported file formats: {', '.join(invalid_extensions[:3])}"
                )

        # Check timeline structure
        if "template" in script_data and isinstance(script_data["template"], dict):
            timeline = script_data["template"].get("timeline", {})
            tracks = timeline.get("tracks", [])

            if not tracks:
                errors.append("No tracks found in timeline")
            else:
                total_clips = 0
                for i, track in enumerate(tracks):
                    clips = track.get("clips", [])
                    total_clips += len(clips)

                    for j, clip in enumerate(clips):
                        # Validate clip structure
                        if "asset" not in clip:
                            errors.append(f"Track {i}, clip {j}: missing 'asset'")
                        elif (
                            clip["asset"].get("type") != "text"
                            and "src" not in clip["asset"]
                        ):
                            # Text clips don't need src, only video/image/audio clips do
                            errors.append(f"Track {i}, clip {j}: missing 'asset.src'")

                if total_clips == 0:
                    errors.append("No clips found in any track")

        if errors:
            return False, "\n".join(errors)

        return True, ""

    def assemble_with_template(
        self,
        script_path: Path,
        output_dir: Optional[Path] = None,
        verbose: bool = False,
    ) -> AssemblyResult:
        script_path = Path(script_path)

        # Step 1: Load and validate script
        if verbose:
            print(f"📄 Loading template script: {script_path}")

        try:
            with open(script_path, "r", encoding="utf-8") as f:
                script_data = json.load(f)
        except FileNotFoundError:
            return AssemblyResult(
                success=False, error=f"Script not found: {script_path}"
            )
        except json.JSONDecodeError as e:
            return AssemblyResult(success=False, error=f"Invalid JSON: {e}")

        # Verify script structure and resources
        if verbose:
            print("🔍 Verifying script...")

        is_valid, error_msg = self._verify_script(script_data, script_path)
        if not is_valid:
            return AssemblyResult(
                success=False, error=f"Script verification failed:\n{error_msg}"
            )

        if verbose:
            print("   ✓ Script structure valid")
            merge_count = len(script_data.get("merge", []))
            print(f"   ✓ Found {merge_count} resources to process")

        # Check if this is a template format
        if "template" not in script_data:
            return AssemblyResult(
                success=False,
                error="Script is not in template format. Missing 'template' field.",
            )

        template_data = script_data.get("template", {})
        merge_fields = script_data.get("merge", [])

        # Step 2: Upload files for merge fields
        if verbose:
            print("📤 Uploading files for template...")

        uploaded_files = {}
        script_dir = script_path.parent
        # Get resources_dir from template data
        template_data = script_data.get("template", {})
        resources_dir_name = template_data.get(
            "resourcesDir", script_data.get("resourcesDir", ".")
        )
        resources_dir = script_dir / resources_dir_name

        if verbose:
            print(f"Debug: Using resources_dir = {resources_dir_name}")

        if not resources_dir.exists():
            return AssemblyResult(
                success=False, error=f"Resources directory not found: {resources_dir}"
            )

        # Collect all unique files from merge fields
        unique_files = set()
        for merge_field in merge_fields:
            find_value = merge_field.get("find", "")
            if find_value and "/" in find_value:
                filename = find_value.split("/")[-1]
                unique_files.add(filename)

        # Upload all unique files
        for i, filename in enumerate(unique_files):
            file_path = resources_dir / filename

            if verbose:
                print(
                    f"   [{i + 1}/{len(unique_files)}] Uploading {filename} from {file_path}..."
                )

            result = self.uploader.upload(file_path)

            if not result.success:
                return AssemblyResult(
                    success=False,
                    error=f"Failed to upload {filename}: {result.error}",
                )

            uploaded_files[filename] = result.url

            if verbose:
                print(f"      ✓ Uploaded (ID: {result.file_id})")

        # Step 3: Prepare merge data with uploaded URLs
        # Note: find should be without {{}} and match the placeholder name in timeline
        merge_data = []
        for merge_field in merge_fields:
            if isinstance(merge_field, dict):
                find_value = merge_field.get("find", "")
                if find_value and "/" in find_value:
                    filename = find_value.split("/")[-1]
                    if filename in uploaded_files:
                        # Use just the filename (without Content/) as find value
                        merge_data.append(
                            {"find": filename, "replace": uploaded_files[filename]}
                        )
                        if verbose:
                            print(
                                f"   ✓ Prepared merge: {filename} -> {uploaded_files[filename][:50]}..."
                            )

        if verbose and merge_data:
            print(f"🔗 Merge data prepared: {len(merge_data)} replacements")

        # Step 4: Replace placeholders in timeline and render
        if verbose:
            print("🚀 Preparing timeline for render...")

        # Deep copy timeline and replace placeholders with URLs
        import copy

        timeline = copy.deepcopy(template_data.get("timeline", {}))

        def replace_placeholders(obj):
            if isinstance(obj, str):
                # Replace {{Content/filename}} with URL using filename as key
                for merge_item in merge_data:
                    # Match {{Content/filename}} pattern
                    placeholder_with_path = "{{Content/" + merge_item["find"] + "}}"
                    placeholder_simple = "{{" + merge_item["find"] + "}}"
                    if placeholder_with_path in obj:
                        obj = obj.replace(placeholder_with_path, merge_item["replace"])
                    elif placeholder_simple in obj:
                        obj = obj.replace(placeholder_simple, merge_item["replace"])
                return obj
            elif isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            return obj

        timeline = replace_placeholders(timeline)

        # Prepare render data with timeline, output, and merge
        render_data = {
            "timeline": timeline,
            "output": template_data.get("output", {}),
            "merge": [],
        }

        if verbose:
            tracks_count = (
                len(timeline.get("tracks", [])) if isinstance(timeline, dict) else 0
            )
            print(f"   Template tracks: {tracks_count}")
            print(f"   Replacements applied: {len(merge_data)}")
            print("🎬 Submitting render job...")

        render_result = self.client.render(render_data)

        if not render_result.success:
            return AssemblyResult(
                success=False, error=f"Render submission failed: {render_result.error}"
            )

        render_id = render_result.render_id

        if render_id is None:
            return AssemblyResult(success=False, error="Render ID is None")

        if verbose:
            print(f"   ✓ Render ID: {render_id}")
            print("⏳ Waiting for render to complete...")

        # Step 5: Wait for completion
        def status_callback(status: str, url: Optional[str]):
            if verbose and status:
                print(f"   Status: {status}")

        final_result = self.client.wait_for_render(
            render_id, callback=status_callback if verbose else None
        )

        if not final_result.success:
            return AssemblyResult(
                success=False,
                render_id=render_id,
                error=f"Render failed: {final_result.error}",
            )

        # Step 6: Download result
        if verbose:
            print("💾 Downloading video...")

        # Generate output path based on script name
        output_path = self._generate_output_path(script_path, output_dir)

        if final_result.url is None:
            return AssemblyResult(
                success=False,
                render_id=render_id,
                error="Download URL is None",
            )

        success = self.client.download(final_result.url, output_path)

        if not success:
            return AssemblyResult(
                success=False,
                render_id=render_id,
                error=f"Failed to download video from {final_result.url}",
            )

        if verbose:
            print(f"   ✓ Saved to: {output_path}")
            print("✅ Template assembly complete!")

        return AssemblyResult(
            success=True, output_path=output_path, render_id=render_id
        )
