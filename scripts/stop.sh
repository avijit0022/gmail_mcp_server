#!/bin/bash
# Gmail MCP Server - Stop Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Stopping Gmail MCP Server"
echo "=========================="

# Load environment to get port
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

for PID_FILE in gmail_mcp.pid; do
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping $(basename $PID_FILE .pid) (PID: $PID)"
            kill $PID 2>/dev/null || true
            sleep 2
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID 2>/dev/null || true
            fi
        else
            echo "PID $PID from $(basename $PID_FILE) is stale (process not running)"
        fi
        rm -f "$PID_FILE"
    fi
done

# Fallback: kill any leftover process on the configured port
PORT="${GMAIL_MCP_SERVER_PORT:-9000}"
LEFTOVER=$(lsof -ti :"$PORT" 2>/dev/null)
if [ -n "$LEFTOVER" ]; then
    echo "Killing leftover process on port $PORT (PID: $LEFTOVER)"
    kill -9 $LEFTOVER 2>/dev/null || true
fi

echo "Gmail MCP server stopped"
