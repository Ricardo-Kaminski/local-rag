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
