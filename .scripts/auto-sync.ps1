# Obsidian Vault auto-sync script
# Triggered by Windows Task Scheduler every 10 minutes

$vaultPath = "C:\Users\34406\Documents\Obsidian Vault"
Set-Location $vaultPath

# Pull first to avoid push conflicts (in case of multi-device sync)
git pull --rebase --quiet 2>$null

# Stage and commit if there are changes
$status = git status --porcelain
if ($status) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git add -A
    git commit -m "vault backup: $timestamp" --quiet
    git push --quiet
}
