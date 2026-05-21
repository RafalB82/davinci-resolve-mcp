@echo off
title DaVinci Resolve MCP Launcher

echo [1/3] Starting DaVinci Resolve Studio...
start "" "C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"

echo Waiting for Resolve to initialize (20s)...
timeout /t 20 /nobreak >nul

echo [2/3] Starting MCP SSR server...
cd /d C:\Users\Rafal\davinci-resolve-mcp
start "DaVinciMCP" /min ".\venv\Scripts\python" "src\sse_server.py" --full --host 0.0.0.0 --port 8765

echo [3/3] DaVinci Resolve MCP ready on http://192.168.100.126:8765/mcp
echo.
echo Close this window to stop the server.
echo.
pause
