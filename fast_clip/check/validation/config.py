"""
Configuration loader for validation settings.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import tomli

    HAS_TOML = True
except ImportError:
    HAS_TOML = False


class ValidationConfig:
    """Configuration for validation behavior."""

    def __init__(
        self,
        strict_mode: bool = False,
        max_workers: Optional[int] = None,
        parallel_threshold: int = 5,
        skip_file_validation: bool = False,
        enable_cache: bool = True,
        verbose: bool = False,
    ):
        self.strict_mode = strict_mode
        self.max_workers = max_workers
        self.parallel_threshold = parallel_threshold
        self.skip_file_validation = skip_file_validation
        self.enable_cache = enable_cache
        self.verbose = verbose

    @classmethod
    def from_file(cls, config_path: Path) -> "ValidationConfig":
        """Load configuration from TOML file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if not HAS_TOML:
            return cls()

        with open(config_path, "rb") as f:
            config_data = tomli.load(f)

        validation_config = config_data.get("validation", {})
        return cls(
            strict_mode=validation_config.get("strict_mode", False),
            max_workers=validation_config.get("max_workers"),
            parallel_threshold=validation_config.get("parallel_threshold", 5),
            skip_file_validation=validation_config.get("skip_file_validation", False),
            enable_cache=validation_config.get("enable_cache", True),
            verbose=validation_config.get("verbose", False),
        )

    @classmethod
    def find_config_file(cls, start_dir: Optional[Path] = None) -> Optional[Path]:
        """Find validation configuration file in directory hierarchy."""
        if start_dir is None:
            start_dir = Path.cwd()

        config_files = [
            ".validation.toml",
            "validation.toml",
            ".pyproject.toml",
        ]

        current_dir = start_dir
        while True:
            for config_file in config_files:
                config_path = current_dir / config_file
                if config_path.exists():
                    return config_path

            parent = current_dir.parent
            if parent == current_dir:
                break
            current_dir = parent

        return None

    @classmethod
    def from_env(cls) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        if "VALIDATION_STRICT_MODE" in os.environ:
            config["strict_mode"] = (
                os.environ["VALIDATION_STRICT_MODE"].lower() == "true"
            )
        if "VALIDATION_MAX_WORKERS" in os.environ:
            config["max_workers"] = int(os.environ["VALIDATION_MAX_WORKERS"])
        if "VALIDATION_PARALLEL_THRESHOLD" in os.environ:
            config["parallel_threshold"] = int(
                os.environ["VALIDATION_PARALLEL_THRESHOLD"]
            )
        if "VALIDATION_SKIP_FILE_VALIDATION" in os.environ:
            config["skip_file_validation"] = (
                os.environ["VALIDATION_SKIP_FILE_VALIDATION"].lower() == "true"
            )
        if "VALIDATION_ENABLE_CACHE" in os.environ:
            config["enable_cache"] = (
                os.environ["VALIDATION_ENABLE_CACHE"].lower() == "true"
            )
        if "VALIDATION_VERBOSE" in os.environ:
            config["verbose"] = os.environ["VALIDATION_VERBOSE"].lower() == "true"
        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "strict_mode": self.strict_mode,
            "max_workers": self.max_workers,
            "parallel_threshold": self.parallel_threshold,
            "skip_file_validation": self.skip_file_validation,
            "enable_cache": self.enable_cache,
            "verbose": self.verbose,
        }
