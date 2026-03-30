import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from local_rag.config_loader import load_config
from local_rag.lightrag_client import LightRAGClient, LightRAGError
from local_rag.extractor import extract_text, UnsupportedFormatError
from local_rag.chunker import chunk_text

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
config = load_config(CONFIG_PATH)
client = LightRAGClient(
    host=config["lightrag"]["host"],
    port=config["lightrag"]["port"]
)

server = Server("lightrag-local")


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
        import os as _os
        lines = []
        for source_name, source_cfg in config["sources"].items():
            path = source_cfg["path"]
            extensions = source_cfg.get("extensions", [])
            if _os.path.exists(path):
                count = sum(
                    1 for root, _, files in _os.walk(path)
                    for f in files
                    if not extensions or _os.path.splitext(f)[1].lower() in extensions
                )
                lines.append(f"• {source_name}: {path} ({count} files, exts: {extensions})")
            else:
                lines.append(f"• {source_name}: {path} (NOT FOUND)")
        return [types.TextContent(type="text", text="\n".join(lines) or "No sources configured.")]

    elif name == "get_indexed_documents":
        import requests as _req
        limit = arguments.get("limit", 20)
        base = f"http://{config['lightrag']['host']}:{config['lightrag']['port']}"
        try:
            r = _req.get(f"{base}/documents", params={"limit": limit}, timeout=10)
            if r.status_code != 200:
                return [types.TextContent(type="text", text=f"Error: {r.status_code} {r.text}")]
            docs = r.json()
            if not docs:
                return [types.TextContent(type="text", text="No documents indexed yet.")]
            lines = [
                f"• {d.get('id', '?')} — {d.get('content_summary', d.get('file_path', '?'))}"
                for d in docs[:limit]
            ]
            return [types.TextContent(type="text", text="\n".join(lines))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error fetching documents: {e}")]

    elif name == "delete_document":
        import requests as _req
        doc_id = arguments["doc_id"]
        base = f"http://{config['lightrag']['host']}:{config['lightrag']['port']}"
        try:
            r = _req.delete(f"{base}/documents/{doc_id}", timeout=10)
            if r.status_code in (200, 204):
                return [types.TextContent(type="text", text=f"Document {doc_id} deleted.")]
            return [types.TextContent(type="text", text=f"Error: {r.status_code} {r.text}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error deleting document: {e}")]

    elif name == "get_graph_labels":
        import requests as _req
        base = f"http://{config['lightrag']['host']}:{config['lightrag']['port']}"
        try:
            r = _req.get(f"{base}/graph/label/list", timeout=10)
            if r.status_code != 200:
                return [types.TextContent(type="text", text=f"Error: {r.status_code} {r.text}")]
            labels = r.json()
            if not labels:
                return [types.TextContent(type="text", text="No entity types found in graph yet.")]
            return [types.TextContent(type="text", text="Entity types in knowledge graph:\n" + "\n".join(f"• {l}" for l in labels))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error fetching graph labels: {e}")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
