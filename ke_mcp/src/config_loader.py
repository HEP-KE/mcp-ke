"""Configuration loading utility"""
from pathlib import Path
import yaml

_CONFIG_CACHE = None


def get_config_path() -> Path:
    """Get path to config.yaml"""
    return Path(__file__).parent.parent.parent / "config.yaml"


def load_config() -> dict:
    """Load and cache config.yaml"""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        with open(get_config_path()) as f:
            _CONFIG_CACHE = yaml.safe_load(f)
    return _CONFIG_CACHE


def get_tool_config(tool_name: str) -> dict | None:
    """Get config for specific tool by tool_name"""
    config = load_config()
    for cfg in config["tools"].values():
        if cfg["tool_name"] == tool_name:
            return cfg
    return None


def get_all_tools() -> dict:
    """Get all tool configurations"""
    return load_config()["tools"]


def get_server_config() -> dict:
    """Get server configuration"""
    return load_config()["server"]
