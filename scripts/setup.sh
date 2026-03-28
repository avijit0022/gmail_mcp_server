#!/bin/bash
# Gmail MCP Server - Setup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

VENV_NAME=".venv"

echo "Setting up Gmail MCP Server"
echo "============================"

# Check for Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 not found. Attempting to install..."
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y python3 python3-pip
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y python3 python3-pip
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -Sy --noconfirm python python-pip
    elif command -v brew >/dev/null 2>&1; then
        brew install python3
    else
        echo "ERROR: Could not install Python3 automatically."
        echo "Please install Python 3.10+ manually from https://www.python.org/downloads/"
        exit 1
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo "ERROR: Python3 installation failed."
        exit 1
    fi
    echo "Python3 installed successfully."
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "Found $PYTHON_VERSION"

# Check for uv or pip
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if command_exists uv; then
    echo "Using uv for package installation"
    uv venv "$VENV_NAME" --python python3
    source "$VENV_NAME/bin/activate"
    uv pip install -r requirements.txt
elif command_exists pip; then
    echo "Using pip for package installation"
    python3 -m venv "$VENV_NAME"
    source "$VENV_NAME/bin/activate"
    pip install -r requirements.txt
else
    echo "ERROR: Neither uv nor pip found. Please install one."
    exit 1
fi

# Create .env if missing
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.template"
    cp .env.template .env
    echo "Please edit .env with your configuration"
fi

echo ""
echo "Setup complete!"
echo "Next steps:"
echo "  1. Edit .env and set ACCESS_TOKEN to your Gmail App Password"
echo "  2. Run: bash scripts/start.sh"
