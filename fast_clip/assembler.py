"""Video assembler for Fast-Clip - main orchestration module."""

import json
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
        resources_dir = script_dir / script_data.get("resources_dir", ".")

        if not resources_dir.exists():
            return AssemblyResult(
                success=False, error=f"Resources directory not found: {resources_dir}"
            )

        # Step 3: Upload video files
        if verbose:
            print("📤 Uploading video files...")

        timeline = script_data.get("timeline", [])
        uploaded_files = {}

        for i, item in enumerate(timeline):
            resource = item.get("resource")
            if not resource:
                continue

            file_path = resources_dir / resource

            if verbose:
                print(f"   [{i + 1}/{len(timeline)}] Uploading {resource}...")

            result = self.uploader.upload(file_path)

            if not result.success:
                return AssemblyResult(
                    success=False, error=f"Failed to upload {resource}: {result.error}"
                )

            uploaded_files[resource] = result.url

            if verbose:
                print(f"      ✓ Uploaded (ID: {result.file_id})")

        # Step 4: Build timeline
        if verbose:
            print("🎬 Building timeline...")

        builder = TimelineBuilder(script_data)
        builder.set_uploaded_files(uploaded_files)

        try:
            edit_data = builder.build()
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

        output_path = output_dir / script_data.get("result_file", "output.mp4")

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
