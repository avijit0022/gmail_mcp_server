# Gmail MCP Server - Start Script

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

$VenvName = ".venv"

Write-Host "Starting Gmail MCP Server"
Write-Host "=========================="

# Load environment from .env
if (Test-Path "$ProjectRoot\.env") {
    Write-Host "Loading environment from .env"
    Get-Content "$ProjectRoot\.env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
} else {
    Write-Warning "No .env file found"
}

# Check venv
if (-not (Test-Path $VenvName)) {
    Write-Error "ERROR: Virtual environment not found. Run scripts\setup.ps1 first."
    exit 1
}

& "$VenvName\Scripts\activate.ps1"

# Start Gmail MCP server
Write-Host "Starting Gmail MCP server..."
$LogFile = Join-Path $ProjectRoot "gmail_mcp.log"
$PidFile = Join-Path $ProjectRoot "gmail_mcp.pid"

$proc = Start-Process -FilePath "python" `
    -ArgumentList "gmail_mcp_server.py" `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput $LogFile `
    -RedirectStandardError $LogFile `
    -NoNewWindow `
    -PassThru

Start-Sleep -Seconds 2

if (-not $proc.HasExited) {
    $proc.Id | Out-File -FilePath $PidFile -Encoding ascii
    $host_val = if ($env:GMAIL_MCP_SERVER_HOST) { $env:GMAIL_MCP_SERVER_HOST } else { "localhost" }
    $port_val = if ($env:GMAIL_MCP_SERVER_PORT) { $env:GMAIL_MCP_SERVER_PORT } else { "9000" }
    Write-Host ""
    Write-Host "Gmail MCP server started!"
    Write-Host "  - Server: http://${host_val}:${port_val}"
    Write-Host "  - Logs:   gmail_mcp.log"
} else {
    Write-Error "ERROR: Gmail MCP server failed to start. Check gmail_mcp.log"
    exit 1
}
