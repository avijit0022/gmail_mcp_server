#!/usr/bin/env python3
"""Gmail MCP Server - Cross-Platform Stop Script

Works on both Linux/macOS and Windows.

Usage:
    python  scripts/stop.py
    python3 scripts/stop.py
"""

import os
import sys
import time
import signal
import platform
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
PID_FILE = PROJECT_ROOT / "gmail_mcp.pid"
IS_WINDOWS = platform.system() == "Windows"


# ── Helpers ──────────────────────────────────────────────────────────────────

def load_env():
    """Load variables from .env into os.environ."""
    if not ENV_FILE.exists():
        return
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


def kill_pid(pid, forceful=False):
    """Kill a process by PID."""
    try:
        if IS_WINDOWS:
            flag = "/F" if forceful else ""
            cmd = ["taskkill", "/PID", str(pid)]
            if forceful:
                cmd.append("/F")
            subprocess.run(cmd, capture_output=True)
        else:
            os.kill(pid, signal.SIGKILL if forceful else signal.SIGTERM)
    except (OSError, ProcessLookupError):
        pass


def find_pid_on_port(port):
    """Return list of PIDs listening on the given port."""
    pids = []
    try:
        if IS_WINDOWS:
            result = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if parts:
                        pids.append(int(parts[-1]))
        else:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], capture_output=True, text=True
            )
            for pid_str in result.stdout.split():
                pids.append(int(pid_str.strip()))
    except Exception:
        pass
    return list(set(pids))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.chdir(PROJECT_ROOT)

    print("=" * 45)
    print("  Gmail MCP Server - Stop")
    print(f"  Platform: {platform.system()} {platform.machine()}")
    print("=" * 45)
    print()

    load_env()
    port = os.environ.get("GMAIL_MCP_SERVER_PORT", "9000")
    stopped = False

    # Stop via PID file
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        if is_running(pid):
            print(f"Stopping server (PID: {pid})...")
            kill_pid(pid)
            time.sleep(2)
            if is_running(pid):
                print(f"  Graceful stop failed, force-killing PID {pid}...")
                kill_pid(pid, forceful=True)
                time.sleep(1)
            if not is_running(pid):
                print(f"  Server stopped.")
                stopped = True
            else:
                print(f"  WARNING: Could not stop PID {pid}.")
        else:
            print(f"PID {pid} from gmail_mcp.pid is stale (process not running).")
        PID_FILE.unlink()
    else:
        print("No PID file found.")

    # Fallback: kill anything still on the port
    leftover = find_pid_on_port(port)
    if leftover:
        for pid in leftover:
            print(f"Killing leftover process on port {port} (PID: {pid})...")
            kill_pid(pid, forceful=True)
        stopped = True

    if stopped:
        print("\nGmail MCP server stopped.")
    else:
        print("\nNo running server found.")


if __name__ == "__main__":
    main()
