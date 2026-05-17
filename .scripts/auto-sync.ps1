# Obsidian Vault auto-sync script
# Triggered by Windows Task Scheduler every 10 minutes

$ErrorActionPreference = "Stop"
$vaultPath = "C:\Users\34406\Documents\Obsidian Vault"
$scriptDir = Join-Path $vaultPath ".scripts"
$logFile = Join-Path $scriptDir "sync-log.txt"
$statusFile = Join-Path $vaultPath "_sync_status.md"

Set-Location $vaultPath
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Log {
    param([string]$Message)
    $line = "[$timestamp] $Message"
    Add-Content -Path $logFile -Value $line
    $lines = Get-Content $logFile -Tail 100 -ErrorAction SilentlyContinue
    if ($lines) { $lines | Set-Content $logFile }
}

function Show-Toast {
    param([string]$Title, [string]$Message, [bool]$IsError)
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        $balloonIcon = if ($IsError) { "Error" } else { "Info" }
        $icon = if ($IsError) {
            [System.Drawing.SystemIcons]::Error
        } else {
            [System.Drawing.SystemIcons]::Information
        }
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = $icon
        $notify.Visible = $true
        $notify.BalloonTipTitle = $Title
        $notify.BalloonTipText = $Message
        $notify.BalloonTipIcon = $balloonIcon
        $notify.ShowBalloonTip(8000)
        Start-Sleep -Seconds 2
        $notify.Visible = $false
        $notify.Dispose()
    } catch {
        # Toast unavailable in background context; logged to file instead
    }
}

function Update-StatusFile {
    param([string]$Status, [string]$Detail)
    $icon = switch ($Status) {
        "success" { "OK" }
        "warning" { "WARN" }
        "failure" { "FAIL" }
    }
    $content = @"
# Sync Status

**[$icon] $Status** at $timestamp

$Detail
"@
    $content | Set-Content $statusFile
}

# ── Step 1: Stage & Commit local changes ──
$changes = git status --porcelain 2>&1
if (-not $changes) {
    # No local changes, try to pull and push anyway (catch up with remote)
    try {
        $pullResult = git pull --rebase 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) {
            Write-Log "FAIL pull (no local changes)"
            Update-StatusFile "warning" "Pull failed (no local changes to commit)."
            exit 1
        }
        if ($pullResult -notmatch "Already up to date") {
            Write-Log "pull ok (remote updated)"
        } else {
            Write-Log "no changes, up to date"
        }
        Update-StatusFile "success" "No local changes, up to date with remote."
    } catch {
        Write-Log "FAIL pull exception: $_"
        Update-StatusFile "warning" "Pull exception: $_"
        exit 1
    }
    exit 0
}

git add -A 2>&1 | Out-Null
try {
    $commitMsg = "vault backup: $timestamp"
    $commitOutput = git commit -m $commitMsg 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-Log "FAIL commit"
        Show-Toast "Obsidian Sync FAILED" "git commit failed" $true
        Update-StatusFile "failure" "Commit failed.`n`nOutput:`n$commitOutput"
        exit 1
    }
    Write-Log "commit ok"
} catch {
    Write-Log "FAIL commit exception: $_"
    Show-Toast "Obsidian Sync FAILED" "Commit error" $true
    Update-StatusFile "failure" "Commit exception: $_"
    exit 1
}

# ── Step 2: Pull from remote (rebase local commit on top) ──
try {
    $pullResult = git pull --rebase 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-Log "FAIL pull"
        Show-Toast "Obsidian Sync FAILED" "git pull failed after commit" $true
        Update-StatusFile "failure" "Commit succeeded but pull failed.`n`nOutput:`n$pullResult"
        exit 1
    }
    Write-Log "pull ok"
} catch {
    Write-Log "FAIL pull exception: $_"
    Show-Toast "Obsidian Sync FAILED" "Pull error after commit" $true
    Update-StatusFile "failure" "Commit succeeded but pull exception: $_"
    exit 1
}

# ── Step 3: Push to GitHub ──
try {
    $pushOutput = git push 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-Log "FAIL push"
        Show-Toast "Obsidian Sync FAILED" "git push failed" $true
        Update-StatusFile "failure" "Commit + pull ok, but push failed (will retry).`n`nOutput:`n$pushOutput"
        exit 1
    }
    $changeCount = ($changes | Measure-Object -Line).Lines
    Write-Log "push ok, $changeCount files"
    $toastMsg = "Pushed $changeCount file(s) to GitHub at $timestamp"
    Show-Toast "Obsidian Synced" $toastMsg $false
    Update-StatusFile "success" "Synced $changeCount file(s) to GitHub."
} catch {
    Write-Log "FAIL push exception: $_"
    Show-Toast "Obsidian Sync FAILED" "Push error" $true
    Update-StatusFile "failure" "Commit + pull ok, but push exception: $_"
    exit 1
}
