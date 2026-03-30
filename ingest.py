import os
import sys
import argparse
from local_rag.config_loader import load_config
from local_rag.extractor import extract_text, UnsupportedFormatError
from local_rag.chunker import chunk_text
from local_rag.checkpoint import Checkpoint
from local_rag.lightrag_client import LightRAGClient, LightRAGError


def discover_files(source_cfg: dict) -> list:
    path = source_cfg["path"]
    extensions = [e.lower() for e in source_cfg.get("extensions", [])]
    files = []
    for root, _, filenames in os.walk(path):
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if not extensions or ext in extensions:
                files.append(os.path.join(root, fname))
    return files


def run_ingest(config_path: str):
    config = load_config(config_path)
    client = LightRAGClient(
        host=config["lightrag"]["host"],
        port=config["lightrag"]["port"]
    )

    if not client.health_check():
        print("ERROR: LightRAG server not responding at "
              f"{config['lightrag']['host']}:{config['lightrag']['port']}")
        print("Start the server first with:")
        print("  lightrag-server --host 0.0.0.0 --port 9621 \\")
        print("    --llm-provider ollama --llm-model llama3.2:3b \\")
        print("    --embedding-provider ollama --embedding-model nomic-embed-text \\")
        print(f"    --working-dir {config['lightrag']['working_dir']}")
        sys.exit(1)

    checkpoint = Checkpoint(config["checkpoint_file"])
    chunk_size = config["chunking"]["chunk_size"]
    overlap = config["chunking"]["overlap"]

    total_files = 0
    skipped = 0
    indexed = 0
    errors = 0

    for source_name, source_cfg in config["sources"].items():
        print(f"\n[{source_name}] Scanning {source_cfg['path']} ...")
        files = discover_files(source_cfg)
        print(f"  Found {len(files)} files")

        for file_path in files:
            mtime = os.path.getmtime(file_path)
            total_files += 1

            if checkpoint.is_processed(file_path, mtime):
                skipped += 1
                continue

            try:
                text = extract_text(file_path)
                if not text.strip():
                    checkpoint.mark_processed(file_path, mtime)
                    continue

                chunks = chunk_text(text, file_path, chunk_size, overlap)
                for chunk in chunks:
                    description = f"{chunk['source']} [{chunk['chunk_index']+1}/{chunk['total_chunks']}]"
                    client.insert_text(chunk["text"], description=description)

                checkpoint.mark_processed(file_path, mtime)
                checkpoint.save()
                indexed += 1
                print(f"  + {file_path} ({len(chunks)} chunks)")

            except UnsupportedFormatError:
                pass
            except LightRAGError as e:
                print(f"  ERROR indexing {file_path}: {e}")
                errors += 1
            except Exception as e:
                print(f"  ERROR processing {file_path}: {e}")
                errors += 1

    print(f"\nDone. {indexed} indexed, {skipped} skipped, {errors} errors (of {total_files} total files)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index documents into LightRAG")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()
    run_ingest(args.config)
