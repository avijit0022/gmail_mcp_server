#!/usr/bin/env python3
"""Gmail MCP Server - Cross-Platform Start Script

Works on both Linux/macOS and Windows.

Usage:
    python  scripts/start.py
    python3 scripts/start.py
"""

import os
import sys
import time
import signal
import platform
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = PROJECT_ROOT / ".venv"
ENV_FILE = PROJECT_ROOT / ".env"
PID_FILE = PROJECT_ROOT / "gmail_mcp.pid"
LOG_FILE = PROJECT_ROOT / "gmail_mcp.log"
SERVER_SCRIPT = PROJECT_ROOT / "gmail_mcp_server.py"
IS_WINDOWS = platform.system() == "Windows"


# ── Helpers ──────────────────────────────────────────────────────────────────

def venv_python():
    """Return the path to the Python executable inside the venv."""
    if IS_WINDOWS:
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python")


def load_env():
    """Load variables from .env into os.environ."""
    if not ENV_FILE.exists():
        print("WARNING: No .env file found")
        return
    print("Loading environment from .env")
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip()


def is_running(pid):
    """Check whether a process with the given PID is alive."""
    try:
        if IS_WINDOWS:
            # signal 0 doesn't work reliably on Windows; use tasklist
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True, text=True
            )
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)
            return True
    except (OSError, ProcessLookupError):
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.chdir(PROJECT_ROOT)

    print("=" * 45)
    print("  Gmail MCP Server - Start")
    print(f"  Platform: {platform.system()} {platform.machine()}")
    print("=" * 45)
    print()

    # Check if already running
    if PID_FILE.exists():
        old_pid = int(PID_FILE.read_text().strip())
        if is_running(old_pid):
            print(f"Server is already running (PID: {old_pid})")
            print("Run 'python scripts/stop.py' first to restart.")
            sys.exit(1)
        else:
            print(f"Stale PID file found (PID {old_pid} not running). Cleaning up.")
            PID_FILE.unlink()

    # Check venv
    if not VENV_DIR.exists():
        print("ERROR: Virtual environment not found.")
        print("Run 'python scripts/setup.py' first.")
        sys.exit(1)

    # Load env
    load_env()

    host = os.environ.get("GMAIL_MCP_SERVER_HOST", "localhost")
    port = os.environ.get("GMAIL_MCP_SERVER_PORT", "9000")

    # Start server
    print("Starting Gmail MCP server...")
    log_handle = open(LOG_FILE, "w")

    if IS_WINDOWS:
        # CREATE_NEW_PROCESS_GROUP lets the child outlive this script
        proc = subprocess.Popen(
            [venv_python(), str(SERVER_SCRIPT)],
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            cwd=str(PROJECT_ROOT),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        proc = subprocess.Popen(
            [venv_python(), str(SERVER_SCRIPT)],
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            cwd=str(PROJECT_ROOT),
            start_new_session=True,
        )

    # Give it a moment to start (or crash)
    time.sleep(2)

    if proc.poll() is None:
        PID_FILE.write_text(str(proc.pid))
        print()
        print("Gmail MCP server started!")
        print(f"  - PID:    {proc.pid}")
        print(f"  - Server: http://{host}:{port}")
        print(f"  - Logs:   {LOG_FILE}")
    else:
        log_handle.close()
        print(f"ERROR: Server failed to start (exit code {proc.returncode}).")
        print(f"Check {LOG_FILE} for details.")
        sys.exit(1)

    log_handle.close()


if __name__ == "__main__":
    main()
