[CmdletBinding()]
param(
    [string]$SshTarget = "strand@192.168.1.16",
    [string]$RemoteProject = "/volume1/docker/edge-dashboard",
    [string]$SshKey = "$HOME\.ssh\id_ed25519_edge_dashboard"
)

$ErrorActionPreference = "Stop"
$sshDirectory = Split-Path -Parent $SshKey
New-Item -ItemType Directory -Force -Path $sshDirectory | Out-Null
if (-not (Test-Path -LiteralPath $SshKey)) {
    & ssh-keygen -t ed25519 -f $SshKey -N '""' -C "edge-dashboard-deploy"
    if ($LASTEXITCODE -ne 0) { throw "ssh-keygen failed." }
}

$publicKey = (Get-Content -Raw -LiteralPath "$SshKey.pub").Trim()
$installKey = "umask 077; mkdir -p ~/.ssh; touch ~/.ssh/authorized_keys; grep -qxF '$publicKey' ~/.ssh/authorized_keys || echo '$publicKey' >> ~/.ssh/authorized_keys"
Write-Host "Enter the Synology login password once to install the deployment key."
& ssh -t -o StrictHostKeyChecking=yes $SshTarget $installKey
if ($LASTEXITCODE -ne 0) { throw "Could not install the SSH public key." }

$composeFile = "$RemoteProject/docker-compose.yml"
$sudoers = "strand ALL=(root) NOPASSWD: /usr/local/bin/docker compose -f $composeFile up -d --build`n"
$encodedSudoers = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($sudoers))
$installSudoers = "set -e; echo '$encodedSudoers' | base64 -d > /tmp/edge-dashboard-sudoers; chmod 440 /tmp/edge-dashboard-sudoers; sudo cp /tmp/edge-dashboard-sudoers /etc/sudoers.d/edge-dashboard; sudo chmod 440 /etc/sudoers.d/edge-dashboard; sudo test -r /etc/sudoers.d/edge-dashboard; rm -f /tmp/edge-dashboard-sudoers"
Write-Host "Enter the Synology sudo password once to install the restricted deployment rule."
& ssh -t -i $SshKey -o StrictHostKeyChecking=yes $SshTarget $installSudoers
if ($LASTEXITCODE -ne 0) { throw "Could not install or validate the sudo rule." }

& ssh -i $SshKey -o BatchMode=yes -o StrictHostKeyChecking=yes $SshTarget "sudo -n /usr/local/bin/docker compose -f '$composeFile' up -d --build"
if ($LASTEXITCODE -ne 0) { throw "No-touch verification failed." }
Write-Host "No-touch SSH and Docker rebuild are configured."
