# Guide: Obsidian + local-rag

Query your Obsidian vault with natural language from Claude Code.

## Prerequisites

- Obsidian vault on your local machine
- [local-rag installed](../../README.md#quickstart)

## Configuration

In `config.yaml`, set the Obsidian source:

```yaml
sources:
  obsidian:
    path: "/path/to/your/vault"   # absolute path to your Obsidian vault folder
    include_all: true
    extensions: [".md"]
```

## Initial Ingestion

Run the ingestion pipeline to index all your notes:

```bash
conda activate local-rag
python ingest.py
```

For a large vault (1000+ notes) this may take 30–60 minutes on first run.
Subsequent runs only process new or modified files (checkpoint system).

## Continuous Sync

Start the watcher daemon to automatically index new notes:

```bash
python watcher.py
```

Or use the startup script: `start-rag.bat` (Windows) / `start-rag.sh` (Linux/macOS)

## Querying from Claude Code

Once the stack is running, in Claude Code:

```
query_rag("What are my notes on quantum cognition?")
query_rag("Summarize everything I've written about VSM", mode="global")
query_rag("Find connections between Stafford Beer and complexity theory", mode="hybrid")
```

## Tips

- Use `mode="global"` for broad thematic questions across your whole vault
- Use `mode="local"` for specific facts or quotes
- Use `mode="hybrid"` (default) when unsure — it combines both approaches
- Tag your notes consistently in Obsidian; the RAG preserves frontmatter metadata
