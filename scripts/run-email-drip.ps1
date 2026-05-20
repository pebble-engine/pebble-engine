# Pebble Email Drip — hidden runner for the Windows scheduled task.
#
# Why this exists:
#   - The previous task action was a bare `curl` command with the
#     PEBBLE_INTERNAL_KEY baked into the task XML in plain text.
#     That meant every key rotation required re-creating the task,
#     AND any user who could read task XML (or saw the task surface
#     in a tool like Get-ScheduledTask) could pull the key.
#   - It also opened a brief curl console window every hour because
#     `curl.exe` runs as a console app when launched directly by
#     the Task Scheduler.
#
# What this script does:
#   - Reads PEBBLE_INTERNAL_KEY from .env at run time (one source
#     of truth; rotations are zero-touch).
#   - POSTs to /api/internal/process-email-drip with -UseBasicParsing
#     so PowerShell doesn't try to render a UI.
#   - Runs entirely in PowerShell — no console window when invoked
#     with `-WindowStyle Hidden`.
#   - Soft-fails (writes a one-line error to a sibling log) if the
#     engine isn't running. Doesn't pop up an error dialog.
#
# How to wire it into the scheduled task:
#   $action = New-ScheduledTaskAction `
#     -Execute "powershell.exe" `
#     -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PSScriptRoot\run-email-drip.ps1`""
#   Set-ScheduledTask -TaskName "Pebble Email Drip" -Action $action

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot  = Split-Path -Parent $scriptDir
$envFile   = Join-Path $repoRoot '.env'
$logFile   = Join-Path $scriptDir 'run-email-drip.log'

function Write-LogLine([string]$msg) {
    $stamp = Get-Date -Format 'yyyy-MM-ddTHH:mm:ss'
    Add-Content -Path $logFile -Value "$stamp $msg"
}

try {
    if (-not (Test-Path $envFile)) {
        Write-LogLine "ERROR .env not found at $envFile"
        exit 1
    }

    # Read PEBBLE_INTERNAL_KEY from .env — ignores comments, handles
    # quoted + unquoted values, never echoes the value.
    $line = Get-Content $envFile | Where-Object { $_ -match '^\s*PEBBLE_INTERNAL_KEY\s*=' } | Select-Object -First 1
    if (-not $line) {
        Write-LogLine "ERROR PEBBLE_INTERNAL_KEY not found in .env"
        exit 1
    }
    $key = $line -replace '^\s*PEBBLE_INTERNAL_KEY\s*=\s*', '' -replace '^["'']', '' -replace '["'']$', ''
    $key = $key.Trim()
    if (-not $key) {
        Write-LogLine "ERROR PEBBLE_INTERNAL_KEY is empty"
        exit 1
    }

    try {
        $resp = Invoke-WebRequest `
            -Uri 'http://localhost:8000/api/internal/process-email-drip' `
            -Method POST `
            -Headers @{ 'X-Internal-Key' = $key } `
            -UseBasicParsing `
            -TimeoutSec 30
        Write-LogLine ("OK status={0}" -f $resp.StatusCode)
    } catch [System.Net.WebException] {
        # Engine probably not running. Soft-fail; no popup.
        Write-LogLine ("WARN engine unreachable: {0}" -f $_.Exception.Message)
        exit 0
    }
} catch {
    Write-LogLine ("FAIL {0}" -f $_.Exception.Message)
    exit 1
} finally {
    # Cap the log at ~10 KB so it doesn't grow unbounded over months.
    if (Test-Path $logFile) {
        $size = (Get-Item $logFile).Length
        if ($size -gt 10240) {
            Get-Content $logFile -Tail 50 | Set-Content $logFile
        }
    }
}
