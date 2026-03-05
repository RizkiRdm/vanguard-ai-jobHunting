import yaml
import time
from pathlib import Path
from typing import Dict, Any
from core.custom_logging import logger


class ConfigManager:
    _instance = None
    _last_loaded = 0

    def __new__(cls):
        """Singleton pattern to ensure global access to the same config."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.config_path = Path("config/jobsites.yaml")
        self._config_cache = {}
        self.log = logger.bind(service="config_manager")
        self._load_config()
        self._initialized = True

    def _load_config(self):
        """Loads YAML file with error handling."""
        if not self.config_path.exists():
            self.log.error("config_file_missing", path=str(self.config_path))
            return

        try:
            with open(self.config_path, "r") as f:
                self._config_cache = yaml.safe_load(f) or {}
            self._last_loaded = time.time()
            self.log.info("config_loaded_successfully")
        except Exception as e:
            self.log.error("config_parse_error", error=str(e))

    def _maybe_reload(self):
        """Reloads config if the file was modified (simple TTL 60s)."""
        # Cek setiap 60 detik apakah ada perubahan
        if time.time() - self._last_loaded > 60:
            self._load_config()

    def get_site_config(self, site_name: str) -> Dict[str, Any]:
        """
        Returns site-specific config with default fallback values
        to prevent KeyError in Orchestrator/Scraper.
        """
        self._maybe_reload()

        site_data = self._config_cache.get(site_name)
        if not site_data:
            self.log.error("site_not_supported", site=site_name)
            raise ValueError(f"Configuration for {site_name} is missing in YAML.")

        # Default Schema Fallback
        defaults = {
            "selectors": {},
            "settings": {
                "typing_delay_range": [50, 150],
                "max_steps": 10,
                "wait_after_page_load": 2000,
            },
        }

        # Merge user config with defaults
        for key, default_val in defaults.items():
            if key not in site_data:
                site_data[key] = default_val
            elif isinstance(default_val, dict):
                # Deep merge for nested settings
                site_data[key] = {**default_val, **site_data[key]}

        return site_data


# Global instance for easy import
site_config = ConfigManager()
