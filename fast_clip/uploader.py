"""Uploader module for Fast-Clip - handles file uploads to Shotstack."""

import time
import requests
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class UploadResult:
    """Result of file upload."""

    success: bool
    file_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None


class ShotstackUploader:
    """Uploader for Shotstack Ingest API."""

    def __init__(
        self, api_key: str, base_url: str = "https://api.shotstack.io/ingest/stage"
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "x-api-key": api_key,
            "Accept": "application/json",
        }

    def _get_signed_url(self) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Get signed URL for direct upload.

        Returns:
            Tuple of (file_id, signed_url, error_message)
        """
        url = f"{self.base_url}/upload"

        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            file_id = data["data"]["id"]
            signed_url = data["data"]["attributes"]["url"]

            return file_id, signed_url, None

        except requests.exceptions.RequestException as e:
            return None, None, f"Failed to get signed URL: {e}"
        except (KeyError, ValueError) as e:
            return None, None, f"Invalid response format: {e}"

    def _upload_file(self, file_path: Path, signed_url: str) -> Optional[str]:
        """Upload file to signed URL.

        Args:
            file_path: Path to local file
            signed_url: Signed URL from Shotstack

        Returns:
            Error message if failed, None if success
        """
        try:
            with open(file_path, "rb") as f:
                # Note: Do NOT include Content-Type header for S3 signed URLs
                response = requests.put(signed_url, data=f)
                response.raise_for_status()
            return None

        except requests.exceptions.RequestException as e:
            return f"Failed to upload file: {e}"
        except FileNotFoundError:
            return f"File not found: {file_path}"

    def upload(self, file_path: Path) -> UploadResult:
        """Upload file to Shotstack.

        Args:
            file_path: Path to local video file

        Returns:
            UploadResult with file_id and status
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return UploadResult(success=False, error=f"File not found: {file_path}")

        # Step 1: Get signed URL
        file_id, signed_url, error = self._get_signed_url()
        if error or not file_id or not signed_url:
            return UploadResult(
                success=False, error=error or "Failed to get signed URL"
            )

        # Step 2: Upload file
        error = self._upload_file(file_path, signed_url)
        if error:
            return UploadResult(success=False, error=error)

        # Wait for file to be processed and get source URL
        source_url = self._wait_for_file_ready(file_id)
        if not source_url:
            return UploadResult(
                success=False,
                error="Failed to get source URL from API (file processing timeout)",
            )

        return UploadResult(success=True, file_id=file_id, url=source_url)

    def _wait_for_file_ready(
        self, file_id: str, timeout: int = 60, poll_interval: int = 2
    ) -> Optional[str]:
        """Wait for file to be processed and ready.

        Args:
            file_id: The file ID from upload
            timeout: Maximum wait time in seconds
            poll_interval: Seconds between checks

        Returns:
            Source URL when ready, None if failed or timeout
        """
        url = f"{self.base_url}/sources/{file_id}"
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                status = data["data"]["attributes"].get("status")

                if status == "ready":
                    return data["data"]["attributes"]["source"]
                elif status == "failed":
                    return None

                # Still processing, wait
                time.sleep(poll_interval)

            except (requests.exceptions.RequestException, KeyError, ValueError):
                return None

        return None  # Timeout

    def upload_multiple(self, file_paths: list[Path]) -> list[UploadResult]:
        """Upload multiple files.

        Args:
            file_paths: List of paths to video files

        Returns:
            List of UploadResult objects
        """
        results = []
        for path in file_paths:
            result = self.upload(path)
            results.append(result)
        return results
