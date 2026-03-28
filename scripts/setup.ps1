# Gmail MCP Server - Setup Script

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

$VenvName = ".venv"

Write-Host "Setting up Gmail MCP Server"
Write-Host "============================"

# Check for Python
$hasPython = $null -ne (Get-Command python -ErrorAction SilentlyContinue)

if (-not $hasPython) {
    Write-Host "Python not found. Attempting to install..."
    $hasWinget = $null -ne (Get-Command winget -ErrorAction SilentlyContinue)
    $hasChoco  = $null -ne (Get-Command choco  -ErrorAction SilentlyContinue)
    $hasScoop  = $null -ne (Get-Command scoop  -ErrorAction SilentlyContinue)

    if ($hasWinget) {
        winget install --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    } elseif ($hasChoco) {
        choco install python3 -y
    } elseif ($hasScoop) {
        scoop install python
    } else {
        Write-Error "ERROR: Could not install Python automatically."
        Write-Host "Please install Python 3.10+ from https://www.python.org/downloads/"
        exit 1
    }

    # Refresh PATH so the current session picks up the new install
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

    $hasPython = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
    if (-not $hasPython) {
        Write-Error "ERROR: Python installation failed. You may need to restart your terminal."
        exit 1
    }
    Write-Host "Python installed successfully."
}

$pythonVersion = python --version 2>&1
Write-Host "Found $pythonVersion"

# Check for uv or pip
$hasUv  = $null -ne (Get-Command uv  -ErrorAction SilentlyContinue)
$hasPip = $null -ne (Get-Command pip -ErrorAction SilentlyContinue)

if ($hasUv) {
    Write-Host "Using uv for package installation"
    uv venv $VenvName
    & "$VenvName\Scripts\activate.ps1"
    uv pip install -r requirements.txt
} elseif ($hasPip) {
    Write-Host "Using pip for package installation"
    python -m venv $VenvName
    & "$VenvName\Scripts\activate.ps1"
    pip install -r requirements.txt
} else {
    Write-Error "ERROR: Neither uv nor pip found. Please install one."
    exit 1
}

# Create .env if missing
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.template"
    Copy-Item ".env.template" ".env"
    Write-Host "Please edit .env with your configuration"
}

Write-Host ""
Write-Host "Setup complete!"
Write-Host "Next steps:"
Write-Host "  1. Edit .env and set ACCESS_TOKEN to your Gmail App Password"
Write-Host "  2. Run: .\scripts\start.ps1"
