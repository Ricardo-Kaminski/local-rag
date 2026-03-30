# local-rag

> 100% local RAG for Obsidian, Zotero, and Claude Code — powered by LightRAG + Ollama

[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![LightRAG](https://img.shields.io/badge/LightRAG-HKUDS-orange)](https://github.com/HKUDS/LightRAG)
[![Ollama](https://img.shields.io/badge/Ollama-compatible-green)](https://ollama.com)
[![MCP](https://img.shields.io/badge/MCP-Claude_Code-purple)](https://modelcontextprotocol.io)

A complete, **privacy-first** RAG stack that runs entirely on your machine.
No API keys. No cloud. No data leaves your computer.

---

## Why local-rag?

| | local-rag | Cloud RAG |
|---|---|---|
| Privacy | Your data stays on your machine | Sent to third-party servers |
| Cost | Free after hardware | Per-token API costs |
| Offline | Works without internet | Requires connectivity |
| Latency | Local inference | Network round-trips |
| Customization | Any model via Ollama | Limited to provider models |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  YOUR DOCUMENTS                      │
│   Obsidian vault (.md)  │  Zotero storage (.pdf)    │
└──────────────┬──────────────────────────────────────┘
               │  ingestion pipeline (Python)
               ▼
┌─────────────────────────────────────────────────────┐
│                 LIGHTRAG SERVER                      │
│  • Knowledge graph (entities + relations)            │
│  • Vector index (NanoVectorDB)                       │
│  • LLM: Ollama → qwen2.5:14b                        │
│  • Embeddings: Ollama → nomic-embed-text             │
│  • REST API at http://localhost:9621                 │
└──────────────┬──────────────────────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐  ┌──────────────┐
│ Claude Code │  │   Obsidian   │
│  (MCP tool) │  │Smart Connect.│
└─────────────┘  └──────────────┘
```

---

## Quickstart

### 1. Install Ollama and pull models

```bash
# Download Ollama from https://ollama.com
ollama pull qwen2.5:14b        # ~8GB — the LLM
ollama pull nomic-embed-text   # ~300MB — embeddings
```

### 2. Install LightRAG

```bash
pip install "lightrag-hku[api]"
```

### 3. Clone and configure

```bash
git clone https://github.com/Ricardo-Kaminski/local-rag
cd local-rag
cp config.example.yaml config.yaml
# Edit config.yaml with your paths
```

### 4. Start the stack

**Windows:**
```batch
start-rag.bat
```

**Linux/macOS:**
```bash
./start-rag.sh
```

### 5. Run initial ingestion

```bash
conda activate local-rag
python ingest.py
```

### 6. Configure Claude Code MCP

Add to your Claude Code `settings.json` (`~/.claude/settings.json`):

```json
"mcpServers": {
  "lightrag": {
    "command": "python",
    "args": ["C:/path/to/local-rag/mcp_server.py"]
  }
}
```

Now use `query_rag`, `insert_document`, and `rag_health` directly in Claude Code.

---

## Install via pip

```bash
pip install local-rag
```

After installation, use the `local-rag` CLI:

```bash
local-rag ingest          # index all documents once
local-rag watch           # continuous indexing daemon
local-rag start           # start LightRAG server + watcher
local-rag mcp             # start MCP server (for testing)
```

Configure Claude Code to use the MCP server (add to `~/.claude/settings.json`):

```json
"mcpServers": {
  "lightrag": {
    "command": "local-rag",
    "args": ["mcp"]
  }
}
```

## Claude Code Plugin

Install directly from Claude Code:

```
/plugin install local-rag
```

## MCP Tools (7 total)

| Tool | Description |
|---|---|
| `query_rag(question, mode?)` | Query the knowledge base. Modes: `local`, `global`, `hybrid` (default) |
| `insert_document(path)` | Index a specific file by path |
| `rag_health()` | Check if LightRAG server is running |
| `list_sources()` | List configured sources with file counts |
| `get_indexed_documents(limit?)` | List documents already indexed |
| `delete_document(doc_id)` | Remove a document from the knowledge base |
| `get_graph_labels()` | List entity types in the knowledge graph |

## Using Claude API as LLM (optional)

Use Claude instead of Ollama for RAG responses. In `config.yaml`:

```yaml
llm:
  provider: "claude"
  model: "claude-opus-4-6"
  api_key: ""   # or set ANTHROPIC_API_KEY env var
```

> Note: Ollama is still required for embeddings (nomic-embed-text). Only the response LLM can be replaced with Claude.

---

## Guides by Use Case

- [Obsidian users](docs/guides/obsidian.md) — query your personal knowledge base
- [Zotero users](docs/guides/zotero.md) — search your academic PDF library
- [Generic documents](docs/guides/generic.md) — any folder of PDFs, Word files, or Markdown

---

## Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| GPU VRAM | 0 (CPU only, slow) | 8 GB (qwen2.5:7b) / 12 GB (qwen2.5:14b) |
| Disk | 10 GB | 20 GB |

> Tested on Windows 11 with RTX 3060 12GB. CPU inference works but is significantly slower.

---

## Just want the MCP server?

If you already have a LightRAG instance running, install the standalone MCP package:

```bash
pip install lightrag-mcp
```

See [lightrag-mcp](https://github.com/Ricardo-Kaminski/lightrag-mcp) for details.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and feature requests welcome via GitHub Issues.

## License

MIT — see [LICENSE](LICENSE)
