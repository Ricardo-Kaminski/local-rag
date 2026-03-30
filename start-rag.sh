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
