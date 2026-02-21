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

        if output_dir is None:
            output_dir = Path.cwd()

        # Use output filename from script or default
        output_config = script_data.get("output", {})
        output_name = output_config.get("filename", "output.mp4")
        output_path = output_dir / output_name

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

    def assemble_with_template(
        self,
        script_path: Path,
        output_dir: Optional[Path] = None,
        verbose: bool = False,
    ) -> AssemblyResult:
        """Assemble video from script using template + merge workflow.

        Args:
            script_path: Path to JSON script with template
            output_dir: Where to save output (default: current directory)
            verbose: Print progress

        Returns:
            AssemblyResult with status
        """
        """Assemble video from script using template + merge workflow.

        Args:
            script_path: Path to JSON script with template
            output_dir: Where to save output (default: current directory)
            verbose: Print progress

        Returns:
            AssemblyResult with status
        """
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
        resources_dir_name = script_data.get(
            "resourcesDir", template_data.get("resourcesDir", ".")
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

            if verbose:
                print(f"   [{i + 1}/{len(unique_files)}] Uploading {filename}...")

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
        merge_data = []
        for merge_field in merge_fields:
            find_value = merge_field.get("find", "")
            if find_value and "/" in find_value:
                filename = find_value.split("/")[-1]
                if filename in uploaded_files:
                    merge_data.append(
                        {"find": find_value, "replace": uploaded_files[filename]}
                    )

        if verbose and merge_data:
            print(f"🔗 Merge data prepared: {len(merge_data)} replacements")

        # Step 4: Render video using template
        if verbose:
            print("🚀 Submitting render job with template...")

        render_data = {"id": script_data.get("name", "template"), "merge": merge_data}

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

        if output_dir is None:
            output_dir = Path.cwd()

        # Use output filename from template or default
        template_output = template_data.get("output", {})
        output_name = template_output.get("filename", "output.mp4")
        output_path = output_dir / output_name

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
