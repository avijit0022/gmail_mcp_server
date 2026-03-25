# Gmail MCP Server - Setup Script

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

$VenvName = ".venv"

Write-Host "Setting up Gmail MCP Server"
Write-Host "============================"

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
