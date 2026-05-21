@echo off
title DaVinci Resolve MCP Server

echo Checking if DaVinci Resolve is running...
tasklist /FI "IMAGENAME eq Resolve.exe" 2>nul | find /I "Resolve.exe" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] DaVinci Resolve is NOT running.
    echo Please start DaVinci Resolve Studio first, then press any key...
    pause >nul
)

echo Starting MCP SSE server (full mode)...
cd /d C:\Users\Rafal\davinci-resolve-mcp
".\venv\Scripts\python" "src\sse_server.py" --full --host 0.0.0.0 --port 8765

echo.
echo Server stopped.
pause
