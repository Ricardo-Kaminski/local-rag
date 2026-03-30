# Setup: local-rag

Guide the user through installing and configuring the local-rag stack.

## When to use this skill

Use when the user asks to:
- Install local-rag
- Set up local RAG with Obsidian or Zotero
- Configure Claude Code to use their local knowledge base
- Use Claude API as the LLM for their RAG

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
pip install local-rag-stack
```

### 4. Create config.yaml

```bash
curl -o config.yaml https://raw.githubusercontent.com/Ricardo-Kaminski/local-rag/main/config.example.yaml
# Then edit config.yaml: set your Obsidian/Zotero paths and lightrag.working_dir
```

### 5. Start the stack

```bash
local-rag start
```

### 6. Run initial ingestion

```bash
local-rag ingest
```

### 7. Configure Claude Code MCP

Add to `~/.claude/settings.json`:

```json
"mcpServers": {
  "lightrag": {
    "command": "local-rag",
    "args": ["mcp"]
  }
}
```

Restart Claude Code. You now have 7 tools: `query_rag`, `insert_document`, `rag_health`, `list_sources`, `get_indexed_documents`, `delete_document`, `get_graph_labels`.

## Using Claude API as LLM (optional)

To use Claude instead of Ollama for RAG responses, update `config.yaml`:

```yaml
llm:
  provider: "claude"
  model: "claude-opus-4-6"
  api_key: ""  # or set ANTHROPIC_API_KEY env var
```

Then restart: `local-rag start`

> Note: Ollama is still required for embeddings (nomic-embed-text).

## Troubleshooting

- **LightRAG not starting:** Check `ollama serve` is running and port 9621 is free
- **No results from query_rag:** Run `local-rag ingest` first to index your documents
- **Claude API error:** Verify ANTHROPIC_API_KEY is set correctly
