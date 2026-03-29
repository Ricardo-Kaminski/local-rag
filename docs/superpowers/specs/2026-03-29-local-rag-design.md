# Local RAG System — Design Spec
**Data:** 2026-03-29
**Status:** Aprovado

---

## Objetivo

Sistema RAG 100% local para extração de dados e exploração de documentos pessoais e acadêmicos, integrado ao Claude Code (via MCP) e ao Obsidian. Arquitetura modular reutilizável como camada RAG em projetos futuros.

---

## Arquitetura Geral

```
┌─────────────────────────────────────────────────────────┐
│                    FONTES DE DADOS                       │
│  D:/Obsidian/vault/ (.md)  │  D:/_bib_Zotero/ (.bib+pdf)│
└───────────────────┬─────────────────────────────────────┘
                    │ ingestão (pipeline Python)
                    ▼
┌─────────────────────────────────────────────────────────┐
│                  LIGHTRAG SERVER                         │
│  • Grafo de entidades/relações  (NanoVectorDB local)    │
│  • Índice vetorial              (NanoVectorDB local)    │
│  • LLM local                    (Ollama — qwen2.5:14b)  │
│  • Embeddings                   (Ollama — nomic-embed)  │
│  • API REST  http://localhost:9621                       │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
               ▼                      ▼
┌──────────────────────┐   ┌──────────────────────────────┐
│   CLAUDE CODE (MCP)  │   │   OBSIDIAN                   │
│   • query via MCP    │   │   • plugin Smart Connections  │
│   • extração/análise │   │   • busca semântica inline    │
│   • scripts Python   │   │   • notas geradas pelo RAG   │
└──────────────────────┘   └──────────────────────────────┘
```

---

## Componentes

| Componente | Tecnologia | Função |
|---|---|---|
| RAG Engine | LightRAG (HKUDS) | grafo de conhecimento + vetores |
| LLM local | Ollama + qwen2.5:14b | geração de respostas |
| Embeddings | Ollama + nomic-embed-text | indexação semântica |
| Pipeline de ingestão | Python (ingest.py) | processar fontes de dados |
| Integração Claude Code | MCP server (mcp_server.py) | queries no terminal |
| Integração Obsidian | Smart Connections plugin | busca semântica nas notas |
| Armazenamento | `data/lightrag_storage/` | grafo + vetores (local) |

---

## Fontes de Dados

| Fonte | Caminho | Formatos |
|---|---|---|
| Obsidian vault | `D:/Obsidian/vault/` | .md |
| Zotero | `D:/_bib_Zotero/` | .bib, .pdf |

> Google Drive excluído por conter backups do PC (evitar duplicação e indexação desnecessária). Pode ser adicionado via `config.yaml` no futuro com `include_paths` seletivo.

---

## Pipeline de Ingestão

### Etapas

1. **Descoberta** — varre pastas configuradas no `config.yaml`, filtra por extensão, verifica checkpoint para evitar reprocessamento
2. **Extração de texto**
   - `.md` → leitura direta
   - `.pdf` → pymupdf (PDFs digitais) ou tesseract (PDFs escaneados)
   - `.docx` → python-docx
   - `.xlsx` → openpyxl
   - `.bib` → bibtexparser
3. **Chunking** — chunks de ~500 tokens com overlap de 50, metadados preservados (fonte, pasta, data)
4. **Indexação** — envio via API REST do LightRAG, que extrai entidades e relações via LLM e armazena vetores + grafo localmente

### Configuração (`config.yaml`)

```yaml
sources:
  obsidian:
    path: "D:/Obsidian/vault/"
    include_all: true

  zotero:
    path: "D:/_bib_Zotero/"
    extensions: [".pdf", ".bib"]

lightrag:
  host: "localhost"
  port: 9621
  working_dir: "C:/workspace/pessoal/local-rag/data/lightrag_storage"

ollama:
  llm_model: "qwen2.5:14b"
  embedding_model: "nomic-embed-text"
```

---

## Integração Claude Code (MCP)

O MCP server (`mcp_server.py`) faz a ponte entre Claude Code e a API REST do LightRAG. Ferramentas disponíveis no terminal:

| Ferramenta MCP | Descrição |
|---|---|
| `query_rag(question, mode)` | busca híbrida (local / global / hybrid) |
| `insert_document(path)` | indexa um arquivo específico |
| `get_graph_entities(entity)` | explora nó no grafo de conhecimento |
| `search_by_keyword(term)` | busca por termo exato |

**Modos de query:**
- `local` — contexto específico em trechos próximos
- `global` — visão ampla sobre todo o corpus
- `hybrid` — combina os dois (recomendado para pesquisa acadêmica)

**Configuração no `settings.json` do Claude Code:**
```json
"mcpServers": {
  "lightrag": {
    "command": "python",
    "args": ["C:/workspace/pessoal/local-rag/mcp_server.py"]
  }
}
```

---

## Integração Obsidian

Plugin **Smart Connections** configurado para apontar para `http://localhost:9621`. Permite busca semântica inline nas notas sem sair do Obsidian.

---

## Estrutura do Projeto

```
C:/workspace/pessoal/local-rag/
├── config.yaml              ← fontes, modelos, caminhos
├── ingest.py                ← pipeline de ingestão
├── mcp_server.py            ← MCP server para Claude Code
├── watcher.py               ← daemon para detectar novos arquivos
├── requirements.txt
├── docs/
│   └── superpowers/specs/
│       └── 2026-03-29-local-rag-design.md
└── data/
    └── lightrag_storage/    ← grafo + vetores (local, não commitar)
```

---

## Instalação

### 1. Ollama
```bash
# Baixar em https://ollama.com e instalar
# Modelos salvos em D: (C: com pouco espaço)
$env:OLLAMA_MODELS = "D:\ollama_models"  # PowerShell
# ou definir como variável de ambiente permanente no Windows

ollama pull qwen2.5:14b
ollama pull nomic-embed-text
```

### 2. LightRAG
```bash
pip install "lightrag-hku[api]"
```

### 3. Iniciar servidor
```bash
lightrag-server --host 0.0.0.0 --port 9621 \
  --llm-provider ollama --llm-model qwen2.5:14b \
  --embedding-provider ollama --embedding-model nomic-embed-text \
  --working-dir C:/workspace/pessoal/local-rag/data/lightrag_storage
```

### 4. Rodar ingestão
```bash
python ingest.py --config config.yaml
```

---

## Requisitos de Hardware

- RAM mínima: 8GB
- Espaço em disco: ~5GB (modelos Ollama + storage LightRAG)
- GPU: opcional (melhora performance, mas não obrigatório)

---

## Casos de Uso Prioritários

1. **Pesquisa acadêmica** — perguntas contextualizadas sobre tese, artigos e referências Zotero
2. **Gestão de conhecimento** — navegar conexões entre notas do Obsidian, descobrir relações entre conceitos
3. **Trabalho analítico** — extrair informações específicas de relatórios e documentos institucionais

---

## Extensibilidade Futura

A arquitetura foi pensada para reuso como camada RAG em outros projetos (ex: desd-xt). Para isso basta:
- Apontar novas fontes no `config.yaml`
- Reutilizar `mcp_server.py` em outros projetos
- O LightRAG server roda como serviço independente acessível por qualquer cliente HTTP
