#!/bin/bash
# Gmail MCP Server - Start Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

VENV_NAME=".venv"

echo "Starting Gmail MCP Server"
echo "=========================="

# Load environment
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "Loading environment from .env"
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
else
    echo "WARNING: No .env file found"
fi

# Check venv
if [ ! -d "$VENV_NAME" ]; then
    echo "ERROR: Virtual environment not found. Run scripts/setup.sh first."
    exit 1
fi

source "$VENV_NAME/bin/activate"

# Start Gmail MCP server
echo "Starting Gmail MCP server..."
nohup python gmail_mcp_server.py > gmail_mcp.log 2>&1 &
PID=$!
sleep 2
if ps -p $PID > /dev/null 2>&1; then
    echo $PID > gmail_mcp.pid
    echo ""
    echo "Gmail MCP server started!"
    echo "  - Server: http://${GMAIL_MCP_SERVER_HOST:-localhost}:${GMAIL_MCP_SERVER_PORT:-9000}"
    echo "  - Logs:   gmail_mcp.log"
else
    echo "ERROR: Gmail MCP server failed to start. Check gmail_mcp.log"
    exit 1
fi
