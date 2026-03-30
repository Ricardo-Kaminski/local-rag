# GitHub Publication & MCP Distribution — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publicar `local-rag` como template open-source no GitHub e criar `lightrag-mcp` como pacote pip distribuível no MCP Registry e Claude Plugin marketplace.

**Architecture:** Dois repositórios independentes. `local-rag` é o template de referência (clone-e-use). `lightrag-mcp` é um pacote pip leve que expõe qualquer servidor LightRAG como MCP server via variáveis de ambiente — sem dependência em `local-rag`.

**Tech Stack:** Python 3.11+, mcp (Anthropic SDK), requests, GitHub Actions, PyPI (trusted publishing via OIDC), gh CLI

---

## Mapa de Arquivos

### Fase 1 — `local-rag` (C:/Workspace/pessoal/local-rag/)

| Ação | Arquivo |
|---|---|
| Criar | `README.md` |
| Criar | `LICENSE` |
| Criar | `CONTRIBUTING.md` |
| Criar | `config.example.yaml` |
| Criar | `pyproject.toml` |
| Criar | `start-rag.sh` |
| Criar | `docs/guides/obsidian.md` |
| Criar | `docs/guides/zotero.md` |
| Criar | `docs/guides/generic.md` |
| Criar | `.github/ISSUE_TEMPLATE/bug_report.md` |
| Criar | `.github/ISSUE_TEMPLATE/feature_request.md` |
| Modificar | `.gitignore` |
| Publicar | GitHub repo público |

### Fase 2 — `lightrag-mcp` (C:/Workspace/pessoal/lightrag-mcp/)

| Ação | Arquivo |
|---|---|
| Criar | `README.md` |
| Criar | `LICENSE` |
| Criar | `pyproject.toml` |
| Criar | `lightrag_mcp/__init__.py` |
| Criar | `lightrag_mcp/server.py` |
| Criar | `.github/workflows/publish.yml` |
| Publicar | GitHub repo público + tag v0.1.0 |

---

## FASE 1: Polimento do `local-rag`

---

### Task 1: Atualizar .gitignore e criar config.example.yaml

**Files:**
- Modify: `.gitignore`
- Create: `config.example.yaml`

- [ ] **Step 1: Atualizar .gitignore**

Substituir conteúdo de `.gitignore` por:

```gitignore
# Configuração pessoal (copie config.example.yaml → config.yaml e adapte)
config.yaml

# Storage do LightRAG (grafo + vetores — pode ser gigabytes)
data/
D:/local-rag-storage/

# Checkpoint (rastreia arquivos já processados)
*.json

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
.env

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 2: Criar config.example.yaml**

```yaml
# Copie este arquivo para config.yaml e ajuste os caminhos para sua máquina.
# config.yaml está no .gitignore — suas configurações pessoais nunca serão commitadas.

sources:
  # Exemplo: Obsidian vault
  obsidian:
    path: "/path/to/your/obsidian/vault"   # ex: D:/Obsidian/vault/
    include_all: true
    extensions: [".md"]

  # Exemplo: Zotero storage
  zotero:
    path: "/path/to/your/zotero/storage"   # ex: D:/_bib_Zotero/storage/
    include_all: true
    extensions: [".pdf"]

  # Adicione quantas fontes quiser seguindo o mesmo padrão

lightrag:
  host: "localhost"
  port: 9621
  working_dir: "/path/to/lightrag/storage"  # onde o grafo e vetores serão salvos

ollama:
  llm_model: "qwen2.5:14b"          # requer ~8GB VRAM. Alternativa: llama3.2:3b
  embedding_model: "nomic-embed-text"

chunking:
  chunk_size: 2000   # tokens por chunk
  overlap: 200       # tokens de sobreposição entre chunks

checkpoint_file: "/path/to/local-rag/data/checkpoint.json"
```

- [ ] **Step 3: Verificar que config.yaml pessoal não está staged**

```bash
cd C:/Workspace/pessoal/local-rag
git status
```

Esperado: `config.yaml` deve aparecer em "Changes not staged" ou "Untracked", nunca em "Changes to be committed".

- [ ] **Step 4: Commit**

```bash
git add .gitignore config.example.yaml
git commit -m "chore: add config.example.yaml template and update .gitignore"
```

---

### Task 2: Criar pyproject.toml

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Criar pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "local-rag"
version = "0.1.0"
description = "100% local RAG for Obsidian, Zotero, and Claude Code — powered by LightRAG + Ollama"
readme = "README.md"
license = { file = "LICENSE" }
requires-python = ">=3.11"
dependencies = [
    "lightrag-hku[api]",
    "pymupdf",
    "python-docx",
    "openpyxl",
    "bibtexparser",
    "pyyaml",
    "requests",
    "mcp",
]

[project.urls]
Homepage = "https://github.com/RicardoKaminski/local-rag"
Repository = "https://github.com/RicardoKaminski/local-rag"
Issues = "https://github.com/RicardoKaminski/local-rag/issues"

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

- [ ] **Step 2: Verificar instalação**

```bash
cd C:/Workspace/pessoal/local-rag
conda activate local-rag
pip install -e . --dry-run
```

Esperado: lista de dependências sem erros.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add pyproject.toml for pip-based installation"
```

---

### Task 3: Criar LICENSE e CONTRIBUTING.md

**Files:**
- Create: `LICENSE`
- Create: `CONTRIBUTING.md`

- [ ] **Step 1: Criar LICENSE (MIT)**

```text
MIT License

Copyright (c) 2026 Ricardo Kaminski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Criar CONTRIBUTING.md**

```markdown
# Contributing

Contributions are welcome! Here's how:

## Bug Reports

Open an issue using the Bug Report template. Include:
- Your OS and Python version
- The exact error message
- What you were trying to do

## Feature Requests

Open an issue using the Feature Request template before writing any code.
This ensures we align on the direction before you invest time.

## Pull Requests

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make your changes with tests where applicable
4. Run existing tests: `pytest`
5. Commit with a clear message
6. Open a PR against `main`

## Scope

This project is intentionally focused on local, privacy-first RAG.
PRs that add cloud dependencies or require external API keys are out of scope.
```

- [ ] **Step 3: Commit**

```bash
git add LICENSE CONTRIBUTING.md
git commit -m "chore: add MIT license and contributing guide"
```

---

### Task 4: Criar start-rag.sh (Linux/macOS)

**Files:**
- Create: `start-rag.sh`

- [ ] **Step 1: Criar start-rag.sh**

```bash
#!/usr/bin/env bash
set -e

echo "============================================"
echo "  Local RAG Stack - Starting services"
echo "============================================"
echo ""

# Check if Ollama is running
echo "[1/3] Checking Ollama..."
if pgrep -x "ollama" > /dev/null 2>&1; then
    echo "      Ollama is already running."
else
    echo "      Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Start LightRAG Server
echo "[2/3] Starting LightRAG Server (port 9621)..."
WORKING_DIR="${LIGHTRAG_WORKING_DIR:-./data/lightrag_storage}"
LLM_MODEL="${LIGHTRAG_LLM_MODEL:-qwen2.5:14b}"
EMBED_MODEL="${LIGHTRAG_EMBED_MODEL:-nomic-embed-text}"

conda run -n local-rag lightrag-server \
    --working-dir "$WORKING_DIR" \
    --llm-binding ollama \
    --llm-model "$LLM_MODEL" \
    --embedding-binding ollama \
    --embedding-model "$EMBED_MODEL" \
    --port 9621 \
    --host 0.0.0.0 &

sleep 5

# Start Watcher
echo "[3/3] Starting Watcher (ingestion daemon)..."
conda run -n local-rag python watcher.py &

echo ""
echo "============================================"
echo "  Stack started!"
echo "  - LightRAG: http://localhost:9621"
echo "  - Watcher: monitoring configured sources"
echo "============================================"
echo ""
echo "Press Ctrl+C to stop all services."

wait
```

- [ ] **Step 2: Tornar executável**

```bash
chmod +x start-rag.sh
```

- [ ] **Step 3: Commit**

```bash
git add start-rag.sh
git commit -m "feat: add start-rag.sh for Linux/macOS"
```

---

### Task 5: Criar guias por persona

**Files:**
- Create: `docs/guides/obsidian.md`
- Create: `docs/guides/zotero.md`
- Create: `docs/guides/generic.md`

- [ ] **Step 1: Criar docs/guides/obsidian.md**

```markdown
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
```

- [ ] **Step 2: Criar docs/guides/zotero.md**

```markdown
# Guide: Zotero + local-rag

Query your Zotero PDF library and BibTeX references from Claude Code.

## Prerequisites

- Zotero installed with your library synced locally
- [local-rag installed](../../README.md#quickstart)

## Find Your Zotero Storage Path

In Zotero: Edit → Preferences → Advanced → Files and Folders → Data Directory Location.

Your PDFs are in `<Data Directory>/storage/`.

## Configuration

```yaml
sources:
  zotero:
    path: "/path/to/zotero/storage"   # the storage/ subfolder
    include_all: true
    extensions: [".pdf"]
```

## Initial Ingestion

```bash
conda activate local-rag
python ingest.py
```

PDFs are extracted with PyMuPDF. Scanned PDFs (image-only) are skipped — only
digitally-created PDFs are indexed.

## Querying Academic Papers

```
query_rag("What does the literature say about self-organization in VSM?")
query_rag("Find papers about quantum cognition and decision making", mode="global")
query_rag("Which authors discuss viable system model and complexity?", mode="hybrid")
```

## Tips

- BibTeX files (`.bib`) from Zotero exports are also supported — add them as a separate source
- For large libraries (500+ PDFs), first ingestion may take several hours
- The checkpoint system ensures you only process new papers on subsequent runs
```

- [ ] **Step 3: Criar docs/guides/generic.md**

```markdown
# Guide: Generic Document Collection

Use local-rag with any folder of documents — PDFs, Word files, Markdown, Excel, or BibTeX.

## Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Markdown | `.md` | Full text extraction |
| PDF | `.pdf` | Digital PDFs only (not scanned) |
| Word | `.docx` | Text and tables |
| Excel | `.xlsx` | Cell content as text |
| BibTeX | `.bib` | Academic references |

## Configuration

Add one entry per document source in `config.yaml`:

```yaml
sources:
  my_reports:
    path: "/path/to/reports"
    include_all: true
    extensions: [".pdf", ".docx"]

  my_notes:
    path: "/path/to/notes"
    include_all: true
    extensions: [".md"]

  my_references:
    path: "/path/to/references"
    include_all: false
    extensions: [".bib"]
```

## Ingestion

```bash
conda activate local-rag
python ingest.py
```

## Watching for Changes

```bash
python watcher.py   # polls every 60 seconds by default
```

## Querying

```
query_rag("What are the main findings in Q3 reports?")
query_rag("Summarize the regulatory requirements across all documents", mode="global")
```
```

- [ ] **Step 4: Commit**

```bash
git add docs/guides/
git commit -m "docs: add persona guides for Obsidian, Zotero, and generic use cases"
```

---

### Task 6: Criar GitHub Issue Templates

**Files:**
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`

- [ ] **Step 1: Criar bug_report.md**

```markdown
---
name: Bug Report
about: Something isn't working
labels: bug
---

## Describe the Bug

A clear description of what's wrong.

## Steps to Reproduce

1. ...
2. ...

## Expected Behavior

What should happen.

## Actual Behavior

What actually happens. Include the full error message.

## Environment

- OS: [e.g. Windows 11, Ubuntu 22.04, macOS 14]
- Python version: `python --version`
- LightRAG version: `pip show lightrag-hku`
- Ollama version: `ollama --version`
- LLM model: [e.g. qwen2.5:14b]
```

- [ ] **Step 2: Criar feature_request.md**

```markdown
---
name: Feature Request
about: Suggest an improvement
labels: enhancement
---

## Problem

What problem does this solve? Who has this problem?

## Proposed Solution

What would you like to see?

## Alternatives Considered

Other approaches you thought about.

## Additional Context

Links, screenshots, or examples.
```

- [ ] **Step 3: Commit**

```bash
git add .github/
git commit -m "chore: add GitHub issue templates"
```

---

### Task 7: Criar README.md principal

**Files:**
- Create: `README.md`

- [ ] **Step 1: Criar README.md**

```markdown
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
git clone https://github.com/RicardoKaminski/local-rag
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

Add to your Claude Code `settings.json`:

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

## Guides by Use Case

- [Obsidian users](docs/guides/obsidian.md) — query your personal knowledge base
- [Zotero users](docs/guides/zotero.md) — search your academic PDF library
- [Generic documents](docs/guides/generic.md) — any folder of PDFs, Word files, or Markdown

---

## MCP Tools

| Tool | Description |
|---|---|
| `query_rag(question, mode?)` | Query the knowledge base. Modes: `local`, `global`, `hybrid` (default) |
| `insert_document(path)` | Index a specific file |
| `rag_health()` | Check if LightRAG server is running |

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

See [lightrag-mcp](https://github.com/RicardoKaminski/lightrag-mcp) for details.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and feature requests welcome via GitHub Issues.

## License

MIT — see [LICENSE](LICENSE)
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README with architecture, quickstart, and persona guides"
```

---

### Task 8: Criar repositório GitHub e publicar

**Files:** nenhum novo arquivo

- [ ] **Step 1: Criar repo no GitHub**

```bash
cd C:/Workspace/pessoal/local-rag
gh repo create local-rag \
  --public \
  --description "100% local RAG for Obsidian, Zotero, and Claude Code — LightRAG + Ollama + MCP" \
  --source . \
  --remote origin \
  --push
```

- [ ] **Step 2: Adicionar topics ao repo**

```bash
gh repo edit RicardoKaminski/local-rag \
  --add-topic rag \
  --add-topic local-llm \
  --add-topic ollama \
  --add-topic lightrag \
  --add-topic mcp \
  --add-topic claude-code \
  --add-topic obsidian \
  --add-topic zotero \
  --add-topic knowledge-graph \
  --add-topic privacy
```

- [ ] **Step 3: Verificar no browser**

```bash
gh repo view RicardoKaminski/local-rag --web
```

Confirmar: README renderizado, topics visíveis, todos os arquivos presentes.

---

## FASE 2: Criação do `lightrag-mcp`

---

### Task 9: Criar estrutura do repo lightrag-mcp

**Files:**
- Create: `C:/Workspace/pessoal/lightrag-mcp/lightrag_mcp/__init__.py`

- [ ] **Step 1: Criar diretório e inicializar git**

```bash
mkdir -p C:/Workspace/pessoal/lightrag-mcp/lightrag_mcp
mkdir -p C:/Workspace/pessoal/lightrag-mcp/.github/workflows
cd C:/Workspace/pessoal/lightrag-mcp
git init
git checkout -b main
```

- [ ] **Step 2: Criar __init__.py**

```python
"""lightrag-mcp — MCP server for LightRAG knowledge bases."""

__version__ = "0.1.0"
```

- [ ] **Step 3: Criar .gitignore**

```gitignore
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
.env
```

- [ ] **Step 4: Commit inicial**

```bash
cd C:/Workspace/pessoal/lightrag-mcp
git add .
git commit -m "chore: initial project scaffold"
```

---

### Task 10: Implementar lightrag_mcp/server.py

**Files:**
- Create: `C:/Workspace/pessoal/lightrag-mcp/lightrag_mcp/server.py`

Este é o núcleo do pacote. Configuração via variáveis de ambiente; sem dependência em `local-rag`. Usa `requests` para chamar a API REST do LightRAG diretamente.

API endpoints do LightRAG (verificados em `local-rag/src/lightrag_client.py`):
- `GET /health` → 200 OK
- `POST /query` com `{"query": str, "mode": str}` → `{"response": str}`
- `POST /documents/text` com `{"input_text": str, "description": str}` → 200 OK

- [ ] **Step 1: Criar server.py**

```python
"""MCP server that exposes a LightRAG instance as Claude Code tools."""

import asyncio
import os
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

_HOST = os.getenv("LIGHTRAG_HOST", "localhost")
_PORT = os.getenv("LIGHTRAG_PORT", "9621")
_DEFAULT_MODE = os.getenv("LIGHTRAG_DEFAULT_MODE", "hybrid")
_BASE_URL = f"http://{_HOST}:{_PORT}"

server = Server("lightrag-mcp")


class LightRAGError(Exception):
    pass


def _health() -> bool:
    try:
        r = requests.get(f"{_BASE_URL}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def _query(question: str, mode: str) -> str:
    r = requests.post(
        f"{_BASE_URL}/query",
        json={"query": question, "mode": mode},
        timeout=60,
    )
    if r.status_code != 200:
        raise LightRAGError(f"Query failed [{r.status_code}]: {r.text}")
    return r.json()["response"]


def _insert(text: str, description: str = "") -> None:
    r = requests.post(
        f"{_BASE_URL}/documents/text",
        json={"input_text": text, "description": description},
        timeout=120,
    )
    if r.status_code != 200:
        raise LightRAGError(f"Insert failed [{r.status_code}]: {r.text}")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="query_rag",
            description="Query the local RAG knowledge base (LightRAG)",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Question or topic to search",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["local", "global", "hybrid"],
                        "default": _DEFAULT_MODE,
                        "description": (
                            "local=specific chunks, "
                            "global=broad overview, "
                            "hybrid=both (recommended)"
                        ),
                    },
                },
                "required": ["question"],
            },
        ),
        types.Tool(
            name="insert_document",
            description="Insert text into the RAG knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Document text to index",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional label for this document (e.g. filename)",
                    },
                },
                "required": ["text"],
            },
        ),
        types.Tool(
            name="rag_health",
            description="Check whether the LightRAG server is reachable",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "query_rag":
        mode = arguments.get("mode", _DEFAULT_MODE)
        try:
            result = _query(arguments["question"], mode)
            return [types.TextContent(type="text", text=result)]
        except LightRAGError as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    elif name == "insert_document":
        try:
            _insert(arguments["text"], arguments.get("description", ""))
            return [types.TextContent(type="text", text="Document indexed successfully.")]
        except LightRAGError as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    elif name == "rag_health":
        status = "online" if _health() else "offline"
        return [types.TextContent(type="text", text=f"LightRAG server: {status} ({_BASE_URL})")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def _main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run() -> None:
    """Entry point for `lightrag-mcp` CLI command."""
    asyncio.run(_main())
```

- [ ] **Step 2: Testar import básico**

```bash
cd C:/Workspace/pessoal/lightrag-mcp
conda activate local-rag
python -c "from lightrag_mcp.server import run; print('OK')"
```

Esperado: `OK`

- [ ] **Step 3: Commit**

```bash
git add lightrag_mcp/
git commit -m "feat: MCP server with query_rag, insert_document, rag_health via env vars"
```

---

### Task 11: Criar pyproject.toml com entry point

**Files:**
- Create: `C:/Workspace/pessoal/lightrag-mcp/pyproject.toml`

- [ ] **Step 1: Criar pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "lightrag-mcp"
version = "0.1.0"
description = "MCP server for LightRAG — expose any LightRAG instance to Claude Code"
readme = "README.md"
license = { file = "LICENSE" }
requires-python = ">=3.11"
keywords = ["mcp", "lightrag", "rag", "claude", "llm", "local-ai"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
dependencies = [
    "mcp>=1.0.0",
    "requests>=2.31.0",
]

[project.scripts]
lightrag-mcp = "lightrag_mcp.server:run"

[project.urls]
Homepage = "https://github.com/RicardoKaminski/lightrag-mcp"
Repository = "https://github.com/RicardoKaminski/lightrag-mcp"
Issues = "https://github.com/RicardoKaminski/lightrag-mcp/issues"
Documentation = "https://github.com/RicardoKaminski/local-rag"
```

- [ ] **Step 2: Verificar entry point**

```bash
cd C:/Workspace/pessoal/lightrag-mcp
pip install -e .
lightrag-mcp --help
```

Esperado: o servidor inicia (aguarda stdin MCP) ou mostra mensagem de uso. Ctrl+C para parar.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add pyproject.toml with lightrag-mcp CLI entry point"
```

---

### Task 12: Criar LICENSE e README.md do lightrag-mcp

**Files:**
- Create: `C:/Workspace/pessoal/lightrag-mcp/LICENSE`
- Create: `C:/Workspace/pessoal/lightrag-mcp/README.md`

- [ ] **Step 1: Criar LICENSE (mesmo MIT)**

```text
MIT License

Copyright (c) 2026 Ricardo Kaminski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Criar README.md**

```markdown
# lightrag-mcp

> MCP server for [LightRAG](https://github.com/HKUDS/LightRAG) — expose your local knowledge base to Claude Code in 3 lines

[![PyPI](https://img.shields.io/pypi/v/lightrag-mcp)](https://pypi.org/project/lightrag-mcp/)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple)](https://modelcontextprotocol.io)

## What is this?

`lightrag-mcp` is a lightweight [MCP server](https://modelcontextprotocol.io) that connects Claude Code to any running [LightRAG](https://github.com/HKUDS/LightRAG) instance. It adds three tools to Claude Code: `query_rag`, `insert_document`, and `rag_health`.

No configuration files. No cloud. Configure with environment variables.

## Requirements

- A running [LightRAG server](https://github.com/HKUDS/LightRAG) (default: `localhost:9621`)
- Python 3.11+

> Need a full local RAG stack? See [local-rag](https://github.com/RicardoKaminski/local-rag) — a complete setup with Ollama, ingestion pipeline, and watcher daemon for Obsidian and Zotero.

## Installation

```bash
pip install lightrag-mcp
```

## Claude Code Configuration

Add to your Claude Code `settings.json` (`~/.claude/settings.json`):

```json
"mcpServers": {
  "lightrag": {
    "command": "lightrag-mcp",
    "env": {
      "LIGHTRAG_HOST": "localhost",
      "LIGHTRAG_PORT": "9621",
      "LIGHTRAG_DEFAULT_MODE": "hybrid"
    }
  }
}
```

Restart Claude Code. You now have three new tools available.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LIGHTRAG_HOST` | `localhost` | LightRAG server host |
| `LIGHTRAG_PORT` | `9621` | LightRAG server port |
| `LIGHTRAG_DEFAULT_MODE` | `hybrid` | Default query mode (`local`/`global`/`hybrid`) |

## MCP Tools

### `query_rag`
Query your knowledge base with natural language.

```
query_rag("What are the main themes in my research notes?")
query_rag("Find connections between topic A and topic B", mode="hybrid")
```

**Parameters:**
- `question` (required) — the question or topic to search
- `mode` (optional) — `local` (specific passages), `global` (broad themes), `hybrid` (both)

### `insert_document`
Index new text into the knowledge base.

```
insert_document("Your document text here...", description="report-2026-Q1.pdf")
```

**Parameters:**
- `text` (required) — document text to index
- `description` (optional) — label for this document

### `rag_health`
Check if the LightRAG server is reachable.

```
rag_health()
# → "LightRAG server: online (http://localhost:9621)"
```

## Using with uvx (no install needed)

```json
"mcpServers": {
  "lightrag": {
    "command": "uvx",
    "args": ["lightrag-mcp"]
  }
}
```

## License

MIT — see [LICENSE](LICENSE)
```

- [ ] **Step 3: Commit**

```bash
cd C:/Workspace/pessoal/lightrag-mcp
git add LICENSE README.md
git commit -m "docs: add MIT license and README with installation and usage"
```

---

### Task 13: Criar GitHub Actions workflow para publicação no PyPI

**Files:**
- Create: `C:/Workspace/pessoal/lightrag-mcp/.github/workflows/publish.yml`

Usa [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) — sem API keys armazenadas.

- [ ] **Step 1: Criar publish.yml**

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - "v*"

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write   # required for trusted publishing

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install build dependencies
        run: pip install hatchling build

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

- [ ] **Step 2: Commit**

```bash
cd C:/Workspace/pessoal/lightrag-mcp
git add .github/
git commit -m "ci: add GitHub Actions workflow for PyPI trusted publishing"
```

---

### Task 14: Criar repositório GitHub e publicar lightrag-mcp

- [ ] **Step 1: Criar repo no GitHub**

```bash
cd C:/Workspace/pessoal/lightrag-mcp
gh repo create lightrag-mcp \
  --public \
  --description "MCP server for LightRAG — expose your local knowledge base to Claude Code" \
  --source . \
  --remote origin \
  --push
```

- [ ] **Step 2: Adicionar topics**

```bash
gh repo edit RicardoKaminski/lightrag-mcp \
  --add-topic mcp \
  --add-topic lightrag \
  --add-topic rag \
  --add-topic claude-code \
  --add-topic local-llm \
  --add-topic ollama \
  --add-topic knowledge-graph \
  --add-topic privacy \
  --add-topic model-context-protocol
```

- [ ] **Step 3: Configurar PyPI Trusted Publisher**

Antes de fazer a tag, configure o trusted publisher no PyPI:
1. Crie uma conta em https://pypi.org (ou faça login)
2. Acesse https://pypi.org/manage/account/publishing/
3. Adicione um novo "pending publisher" com:
   - **PyPI project name:** `lightrag-mcp`
   - **Owner:** `RicardoKaminski`
   - **Repository:** `lightrag-mcp`
   - **Workflow:** `publish.yml`
   - **Environment:** `pypi`
4. No GitHub repo, vá em Settings → Environments → New environment → nome: `pypi`

- [ ] **Step 4: Criar tag v0.1.0 para disparar publicação**

```bash
cd C:/Workspace/pessoal/lightrag-mcp
git tag v0.1.0
git push origin v0.1.0
```

- [ ] **Step 5: Verificar publicação**

```bash
gh run list --repo RicardoKaminski/lightrag-mcp
```

Aguardar workflow completar (~2 min), então:

```bash
pip install lightrag-mcp
lightrag-mcp --help
```

---

### Task 15: Submeter ao MCP Registry e atualizar cross-links

- [ ] **Step 1: Submeter ao MCP Registry**

Acesse https://registry.modelcontextprotocol.io e siga o processo de submissão com:
- Nome: `lightrag-mcp`
- Comando de instalação: `pip install lightrag-mcp`
- Comando de execução: `lightrag-mcp`
- Variáveis de ambiente: `LIGHTRAG_HOST`, `LIGHTRAG_PORT`, `LIGHTRAG_DEFAULT_MODE`
- Repositório: `https://github.com/RicardoKaminski/lightrag-mcp`

- [ ] **Step 2: Adicionar PR ao awesome-mcp-servers**

```bash
gh repo fork modelcontextprotocol/servers
```

Adicionar em `README.md` do fork na seção de RAG:
```markdown
- [lightrag-mcp](https://github.com/RicardoKaminski/lightrag-mcp) - MCP server for LightRAG knowledge graphs
```

Abrir PR: `gh pr create --repo modelcontextprotocol/servers --title "Add lightrag-mcp" --body "..."`

- [ ] **Step 3: Verificar cross-links entre repos**

- `local-rag/README.md` → já tem link para `lightrag-mcp`
- `lightrag-mcp/README.md` → já tem link para `local-rag`

```bash
grep "lightrag-mcp" C:/Workspace/pessoal/local-rag/README.md
grep "local-rag" C:/Workspace/pessoal/lightrag-mcp/README.md
```

Ambos devem retornar resultado.
```

---

## Self-Review

**Spec coverage:**
- ✅ local-rag como template B+C → Tasks 1-8
- ✅ config.example.yaml genérico → Task 1
- ✅ pyproject.toml → Task 2
- ✅ LICENSE + CONTRIBUTING → Task 3
- ✅ start-rag.sh → Task 4
- ✅ Guias por persona (Obsidian, Zotero, generic) → Task 5
- ✅ Issue templates → Task 6
- ✅ README com estrutura de conversão → Task 7
- ✅ GitHub topics → Task 8
- ✅ lightrag-mcp pacote pip → Tasks 9-11
- ✅ Configuração via env vars → Task 10
- ✅ Entry point CLI → Task 11
- ✅ GitHub Actions para PyPI → Task 13
- ✅ MCP Registry submission → Task 15
- ✅ Cross-links entre repos → Task 15

**Placeholder scan:** Nenhum TBD, TODO ou "implement later" presente.

**Consistência de tipos:**
- `_query()`, `_insert()`, `_health()` definidos em Task 10 e usados apenas em Task 10 ✅
- `run()` entry point definido em Task 10 e referenciado em `pyproject.toml` Task 11 ✅
- API endpoints (`/health`, `/query`, `/documents/text`) consistentes com `lightrag_client.py` existente ✅
