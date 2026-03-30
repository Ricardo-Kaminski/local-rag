# PyPI + MCP Expansion + Claude API + Plugin — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformar `local-rag` em pacote pip publicável com CLI completo, MCP tools expandido, suporte a Claude API como LLM, e plugin no marketplace Claude Code.

**Architecture:** Renomear `src/` → `local_rag/` para nome de pacote válido no PyPI. Adicionar `local_rag/cli.py` com comandos click. Expandir `mcp_server.py` com 4 novos tools. Suporte a Claude API via flag `--llm-binding openai` do LightRAG server. Plugin Claude Code via `.claude-plugin/marketplace.json`.

**Tech Stack:** Python 3.11+, click, mcp (Anthropic SDK), requests, hatchling, GitHub Actions (OIDC PyPI publishing)

---

## Mapa de Arquivos

| Ação | Arquivo | Motivo |
|---|---|---|
| Criar | `local_rag/__init__.py` | Novo nome de pacote para PyPI |
| Mover | `src/*.py` → `local_rag/*.py` | Renomear pacote |
| Criar | `local_rag/cli.py` | CLI unificado |
| Modificar | `mcp_server.py` | + 4 novos MCP tools |
| Modificar | `ingest.py` | Atualizar imports |
| Modificar | `watcher.py` | Atualizar imports |
| Modificar | `pyproject.toml` | Entry points + click dep + PyPI metadata |
| Modificar | `config.example.yaml` | Seção `llm.provider` |
| Modificar | `start-rag.bat` | Usar `local-rag start` via CLI |
| Modificar | `start-rag.sh` | Usar `local-rag start` via CLI |
| Criar | `.github/workflows/publish.yml` | CI PyPI via OIDC |
| Criar | `.claude-plugin/marketplace.json` | Plugin marketplace Claude Code |
| Criar | `.claude-plugin/skills/setup-local-rag.md` | Skill de setup guiado |
| Modificar | `README.md` | Seção pip install + plugin |
| Modificar | `tests/*.py` | Atualizar imports src → local_rag |

---

## FASE 1: Refatoração do Pacote + CLI

---

### Task 1: Renomear src/ → local_rag/ e atualizar imports

**Files:**
- Create: `local_rag/__init__.py`
- Create: `local_rag/config_loader.py` (cópia com import corrigido)
- Create: `local_rag/extractor.py`
- Create: `local_rag/chunker.py`
- Create: `local_rag/checkpoint.py`
- Create: `local_rag/lightrag_client.py`
- Modify: `ingest.py`
- Modify: `watcher.py`
- Modify: `mcp_server.py`
- Modify: `tests/test_config_loader.py`
- Modify: `tests/test_extractor.py`
- Modify: `tests/test_chunker.py`
- Modify: `tests/test_checkpoint.py`
- Modify: `tests/test_lightrag_client.py`

- [ ] **Step 1: Criar local_rag/__init__.py**

```python
"""local-rag — 100% local RAG stack for Obsidian, Zotero, and Claude Code."""

__version__ = "0.1.0"
```

- [ ] **Step 2: Copiar módulos de src/ para local_rag/**

```bash
cd C:/Workspace/pessoal/local-rag
cp src/config_loader.py local_rag/config_loader.py
cp src/extractor.py local_rag/extractor.py
cp src/chunker.py local_rag/chunker.py
cp src/checkpoint.py local_rag/checkpoint.py
cp src/lightrag_client.py local_rag/lightrag_client.py
```

- [ ] **Step 3: Atualizar imports em ingest.py**

Substituir as 5 linhas de import no topo de `ingest.py`:
```python
from local_rag.config_loader import load_config
from local_rag.extractor import extract_text, UnsupportedFormatError
from local_rag.chunker import chunk_text
from local_rag.checkpoint import Checkpoint
from local_rag.lightrag_client import LightRAGClient, LightRAGError
```

- [ ] **Step 4: Atualizar imports em watcher.py**

Substituir as 5 linhas de import no topo de `watcher.py`:
```python
from local_rag.config_loader import load_config
from local_rag.extractor import extract_text, UnsupportedFormatError
from local_rag.chunker import chunk_text
from local_rag.checkpoint import Checkpoint
from local_rag.lightrag_client import LightRAGClient, LightRAGError
```

- [ ] **Step 5: Atualizar imports em mcp_server.py**

Substituir as 4 linhas de import de src/ no topo de `mcp_server.py`:
```python
from local_rag.config_loader import load_config
from local_rag.lightrag_client import LightRAGClient, LightRAGError
from local_rag.extractor import extract_text, UnsupportedFormatError
from local_rag.chunker import chunk_text
```

- [ ] **Step 6: Atualizar imports nos testes**

Em cada arquivo de test (`tests/test_*.py`), substituir `from src.` por `from local_rag.`:

```bash
cd C:/Workspace/pessoal/local-rag
sed -i 's/from src\./from local_rag./g' tests/test_config_loader.py tests/test_extractor.py tests/test_chunker.py tests/test_checkpoint.py tests/test_lightrag_client.py
```

- [ ] **Step 7: Verificar que os testes passam**

```bash
cd C:/Workspace/pessoal/local-rag
conda activate local-rag
pytest tests/ -v
```

Esperado: todos os testes passam (os que não dependem de servidor externo).

- [ ] **Step 8: Commit**

```bash
git add local_rag/ ingest.py watcher.py mcp_server.py tests/
git commit -m "refactor: rename src/ to local_rag/ for proper PyPI package name"
```

---

### Task 2: Criar local_rag/cli.py

**Files:**
- Create: `local_rag/cli.py`

O CLI orquestra todos os comandos. O comando `start` é o mais complexo — lê `config.yaml`, detecta o provider LLM e monta o comando `lightrag-server` correto.

- [ ] **Step 1: Criar local_rag/cli.py**

```python
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
    from ingest import run_ingest
    run_ingest(config)


@main.command()
@click.option("--config", default=DEFAULT_CONFIG, show_default=True, help="Path to config.yaml")
@click.option("--interval", default=60, show_default=True, help="Polling interval in seconds")
def watch(config, interval):
    """Start watcher daemon — continuously index new documents."""
    from watcher import run_watcher
    run_watcher(config, interval)


@main.command("mcp")
@click.option("--config", default=DEFAULT_CONFIG, show_default=True, help="Path to config.yaml")
def mcp_serve(config):
    """Start MCP server for Claude Code integration."""
    os.environ["LOCAL_RAG_CONFIG"] = os.path.abspath(config)
    from local_rag.mcp_server import main as _mcp_main
    asyncio.run(_mcp_main())


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

    # Build lightrag-server command based on LLM provider
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
            click.echo("ERROR: Claude provider requires ANTHROPIC_API_KEY env var or llm.api_key in config.", err=True)
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
        watcher_proc = subprocess.Popen([sys.executable, "watcher.py", "--config", config])
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
```

- [ ] **Step 2: Verificar import**

```bash
cd C:/Workspace/pessoal/local-rag
conda activate local-rag
python -c "from local_rag.cli import main; print('OK')"
```

Esperado: `OK`

- [ ] **Step 3: Commit**

```bash
git add local_rag/cli.py
git commit -m "feat: add unified CLI with ingest, watch, mcp, start commands"
```

---

### Task 3: Atualizar pyproject.toml com entry points, click e PyPI metadata

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Reescrever pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "local-rag"
version = "0.1.0"
description = "100% local RAG for Obsidian, Zotero, and Claude Code — LightRAG + Ollama + MCP"
readme = "README.md"
license = { file = "LICENSE" }
requires-python = ">=3.11"
keywords = ["rag", "local-llm", "ollama", "lightrag", "mcp", "claude", "obsidian", "zotero", "knowledge-graph"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
dependencies = [
    "lightrag-hku[api]",
    "pymupdf",
    "python-docx",
    "openpyxl",
    "bibtexparser",
    "pyyaml",
    "requests",
    "mcp",
    "click>=8.0",
]

[project.scripts]
local-rag = "local_rag.cli:main"

[project.urls]
Homepage = "https://github.com/Ricardo-Kaminski/local-rag"
Repository = "https://github.com/Ricardo-Kaminski/local-rag"
Issues = "https://github.com/Ricardo-Kaminski/local-rag/issues"
Documentation = "https://github.com/Ricardo-Kaminski/local-rag/tree/main/docs/guides"

[tool.hatch.build.targets.wheel]
packages = ["local_rag"]
```

- [ ] **Step 2: Instalar e verificar CLI**

```bash
cd C:/Workspace/pessoal/local-rag
conda activate local-rag
pip install click>=8.0
pip install -e .
local-rag --help
```

Esperado:
```
Usage: local-rag [OPTIONS] COMMAND [ARGS]...

  local-rag — 100% local RAG stack for Obsidian, Zotero, and Claude Code.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  ingest  Run ingestion pipeline once...
  mcp     Start MCP server for Claude Code integration.
  start   Start LightRAG server and (optionally) watcher daemon.
  watch   Start watcher daemon...
```

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: update pyproject.toml with CLI entry point, click dep, PyPI classifiers"
```

---

### Task 4: Adicionar GitHub Actions para publicação no PyPI

**Files:**
- Create: `.github/workflows/publish.yml`

- [ ] **Step 1: Criar .github/workflows/publish.yml**

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
      id-token: write

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install build tools
        run: pip install hatchling build

      - name: Build
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

- [ ] **Step 2: Configurar PyPI Trusted Publisher**

Antes de criar a tag, configure em https://pypi.org/manage/account/publishing/:
- Project name: `local-rag`
- Owner: `Ricardo-Kaminski`
- Repository: `local-rag`
- Workflow: `publish.yml`
- Environment: `pypi`

Criar o environment no GitHub:
```bash
"/c/Program Files/GitHub CLI/gh" api repos/Ricardo-Kaminski/local-rag/environments/pypi -X PUT -F wait_timer=0
```

- [ ] **Step 3: Commit e push**

```bash
git add .github/workflows/publish.yml
git commit -m "ci: add PyPI trusted publishing workflow"
git push origin main
```

---

## FASE 2: Expansão das Ferramentas MCP

---

### Task 5: Adicionar 4 novos MCP tools ao mcp_server.py

**Files:**
- Modify: `mcp_server.py`

Novos tools baseados nos endpoints da LightRAG REST API:
- `list_sources` — lista fontes configuradas no config.yaml com contagem de arquivos
- `get_indexed_documents` — GET /documents → documentos já indexados
- `delete_document` — DELETE /documents/{doc_id} → remove um documento
- `get_graph_labels` — GET /graph/label/list → tipos de entidade no grafo

- [ ] **Step 1: Adicionar os 4 tools à lista em list_tools()**

Substituir a função `list_tools()` inteira em `mcp_server.py`:

```python
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="query_rag",
            description="Consulta a base de conhecimento RAG local (Obsidian + Zotero)",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Pergunta ou tema a pesquisar"},
                    "mode": {
                        "type": "string",
                        "enum": ["local", "global", "hybrid"],
                        "default": "hybrid",
                        "description": "local=trechos específicos, global=visão ampla, hybrid=ambos"
                    }
                },
                "required": ["question"]
            }
        ),
        types.Tool(
            name="insert_document",
            description="Indexa um arquivo específico no RAG",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho absoluto do arquivo"}
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="rag_health",
            description="Verifica se o servidor LightRAG está online",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="list_sources",
            description="Lista as fontes configuradas e quantos arquivos cada uma tem",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="get_indexed_documents",
            description="Lista os documentos já indexados no LightRAG",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Máximo de documentos a retornar (padrão: 20)", "default": 20}
                }
            }
        ),
        types.Tool(
            name="delete_document",
            description="Remove um documento da base RAG pelo ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "ID do documento (obtido via get_indexed_documents)"}
                },
                "required": ["doc_id"]
            }
        ),
        types.Tool(
            name="get_graph_labels",
            description="Lista os tipos de entidade presentes no grafo de conhecimento",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]
```

- [ ] **Step 2: Adicionar os handlers no call_tool()**

Substituir a função `call_tool()` inteira em `mcp_server.py`:

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "query_rag":
        mode = arguments.get("mode", "hybrid")
        try:
            result = client.query(arguments["question"], mode=mode)
            return [types.TextContent(type="text", text=result)]
        except LightRAGError as e:
            return [types.TextContent(type="text", text=f"Erro na consulta: {e}")]

    elif name == "insert_document":
        path = arguments["path"]
        try:
            text = extract_text(path)
            cfg = config["chunking"]
            chunks = chunk_text(text, path, cfg["chunk_size"], cfg["overlap"])
            for chunk in chunks:
                desc = f"{chunk['source']} [{chunk['chunk_index']+1}/{chunk['total_chunks']}]"
                client.insert_text(chunk["text"], description=desc)
            return [types.TextContent(type="text", text=f"Indexado: {path} ({len(chunks)} chunks)")]
        except UnsupportedFormatError as e:
            return [types.TextContent(type="text", text=f"Formato não suportado: {e}")]
        except LightRAGError as e:
            return [types.TextContent(type="text", text=f"Erro ao indexar: {e}")]

    elif name == "rag_health":
        ok = client.health_check()
        status = "online" if ok else "offline"
        return [types.TextContent(type="text", text=f"LightRAG server: {status}")]

    elif name == "list_sources":
        import os
        lines = []
        for source_name, source_cfg in config["sources"].items():
            path = source_cfg["path"]
            extensions = source_cfg.get("extensions", [])
            if os.path.exists(path):
                count = sum(
                    1 for root, _, files in os.walk(path)
                    for f in files
                    if not extensions or os.path.splitext(f)[1].lower() in extensions
                )
                lines.append(f"• {source_name}: {path} ({count} files, exts: {extensions})")
            else:
                lines.append(f"• {source_name}: {path} (NOT FOUND)")
        return [types.TextContent(type="text", text="\n".join(lines) or "No sources configured.")]

    elif name == "get_indexed_documents":
        import requests as _req
        limit = arguments.get("limit", 20)
        try:
            r = _req.get(
                f"http://{config['lightrag']['host']}:{config['lightrag']['port']}/documents",
                params={"limit": limit},
                timeout=10
            )
            if r.status_code != 200:
                return [types.TextContent(type="text", text=f"Error: {r.status_code} {r.text}")]
            docs = r.json()
            if not docs:
                return [types.TextContent(type="text", text="No documents indexed yet.")]
            lines = [f"• {d.get('id', '?')} — {d.get('content_summary', d.get('file_path', '?'))}" for d in docs[:limit]]
            return [types.TextContent(type="text", text="\n".join(lines))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error fetching documents: {e}")]

    elif name == "delete_document":
        import requests as _req
        doc_id = arguments["doc_id"]
        try:
            r = _req.delete(
                f"http://{config['lightrag']['host']}:{config['lightrag']['port']}/documents/{doc_id}",
                timeout=10
            )
            if r.status_code in (200, 204):
                return [types.TextContent(type="text", text=f"Document {doc_id} deleted.")]
            return [types.TextContent(type="text", text=f"Error: {r.status_code} {r.text}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error deleting document: {e}")]

    elif name == "get_graph_labels":
        import requests as _req
        try:
            r = _req.get(
                f"http://{config['lightrag']['host']}:{config['lightrag']['port']}/graph/label/list",
                timeout=10
            )
            if r.status_code != 200:
                return [types.TextContent(type="text", text=f"Error: {r.status_code} {r.text}")]
            labels = r.json()
            if not labels:
                return [types.TextContent(type="text", text="No entity types found in graph yet.")]
            return [types.TextContent(type="text", text="Entity types in knowledge graph:\n" + "\n".join(f"• {l}" for l in labels))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error fetching graph labels: {e}")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
```

- [ ] **Step 3: Verificar import**

```bash
cd C:/Workspace/pessoal/local-rag
conda activate local-rag
python -c "import mcp_server; print('OK')"
```

Esperado: `OK` (sem erros de import)

- [ ] **Step 4: Commit**

```bash
git add mcp_server.py
git commit -m "feat: expand MCP tools — list_sources, get_indexed_documents, delete_document, get_graph_labels"
```

---

## FASE 3: Suporte a Claude API como LLM

---

### Task 6: Atualizar config.example.yaml com seção llm.provider

**Files:**
- Modify: `config.example.yaml`

- [ ] **Step 1: Adicionar seção llm ao config.example.yaml**

Adicionar após a seção `ollama:`:

```yaml
# Provider do LLM: "ollama" (padrão, local) ou "claude" (Anthropic API)
llm:
  provider: "ollama"        # ollama | claude

  # --- Configuração Ollama (padrão) ---
  # llm_model e embedding_model são lidos da seção "ollama" acima.

  # --- Configuração Claude (descomente para usar) ---
  # provider: "claude"
  # model: "claude-opus-4-6"        # claude-opus-4-6 | claude-sonnet-4-6 | claude-haiku-4-5
  # api_key: ""                      # ou defina ANTHROPIC_API_KEY como variável de ambiente
  #
  # Nota: O embedding continua usando Ollama (nomic-embed-text) mesmo com LLM Claude.
  # Claude não expõe endpoint de embeddings compatível com LightRAG.
```

- [ ] **Step 2: Commit**

```bash
git add config.example.yaml
git commit -m "feat: add llm.provider config section — supports ollama and claude"
```

---

### Task 7: Atualizar start-rag.bat e start-rag.sh para usar local-rag start

Os scripts de startup agora delegam ao CLI — que já tem a lógica de provider no `cli.py`.

**Files:**
- Modify: `start-rag.bat`
- Modify: `start-rag.sh`

- [ ] **Step 1: Reescrever start-rag.bat**

```batch
@echo off
title Local RAG - Iniciando...
echo ============================================
echo   Local RAG Stack - Iniciando servicos
echo ============================================
echo.

:: Verificar se Ollama esta rodando (para embeddings)
echo [0/1] Verificando Ollama (necessario para embeddings)...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo       Ollama ja esta rodando.
) else (
    echo       Iniciando Ollama...
    start "" "ollama" serve
    timeout /t 3 /nobreak >NUL
)

:: Usar o CLI local-rag start
echo [1/1] Iniciando stack via local-rag CLI...
call conda activate local-rag
local-rag start --config config.yaml

echo.
echo Stack encerrado.
```

- [ ] **Step 2: Reescrever start-rag.sh**

```bash
#!/usr/bin/env bash
set -e

echo "============================================"
echo "  Local RAG Stack - Starting services"
echo "============================================"
echo ""

# Check Ollama (needed for embeddings)
echo "[0/1] Checking Ollama (required for embeddings)..."
if pgrep -x "ollama" > /dev/null 2>&1; then
    echo "      Ollama is already running."
else
    echo "      Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Delegate to CLI
echo "[1/1] Starting stack via local-rag CLI..."
conda run -n local-rag local-rag start --config config.yaml
```

- [ ] **Step 3: Commit**

```bash
git add start-rag.bat start-rag.sh
git commit -m "refactor: start scripts delegate to local-rag CLI (supports ollama + claude providers)"
```

---

## FASE 4: Claude Code Plugin

---

### Task 8: Criar .claude-plugin/marketplace.json e skill de setup

**Files:**
- Create: `.claude-plugin/marketplace.json`
- Create: `.claude-plugin/skills/setup-local-rag.md`

O plugin permite que qualquer usuário do Claude Code instale `local-rag` diretamente via `/plugin install local-rag`.

- [ ] **Step 1: Criar .claude-plugin/marketplace.json**

```json
{
  "name": "local-rag",
  "display_name": "Local RAG",
  "description": "100% local RAG for Obsidian, Zotero, and Claude Code — LightRAG + Ollama + MCP",
  "version": "0.1.0",
  "author": "Ricardo Kaminski",
  "homepage": "https://github.com/Ricardo-Kaminski/local-rag",
  "license": "MIT",
  "keywords": ["rag", "local-llm", "ollama", "lightrag", "obsidian", "zotero", "knowledge-graph", "privacy"],
  "skills": [
    {
      "name": "setup-local-rag",
      "path": "skills/setup-local-rag.md",
      "description": "Guided setup for the local-rag stack"
    }
  ],
  "mcpServers": {
    "lightrag": {
      "command": "local-rag",
      "args": ["mcp"],
      "description": "LightRAG knowledge base — query_rag, insert_document, rag_health, list_sources, get_indexed_documents, delete_document, get_graph_labels"
    }
  }
}
```

- [ ] **Step 2: Criar .claude-plugin/skills/setup-local-rag.md**

```markdown
# Setup: local-rag

Guide the user through installing and configuring the local-rag stack.

## When to use this skill

Use when the user asks to:
- Install local-rag
- Set up local RAG with Obsidian or Zotero
- Configure Claude Code to use their local knowledge base

## Steps

### 1. Check prerequisites

Ask the user to confirm:
- [ ] Ollama installed (https://ollama.com)
- [ ] Python 3.11+
- [ ] At least 10GB free disk space
- [ ] 8GB RAM (16GB recommended)

### 2. Install Ollama models

```bash
ollama pull qwen2.5:14b        # LLM (~8GB) — or llama3.2:3b for less VRAM
ollama pull nomic-embed-text   # Embeddings (~300MB)
```

### 3. Install local-rag

```bash
pip install local-rag
```

### 4. Create config.yaml

```bash
# Download the example config
curl -o config.yaml https://raw.githubusercontent.com/Ricardo-Kaminski/local-rag/main/config.example.yaml
# Then edit config.yaml with your paths
```

### 5. Start LightRAG server

```bash
local-rag start
```

### 6. Run initial ingestion

```bash
local-rag ingest
```

### 7. Verify Claude Code MCP connection

```bash
local-rag mcp  # Should start without errors
```

Add to `~/.claude/settings.json`:
```json
"mcpServers": {
  "lightrag": {
    "command": "local-rag",
    "args": ["mcp"]
  }
}
```

## Claude API (optional)

To use Claude as the LLM instead of Ollama, update `config.yaml`:

```yaml
llm:
  provider: "claude"
  model: "claude-opus-4-6"
  api_key: ""  # or set ANTHROPIC_API_KEY env var
```

Then restart: `local-rag start`
```

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/
git commit -m "feat: add Claude Code plugin manifest and setup skill"
```

---

### Task 9: Atualizar README.md com seção pip install e plugin

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Adicionar seção "Install via pip" após o quickstart**

Localizar a linha `## Guides by Use Case` no README.md e inserir antes dela:

```markdown
## Install via pip

```bash
pip install local-rag
```

After installation, the `local-rag` CLI is available:

```bash
local-rag ingest          # index all documents once
local-rag watch           # continuous indexing daemon
local-rag start           # start LightRAG server + watcher
local-rag mcp             # start MCP server (for testing)
```

Configure Claude Code to use the MCP server:

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

Or add manually to `~/.claude/settings.json` as shown above.

## Using Claude API as LLM (optional)

Set in `config.yaml` to use Claude instead of Ollama for RAG responses:

```yaml
llm:
  provider: "claude"
  model: "claude-opus-4-6"
  api_key: ""   # or set ANTHROPIC_API_KEY env var
```

> Note: Ollama is still required for embeddings (nomic-embed-text). Only the LLM can be replaced with Claude.

```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add pip install section, CLI commands, Claude plugin, and Claude API LLM option"
```

---

### Task 10: Publicar no PyPI e push para GitHub

- [ ] **Step 1: Configurar PyPI Trusted Publisher (se ainda não feito)**

Acesse https://pypi.org/manage/account/publishing/ e adicione:
- Project name: `local-rag`
- Owner: `Ricardo-Kaminski`
- Repository: `local-rag`
- Workflow: `publish.yml`
- Environment: `pypi`

- [ ] **Step 2: Push tudo para GitHub**

```bash
cd C:/Workspace/pessoal/local-rag
git push origin main
```

- [ ] **Step 3: Criar tag v0.1.0 para disparar CI**

```bash
git tag v0.1.0
git push origin v0.1.0
```

- [ ] **Step 4: Verificar workflow**

```bash
"/c/Program Files/GitHub CLI/gh" run list --repo Ricardo-Kaminski/local-rag
```

Aguardar `Publish to PyPI` completar com sucesso.

- [ ] **Step 5: Verificar no PyPI**

```bash
pip install local-rag
local-rag --version
```

Esperado: `local-rag, version 0.1.0`

---

### Task 11: Arquivar lightrag-mcp e redirecionar para local-rag

**Files:**
- Modify: `C:/Workspace/pessoal/lightrag-mcp/README.md`

O repo `lightrag-mcp` é redundante agora que `local-rag` inclui o MCP server. Atualizar o README para redirecionar usuários.

- [ ] **Step 1: Atualizar README.md do lightrag-mcp**

Substituir o conteúdo inteiro de `C:/Workspace/pessoal/lightrag-mcp/README.md` por:

```markdown
# lightrag-mcp

> ⚠️ This package has been superseded by [local-rag](https://github.com/Ricardo-Kaminski/local-rag).

`local-rag` includes the MCP server plus a complete RAG stack (ingestion pipeline, watcher daemon, multi-source support, and Claude API integration).

## Migration

Replace:
```bash
pip install lightrag-mcp
```

With:
```bash
pip install local-rag
```

Update your `settings.json`:
```json
"mcpServers": {
  "lightrag": {
    "command": "local-rag",
    "args": ["mcp"]
  }
}
```

See [local-rag](https://github.com/Ricardo-Kaminski/local-rag) for full documentation.
```

- [ ] **Step 2: Commit e push**

```bash
cd C:/Workspace/pessoal/lightrag-mcp
git add README.md
git commit -m "docs: redirect to local-rag (supersedes this package)"
git push origin main
```

- [ ] **Step 3: Arquivar o repo no GitHub**

```bash
"/c/Program Files/GitHub CLI/gh" repo archive Ricardo-Kaminski/lightrag-mcp --yes
```

---

## Self-Review

**Spec coverage:**
- ✅ CLI (`local-rag ingest/watch/mcp/start`) → Tasks 2, 3
- ✅ PyPI com nome `local-rag` → Tasks 3, 4, 10
- ✅ MCP tools expandido (+ 4 tools) → Task 5
- ✅ Claude API como LLM alternativo → Tasks 6, 7
- ✅ Claude Code Plugin marketplace → Task 8
- ✅ README atualizado → Task 9
- ✅ lightrag-mcp arquivado → Task 11

**Placeholder scan:** Nenhum TBD ou "implement later".

**Consistência de tipos:**
- `load_config()` retorna `dict` — usado consistentemente em `cli.py` (Task 2) e `mcp_server.py` (Task 5) ✅
- `client.query()`, `client.insert_text()`, `client.health_check()` — definidos em `lightrag_client.py`, usados em `mcp_server.py` ✅
- `config["lightrag"]["host"]` / `config["lightrag"]["port"]` — presentes no `config.example.yaml` e acessados consistentemente ✅
- `config["llm"]["provider"]` — adicionado ao `config.example.yaml` (Task 6) e lido em `cli.py` (Task 2) ✅
- Imports em `cli.py` usam `from local_rag.*` — consistente com renomeação de Task 1 ✅
