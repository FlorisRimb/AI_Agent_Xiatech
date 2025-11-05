#!/bin/bash

prefix_logs() {
  local prefix="$1"
  while IFS= read -r line; do
    echo "[$prefix] $line"
  done
}

uvicorn main:app --host 0.0.0.0 --port 8000 --reload 2>&1 | prefix_logs "FastAPI" &
FASTAPI_PID=$!

python -u mcp_server.py 2>&1 | prefix_logs "MCP" &
MCP_PID=$!

cleanup() {
    echo "Stopping services..."
    kill $FASTAPI_PID $MCP_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

wait $FASTAPI_PID $MCP_PID