import time
import os
import argparse
from src.config_loader import load_config
from src.extractor import extract_text, UnsupportedFormatError
from src.chunker import chunk_text
from src.checkpoint import Checkpoint
from src.lightrag_client import LightRAGClient, LightRAGError


def get_all_files(config: dict) -> list:
    files = []
    for source_cfg in config["sources"].values():
        path = source_cfg["path"]
        extensions = [e.lower() for e in source_cfg.get("extensions", [])]
        for root, _, filenames in os.walk(path):
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if not extensions or ext in extensions:
                    files.append(os.path.join(root, fname))
    return files


def run_watcher(config_path: str, interval: int = 60):
    config = load_config(config_path)
    client = LightRAGClient(
        host=config["lightrag"]["host"],
        port=config["lightrag"]["port"]
    )
    checkpoint = Checkpoint(config["checkpoint_file"])
    chunk_size = config["chunking"]["chunk_size"]
    overlap = config["chunking"]["overlap"]

    print(f"Watcher iniciado. Verificando a cada {interval}s. Ctrl+C para parar.")
    while True:
        for file_path in get_all_files(config):
            try:
                mtime = os.path.getmtime(file_path)
            except FileNotFoundError:
                continue

            if checkpoint.is_processed(file_path, mtime):
                continue

            try:
                text = extract_text(file_path)
                if not text.strip():
                    checkpoint.mark_processed(file_path, mtime)
                    continue
                chunks = chunk_text(text, file_path, chunk_size, overlap)
                for chunk in chunks:
                    desc = f"{chunk['source']} [{chunk['chunk_index']+1}/{chunk['total_chunks']}]"
                    client.insert_text(chunk["text"], description=desc)
                checkpoint.mark_processed(file_path, mtime)
                checkpoint.save()
                print(f"[watcher] Indexed: {file_path}")
            except (UnsupportedFormatError, LightRAGError, Exception):
                pass

        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch for new/modified files and index them")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between scans")
    args = parser.parse_args()
    run_watcher(args.config, args.interval)
