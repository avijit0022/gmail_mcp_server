# Gmail MCP Server - Stop Script

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "Stopping Gmail MCP Server"
Write-Host "=========================="

# Load environment to get port
$Port = "9000"
if (Test-Path "$ProjectRoot\.env") {
    Get-Content "$ProjectRoot\.env" | ForEach-Object {
        if ($_ -match '^\s*GMAIL_MCP_SERVER_PORT=(.+)$') {
            $Port = $matches[1].Trim()
        }
    }
}

# Stop via PID file
$PidFile = Join-Path $ProjectRoot "gmail_mcp.pid"
if (Test-Path $PidFile) {
    $Pid = Get-Content $PidFile
    $proc = Get-Process -Id $Pid -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "Stopping gmail_mcp (PID: $Pid)"
        Stop-Process -Id $Pid -Force
        Start-Sleep -Seconds 2
    } else {
        Write-Host "PID $Pid from gmail_mcp.pid is stale (process not running)"
    }
    Remove-Item $PidFile -Force
}

# Fallback: kill any process still holding the port
$netstat = netstat -ano | Select-String ":$Port\s"
foreach ($line in $netstat) {
    if ($line -match '\s+(\d+)$') {
        $LeftoverPid = $matches[1]
        Write-Host "Killing leftover process on port $Port (PID: $LeftoverPid)"
        Stop-Process -Id $LeftoverPid -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Gmail MCP server stopped"
