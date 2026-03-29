import pytest
import yaml
from src.config_loader import load_config, ConfigError

VALID_CONFIG = {
    "sources": {
        "obsidian": {"path": "/tmp/vault", "include_all": True, "extensions": [".md"]},
        "zotero": {"path": "/tmp/zotero", "include_all": True, "extensions": [".pdf", ".bib"]}
    },
    "lightrag": {"host": "localhost", "port": 9621, "working_dir": "/tmp/storage"},
    "ollama": {"llm_model": "llama3.2:3b", "embedding_model": "nomic-embed-text"},
    "chunking": {"chunk_size": 2000, "overlap": 200},
    "checkpoint_file": "/tmp/checkpoint.json"
}

def write_config(tmp_path, data):
    path = tmp_path / "config.yaml"
    path.write_text(yaml.dump(data))
    return str(path)

def test_load_valid_config(tmp_path):
    path = write_config(tmp_path, VALID_CONFIG)
    config = load_config(path)
    assert config["lightrag"]["port"] == 9621
    assert config["ollama"]["llm_model"] == "llama3.2:3b"
    assert ".md" in config["sources"]["obsidian"]["extensions"]

def test_missing_lightrag_raises(tmp_path):
    data = {k: v for k, v in VALID_CONFIG.items() if k != "lightrag"}
    path = write_config(tmp_path, data)
    with pytest.raises(ConfigError, match="lightrag"):
        load_config(path)

def test_missing_file_raises():
    with pytest.raises(ConfigError, match="not found"):
        load_config("/nonexistent/config.yaml")
