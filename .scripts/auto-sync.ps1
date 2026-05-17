# Obsidian Vault auto-sync script
# Triggered by Windows Task Scheduler every 10 minutes

$ErrorActionPreference = "Stop"
$vaultPath = "C:\Users\34406\Documents\Obsidian Vault"
$scriptDir = Join-Path $vaultPath ".scripts"
$logFile = Join-Path $scriptDir "sync-log.txt"
$statusFile = Join-Path $vaultPath "_sync_status.md"

Set-Location $vaultPath
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Log($Message) {
    $line = "[$timestamp] $Message"
    Add-Content -Path $logFile -Value $line
    $lines = Get-Content $logFile -Tail 100 -ErrorAction SilentlyContinue
    if ($lines) { $lines | Set-Content $logFile }
}

function Show-Toast($Title, $Message, $IsError) {
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        $balloonIcon = if ($IsError) { "Error" } else { "Info" }
        $icon = if ($IsError) { [System.Drawing.SystemIcons]::Error } else { [System.Drawing.SystemIcons]::Information }
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
    } catch { }
}

function Update-StatusFile($Status, $Detail) {
    $emoji = switch ($Status) {
        "success" { $([char]0x2705) }
        "offline" { $([char]0x1F310) }
        "warning" { $([char]0x26A0) }
        "failure" { $([char]0x274C) }
    }
    $content = @"
# Sync Status

$emoji **$Status** — $timestamp

$Detail
"@
    $content | Set-Content $statusFile
}

function Test-NetworkError($output) {
    # Return $true if the error is a transient network issue (VPN off / DNS blocked)
    $networkPatterns = @(
        "unable to access",
        "Could not connect",
        "Failed to connect",
        "Could not resolve host",
        "Connection refused",
        "Network is unreachable",
        "Connection timed out",
        "OpenSSL SSL_connect",
        "could not resolve proxy",
        "Recv failure",
        "Failed to receive",
        "error: RPC failed"
    )
    foreach ($pat in $networkPatterns) {
        if ($output -match [regex]::Escape($pat)) { return $true }
    }
    return $false
}

function Invoke-GitRemote($action) {
    # Runs a git remote operation. Returns "ok", "offline", or "fail".
    try {
        $output = (& git $action 2>&1 | Out-String)
        if ($LASTEXITCODE -eq 0) { return @{Result="ok"; Output=$output} }
        if (Test-NetworkError $output) { return @{Result="offline"; Output=$output} }
        return @{Result="fail"; Output=$output}
    } catch {
        if (Test-NetworkError $_.Exception.Message) { return @{Result="offline"; Output=$_.Exception.Message} }
        return @{Result="fail"; Output=$_.Exception.Message}
    }
}

# ── Step 1: Stage & Commit local changes ──
$changes = git status --porcelain 2>&1

if (-not $changes) {
    # No local changes — try to catch up with remote
    $r = Invoke-GitRemote "pull --rebase --autostash"
    if ($r.Result -eq "offline") {
        Write-Log "network down (no local changes)"
        Update-StatusFile "offline" "网络不可用，跳过同步。开 VPN 后自动恢复。"
        exit 0
    }
    if ($r.Result -eq "fail") {
        Write-Log "FAIL pull (no local changes)"
        Update-StatusFile "warning" "Pull failed.`n`n``````$($r.Output)``````"
        exit 1
    }
    if ($r.Output -notmatch "Already up to date") {
        Write-Log "pull ok (remote updated)"
    } else {
        Write-Log "no changes, up to date"
    }
    Update-StatusFile "success" "无本地变更，与远程同步。"
    exit 0
}

git add -A 2>&1 | Out-Null
try {
    $commitMsg = "vault backup: $timestamp"
    $commitOutput = git commit -m $commitMsg 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-Log "FAIL commit"
        Show-Toast "Obsidian Sync FAILED" "git commit failed" $true
        Update-StatusFile "failure" "Commit failed.`n`n``````$commitOutput``````"
        exit 1
    }
    Write-Log "commit ok"
} catch {
    Write-Log "FAIL commit exception: $_"
    Show-Toast "Obsidian Sync FAILED" "Commit error" $true
    Update-StatusFile "failure" "Commit exception: $_"
    exit 1
}

# ── Step 2: Pull from remote ──
$r = Invoke-GitRemote "pull --rebase --autostash"
if ($r.Result -eq "offline") {
    Write-Log "commit ok, network down on pull"
    Update-StatusFile "offline" "已本地 commit（`git log` 可查），等待网络恢复后自动 push。"
    exit 0
}
if ($r.Result -eq "fail") {
    Write-Log "FAIL pull"
    Show-Toast "Obsidian Sync FAILED" "git pull failed after commit" $true
    Update-StatusFile "failure" "Commit succeeded but pull failed.`n`n``````$($r.Output)``````"
    exit 1
}
Write-Log "pull ok"

# ── Step 3: Push to GitHub ──
$r = Invoke-GitRemote "push"
if ($r.Result -eq "offline") {
    Write-Log "commit+push ok, network down on push"
    Update-StatusFile "offline" "已本地 commit，等待网络恢复后自动 push。"
    exit 0
}
if ($r.Result -eq "fail") {
    Write-Log "FAIL push"
    Show-Toast "Obsidian Sync FAILED" "git push failed" $true
    Update-StatusFile "failure" "Commit + pull ok, but push failed.`n`n``````$($r.Output)``````"
    exit 1
}
$changeCount = ($changes | Measure-Object -Line).Lines
Write-Log "push ok, $changeCount files"
Show-Toast "Obsidian Synced" "Pushed $changeCount file(s) at $timestamp" $false
Update-StatusFile "success" "已同步 $changeCount 个文件到 GitHub。"
