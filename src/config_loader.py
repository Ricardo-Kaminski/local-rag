import yaml
import os


class ConfigError(Exception):
    pass


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise ConfigError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    for required in ["sources", "lightrag", "ollama", "chunking", "checkpoint_file"]:
        if required not in config:
            raise ConfigError(f"Missing required config section: '{required}'")
    return config
