# GitHub Publication & MCP Distribution — Design Spec
**Data:** 2026-03-30
**Status:** Aprovado

---

## Objetivo

Transformar o projeto `local-rag` em dois repositórios públicos complementares:

1. **`local-rag`** — template de referência open-source (B+C), voltado para pesquisadores, desenvolvedores e usuários de Claude Code que querem RAG 100% local
2. **`lightrag-mcp`** — pacote pip leve e distribuível, publicado no MCP Registry oficial e no Claude Code Plugin marketplace

---

## Público-Alvo

| Persona | Repo principal | Ponto de entrada |
|---|---|---|
| Pesquisador (Obsidian + Zotero) | `local-rag` | `docs/guides/obsidian.md` + `docs/guides/zotero.md` |
| Desenvolvedor (RAG genérico) | `local-rag` | `docs/guides/generic.md` |
| Usuário Claude Code | `lightrag-mcp` | `pip install lightrag-mcp` + settings.json |

---

## Repo 1: `local-rag` — Template de Referência

### Propósito
Clone-e-use. Projeto de referência que demonstra uma stack RAG local completa com LightRAG + Ollama + MCP + watcher daemon.

### Mudanças na codebase atual

| Item | Mudança |
|---|---|
| `config.yaml` | Renomear para `config.example.yaml` com caminhos genéricos e comentários |
| Variáveis de ambiente | Fallback via `LIGHTRAG_HOST`, `LIGHTRAG_PORT`, `OBSIDIAN_PATH`, etc. |
| `.gitignore` | Cobrir `config.yaml`, `data/`, `*.json` de checkpoint |
| `start-rag.bat` | Já existe — manter |
| `start-rag.sh` | Novo — equivalente Linux/macOS |
| `environment.yml` | Manter para Conda; adicionar `pyproject.toml` como alternativa pip |

### Arquivos adicionados

| Arquivo | Propósito |
|---|---|
| `README.md` | Landing page rica: badges, demo GIF, arquitetura, quickstart, links por persona |
| `LICENSE` | MIT |
| `CONTRIBUTING.md` | Guia de contribuição com lowbar intencional |
| `docs/guides/obsidian.md` | Guia completo para usuários Obsidian |
| `docs/guides/zotero.md` | Guia completo para usuários Zotero |
| `docs/guides/generic.md` | Guia para qualquer base de documentos |
| `.github/ISSUE_TEMPLATE/` | Templates de bug report e feature request |

### Estrutura final

```
local-rag/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── config.example.yaml
├── pyproject.toml
├── environment.yml
├── ingest.py
├── mcp_server.py
├── watcher.py
├── start-rag.bat
├── start-rag.sh
├── src/
│   ├── config_loader.py
│   ├── extractor.py
│   ├── chunker.py
│   ├── checkpoint.py
│   └── lightrag_client.py
├── docs/
│   ├── guides/
│   │   ├── obsidian.md
│   │   ├── zotero.md
│   │   └── generic.md
│   └── superpowers/
│       ├── specs/
│       └── plans/
└── .github/
    └── ISSUE_TEMPLATE/
```

### README — Estrutura para conversão de stars

```
1. Badge strip        — Python, License, MCP Registry, PyPI
2. Headline           — "100% local RAG for Obsidian + Zotero + Claude Code"
3. Demo GIF/screenshot — query no Claude Code respondendo com contexto do vault
4. Por que local?     — privacidade, sem API key, funciona offline
5. Diagrama de arquitetura
6. Quickstart em 5 comandos
7. Guias por persona (links)
8. "Works with" — Obsidian, Zotero, Claude Code, Ollama, LightRAG
```

### GitHub Topics
```
rag  local-llm  ollama  lightrag  mcp  claude-code
obsidian  zotero  knowledge-graph  privacy
```

---

## Repo 2: `lightrag-mcp` — Pacote Distribuível

### Propósito
Pacote pip leve com uma responsabilidade única: expor qualquer instância LightRAG como MCP server. Zero configuração além de variáveis de ambiente.

### Identidade
- **Pacote pip:** `lightrag-mcp`
- **Instalação:** `pip install lightrag-mcp` ou `uvx lightrag-mcp`
- **MCP Registry:** `lightrag-mcp`
- **GitHub:** `<usuario>/lightrag-mcp`

### Configuração via variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `LIGHTRAG_HOST` | `localhost` | Host do servidor LightRAG |
| `LIGHTRAG_PORT` | `9621` | Porta do servidor LightRAG |
| `LIGHTRAG_DEFAULT_MODE` | `hybrid` | Modo padrão de query (local/global/hybrid) |

### Ferramentas MCP expostas

| Tool | Input | Descrição |
|---|---|---|
| `query_rag` | `question` (str), `mode` (str, opcional) | Consulta com modo configurável |
| `insert_document` | `path` (str) | Indexa um arquivo por caminho absoluto |
| `rag_health` | — | Retorna status do servidor LightRAG |

### Estrutura do repo

```
lightrag-mcp/
├── README.md
├── LICENSE
├── pyproject.toml          ← entry point: lightrag-mcp = lightrag_mcp.server:main
├── lightrag_mcp/
│   ├── __init__.py
│   └── server.py           ← mcp_server.py atual refatorado
└── .github/
    └── workflows/
        └── publish.yml     ← CI: testa + publica no PyPI ao criar tag
```

### Configuração Claude Code (usuário final)

```json
"mcpServers": {
  "lightrag": {
    "command": "uvx",
    "args": ["lightrag-mcp"],
    "env": {
      "LIGHTRAG_HOST": "localhost",
      "LIGHTRAG_PORT": "9621"
    }
  }
}
```

### Fluxo de distribuição

```
Tag v0.1.0 no GitHub
    → CI (GitHub Actions) publica no PyPI automaticamente
    → Submissão manual no MCP Registry (registry.modelcontextprotocol.io)
    → Submissão no Claude Plugin marketplace (claude.ai/settings/plugins/submit)
```

---

## Estratégia de Stars e Descoberta

### Canais de distribuição

| Canal | Ação | Repo alvo |
|---|---|---|
| MCP Registry oficial | Submeter após v0.1 | `lightrag-mcp` |
| Claude Plugin marketplace | Submeter após aprovação | `lightrag-mcp` |
| Hacker News (Show HN) | Post cobrindo ambos | ambos |
| Reddit r/LocalLLaMA | Foco LLM local + RAG | ambos |
| Reddit r/ObsidianMD | Foco PKM + Obsidian | `local-rag` |
| awesome-mcp-servers | PR de adição | `lightrag-mcp` |
| awesome-selfhosted | PR de adição | `local-rag` |

### Sequência de lançamento

1. **Semana 1:** Polir e publicar `local-rag` no GitHub
2. **Semana 2:** Criar e publicar `lightrag-mcp` com link cruzado
3. **Semana 3:** Posts em comunidades após ambos estarem estáveis

---

## Licença

MIT para ambos os repos — máxima adoção sem fricção legal.

---

## Fora de escopo

- Suporte a backends além de Ollama (pode ser contribuição futura)
- Interface web/UI própria
- Autenticação no MCP server
- Deploy em cloud (projeto intencionalmente local-first)
