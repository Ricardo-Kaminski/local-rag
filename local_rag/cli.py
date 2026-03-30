"""CLI unificado para o local-rag stack."""

import asyncio
import os
import subprocess
import sys
import time

import click

from local_rag.config_loader import load_config

DEFAULT_CONFIG = "config.yaml"


@click.group()
@click.version_option()
def main():
    """local-rag — 100% local RAG stack for Obsidian, Zotero, and Claude Code."""


@main.command()
@click.option("--config", default=DEFAULT_CONFIG, show_default=True, help="Path to config.yaml")
def ingest(config):
    """Run ingestion pipeline once — index all new/modified documents."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ingest import run_ingest
    run_ingest(config)


@main.command()
@click.option("--config", default=DEFAULT_CONFIG, show_default=True, help="Path to config.yaml")
@click.option("--interval", default=60, show_default=True, help="Polling interval in seconds")
def watch(config, interval):
    """Start watcher daemon — continuously index new documents."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from watcher import run_watcher
    run_watcher(config, interval)


@main.command("mcp")
@click.option("--config", default=DEFAULT_CONFIG, show_default=True, help="Path to config.yaml")
def mcp_serve(config):
    """Start MCP server for Claude Code integration."""
    os.environ["LOCAL_RAG_CONFIG"] = os.path.abspath(config)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import mcp_server
    asyncio.run(mcp_server.main())


@main.command()
@click.option("--config", default=DEFAULT_CONFIG, show_default=True, help="Path to config.yaml")
@click.option("--no-watcher", is_flag=True, default=False, help="Start LightRAG only, skip watcher")
def start(config, no_watcher):
    """Start LightRAG server and (optionally) watcher daemon."""
    cfg = load_config(config)
    lightrag_cfg = cfg["lightrag"]
    ollama_cfg = cfg.get("ollama", {})
    llm_cfg = cfg.get("llm", {})

    provider = llm_cfg.get("provider", "ollama")
    working_dir = lightrag_cfg["working_dir"]
    os.makedirs(working_dir, exist_ok=True)

    cmd = [
        "lightrag-server",
        "--host", "0.0.0.0",
        "--port", str(lightrag_cfg.get("port", 9621)),
        "--working-dir", working_dir,
        "--embedding-binding", "ollama",
        "--embedding-model", ollama_cfg.get("embedding_model", "nomic-embed-text"),
    ]

    if provider == "claude":
        api_key = llm_cfg.get("api_key") or os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            click.echo(
                "ERROR: Claude provider requires ANTHROPIC_API_KEY env var or llm.api_key in config.",
                err=True,
            )
            sys.exit(1)
        cmd += [
            "--llm-binding", "openai",
            "--llm-model", llm_cfg.get("model", "claude-opus-4-6"),
            "--llm-base-url", "https://api.anthropic.com/v1",
            "--llm-api-key", api_key,
        ]
    else:
        cmd += [
            "--llm-binding", "ollama",
            "--llm-model", ollama_cfg.get("llm_model", "qwen2.5:14b"),
        ]

    click.echo(f"[1/2] Starting LightRAG server (provider={provider})...")
    lightrag_proc = subprocess.Popen(cmd)
    time.sleep(5)

    if not no_watcher:
        click.echo("[2/2] Starting watcher daemon...")
        watcher_proc = subprocess.Popen(
            [sys.executable, "-m", "local_rag.cli", "watch", "--config", config]
        )
    else:
        watcher_proc = None

    click.echo("\nStack running. Press Ctrl+C to stop.")
    try:
        lightrag_proc.wait()
    except KeyboardInterrupt:
        click.echo("\nStopping...")
        lightrag_proc.terminate()
        if watcher_proc:
            watcher_proc.terminate()
