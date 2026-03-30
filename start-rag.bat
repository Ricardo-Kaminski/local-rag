@echo off
title Local RAG - Iniciando...
echo ============================================
echo   Local RAG Stack - Iniciando servicos
echo ============================================
echo.

:: Verificar se Ollama esta rodando (necessario para embeddings)
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
pause
