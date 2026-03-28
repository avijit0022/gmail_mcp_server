#!/usr/bin/env python3
"""Gmail MCP Server - Cross-Platform Setup Script

Works on both Linux/macOS and Windows.

Usage:
    python  scripts/setup.py
    python3 scripts/setup.py
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = PROJECT_ROOT / ".venv"
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"
ENV_FILE = PROJECT_ROOT / ".env"
ENV_TEMPLATE = PROJECT_ROOT / ".env.template"
IS_WINDOWS = platform.system() == "Windows"


# ── Helpers ──────────────────────────────────────────────────────────────────

def run(cmd, **kwargs):
    """Run a command and exit on failure."""
    print(f"  > {' '.join(cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        sys.exit(result.returncode)


def find_command(name):
    """Return True if *name* is on PATH."""
    return shutil.which(name) is not None


def venv_python():
    """Return the path to the Python executable inside the venv."""
    if IS_WINDOWS:
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python")


def venv_pip():
    """Return the path to pip inside the venv."""
    if IS_WINDOWS:
        return str(VENV_DIR / "Scripts" / "pip.exe")
    return str(VENV_DIR / "bin" / "pip")


# ── Step 1: Verify Python ────────────────────────────────────────────────────

def check_python():
    print("[1/4] Checking Python installation...")
    version = sys.version_info
    print(f"  Found Python {version.major}.{version.minor}.{version.micro} "
          f"({platform.system()} {platform.machine()})")

    if version < (3, 10):
        print("\nERROR: Python 3.10+ is required.")
        print("Download from https://www.python.org/downloads/")
        sys.exit(1)


# ── Step 2: Create virtual environment ────────────────────────────────────────

def create_venv():
    print("\n[2/4] Creating virtual environment...")
    has_uv = find_command("uv")

    if VENV_DIR.exists():
        print(f"  Virtual environment already exists at {VENV_DIR}")
        return

    if has_uv:
        print("  Using uv")
        run(["uv", "venv", str(VENV_DIR), "--python", sys.executable])
    else:
        print("  Using built-in venv module")
        run([sys.executable, "-m", "venv", str(VENV_DIR)])

    print(f"  Created virtual environment at {VENV_DIR}")


# ── Step 3: Install dependencies ─────────────────────────────────────────────

def install_deps():
    print("\n[3/4] Installing dependencies...")
    has_uv = find_command("uv")

    if has_uv:
        print("  Using uv pip")
        run(["uv", "pip", "install", "-r", str(REQUIREMENTS),
             "--python", venv_python()])
    else:
        print("  Using pip")
        run([venv_python(), "-m", "pip", "install", "--upgrade", "pip"],)
        run([venv_python(), "-m", "pip", "install", "-r", str(REQUIREMENTS)])

    print("  Dependencies installed.")


# ── Step 4: Create .env file ─────────────────────────────────────────────────

def create_env():
    print("\n[4/4] Checking .env file...")
    if ENV_FILE.exists():
        print(f"  .env already exists at {ENV_FILE}")
    elif ENV_TEMPLATE.exists():
        shutil.copy2(ENV_TEMPLATE, ENV_FILE)
        print(f"  Created .env from .env.template")
        print("  ** Please edit .env and set ACCESS_TOKEN to your Gmail App Password **")
    else:
        print("  WARNING: No .env.template found. Skipping .env creation.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.chdir(PROJECT_ROOT)

    print("=" * 45)
    print("  Gmail MCP Server - Setup")
    print(f"  Platform: {platform.system()} {platform.machine()}")
    print("=" * 45)
    print()

    check_python()
    create_venv()
    install_deps()
    create_env()

    print()
    print("=" * 45)
    print("  Setup complete!")
    print("=" * 45)
    print()
    print("Next steps:")
    print("  1. Edit .env and set ACCESS_TOKEN to your Gmail App Password")
    if IS_WINDOWS:
        print("  2. Run: python scripts\\start.ps1")
        print("     or:  .\\scripts\\start.ps1")
    else:
        print("  2. Run: bash scripts/start.sh")


if __name__ == "__main__":
    main()
