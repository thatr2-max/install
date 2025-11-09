"""Configuration loader and validator for AI Mod Generator."""

import json
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager for the mod generator."""

    def __init__(self, config_path: str = None):
        """Initialize configuration from file.

        Args:
            config_path: Path to config.json. If None, uses default location.
        """
        if config_path is None:
            # Default to config.json in project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config.json"

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}"
            )

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _validate_config(self):
        """Validate configuration and API key."""
        required_fields = [
            "openrouter_api_key",
            "model",
            "base_url",
            "max_iterations",
            "supported_games"
        ]

        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required config field: {field}")

        # Validate API key
        if self.config["openrouter_api_key"] == "PLACEHOLDER":
            raise ValueError(
                "API key not configured. Please set 'openrouter_api_key' in config.json"
            )

        # Check if API key looks valid (basic check)
        api_key = self.config["openrouter_api_key"]
        if not api_key or len(api_key) < 10:
            raise ValueError("Invalid API key format")

    def get(self, key: str, default=None):
        """Get configuration value by key."""
        return self.config.get(key, default)

    def __getitem__(self, key: str):
        """Get configuration value using dict-like syntax."""
        return self.config[key]

    @property
    def api_key(self) -> str:
        """Get OpenRouter API key."""
        return self.config["openrouter_api_key"]

    @property
    def model(self) -> str:
        """Get model name."""
        return self.config["model"]

    @property
    def base_url(self) -> str:
        """Get API base URL."""
        return self.config["base_url"]

    @property
    def max_iterations(self) -> int:
        """Get maximum iterations for agent."""
        return self.config["max_iterations"]

    @property
    def supported_games(self) -> list:
        """Get list of supported games."""
        return self.config["supported_games"]

    @property
    def cost_tracking(self) -> Dict[str, float]:
        """Get cost tracking configuration."""
        return self.config.get("cost_tracking", {})
