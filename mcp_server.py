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
        )
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

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
