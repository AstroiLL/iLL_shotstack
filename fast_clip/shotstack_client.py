"""Shotstack client for Fast-Clip - handles rendering API."""

import requests
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class RenderResult:
    """Result of video render."""

    success: bool
    render_id: Optional[str] = None
    status: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None


class ShotstackClient:
    """Client for Shotstack Edit API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.shotstack.io/edit/stage",
        poll_interval: int = 5,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.poll_interval = poll_interval
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def render(self, edit_data: dict) -> RenderResult:
        """Submit video for rendering.

        Args:
            edit_data: Shotstack edit data (timeline + output)

        Returns:
            RenderResult with render_id
        """
        url = f"{self.base_url}/render"

        try:
            response = requests.post(url, headers=self.headers, json=edit_data)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                render_id = data["response"]["id"]
                return RenderResult(success=True, render_id=render_id, status="queued")
            else:
                return RenderResult(
                    success=False,
                    error=f"API error: {data.get('message', 'Unknown error')}",
                )

        except requests.exceptions.RequestException as e:
            return RenderResult(success=False, error=f"Request failed: {e}")
        except (KeyError, ValueError) as e:
            return RenderResult(success=False, error=f"Invalid response format: {e}")

    def get_status(self, render_id: str) -> RenderResult:
        """Check render status.

        Args:
            render_id: Render job ID

        Returns:
            RenderResult with current status
        """
        url = f"{self.base_url}/render/{render_id}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                response_data = data["response"]
                status = response_data.get("status")
                url = response_data.get("url")

                return RenderResult(
                    success=(status == "done"),
                    render_id=render_id,
                    status=status,
                    url=url,
                    error=response_data.get("error") if status == "failed" else None,
                )
            else:
                return RenderResult(
                    success=False,
                    render_id=render_id,
                    error=f"API error: {data.get('message', 'Unknown error')}",
                )

        except requests.exceptions.RequestException as e:
            return RenderResult(
                success=False, render_id=render_id, error=f"Request failed: {e}"
            )

    def wait_for_render(
        self, render_id: str, timeout: int = 300, callback=None
    ) -> RenderResult:
        """Wait for render to complete.

        Args:
            render_id: Render job ID
            timeout: Maximum wait time in seconds
            callback: Optional callback function(status, url)

        Returns:
            RenderResult with final status
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.get_status(render_id)

            if callback:
                callback(result.status, result.url)

            if result.status == "done":
                return result
            elif result.status == "failed":
                return result

            time.sleep(self.poll_interval)

        return RenderResult(
            success=False,
            render_id=render_id,
            status="timeout",
            error=f"Render timeout after {timeout} seconds",
        )

    def download(self, url: str, output_path: Path) -> bool:
        """Download rendered video.

        Args:
            url: Video URL
            output_path: Where to save the file

        Returns:
            True if successful
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True

        except requests.exceptions.RequestException:
            return False
