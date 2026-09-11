[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceJson,
    [string]$SshTarget = "strand@192.168.1.16",
    [string]$RemoteProject = "/volume1/docker/edge-dashboard",
    [string]$SshKey = "$HOME\.ssh\id_ed25519_edge_dashboard",
    [string]$PublicUrl = "http://192.168.1.16:8000/data/matches.json"
)

$ErrorActionPreference = "Stop"
$resolvedSource = (Resolve-Path -LiteralPath $SourceJson).Path
if (-not (Test-Path -LiteralPath $SshKey -PathType Leaf)) {
    throw "Dedicated SSH key not found: $SshKey. Run setup_no_touch.ps1 once."
}

$localText = Get-Content -Raw -LiteralPath $resolvedSource
$localData = $localText | ConvertFrom-Json
if ([string]::IsNullOrWhiteSpace($localData.updated) -or @($localData.matches).Count -lt 1) {
    throw "Source JSON does not match the dashboard contract."
}

$sshOptions = @("-i", $SshKey, "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=10")
& ssh @sshOptions $SshTarget "true"
if ($LASTEXITCODE -ne 0) { throw "Noninteractive SSH authentication failed. Run setup_no_touch.ps1 once." }

$remoteUpload = "$RemoteProject/data/matches.json.uploading"
& scp -O @sshOptions $resolvedSource "${SshTarget}:$remoteUpload"
if ($LASTEXITCODE -ne 0) { throw "SCP upload failed; the active dashboard file was not changed." }

$composeFile = "$RemoteProject/docker-compose.yml"
$deployCommand = "set -eu; cd '$RemoteProject'; test -s 'data/matches.json.uploading'; cp 'data/matches.json' 'data/matches.json.previous'; mv 'data/matches.json.uploading' 'data/matches.json'; sudo -n /usr/local/bin/docker compose -f '$composeFile' up -d --build"
& ssh @sshOptions $SshTarget $deployCommand
if ($LASTEXITCODE -ne 0) { throw "Remote install or Docker rebuild failed. The previous JSON is available as data/matches.json.previous." }

$separator = if ($PublicUrl.Contains("?")) { "&" } else { "?" }
$servedText = $null
for ($attempt = 1; $attempt -le 8; $attempt++) {
    try {
        $servedText = (Invoke-WebRequest -UseBasicParsing -Uri "$PublicUrl${separator}v=$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())" -TimeoutSec 20).Content
        break
    }
    catch {
        if ($attempt -eq 8) { throw "Deployment completed, but the public JSON remained unavailable: $($_.Exception.Message)" }
        Start-Sleep -Seconds 3
    }
}
$servedData = $servedText | ConvertFrom-Json
if ($servedData.updated -ne $localData.updated -or @($servedData.matches).Count -ne @($localData.matches).Count) {
    throw "Deployment completed, but the public JSON does not match the generated version."
}

[pscustomobject]@{
    deployed = $true
    updated = $servedData.updated
    matches = @($servedData.matches).Count
    url = $PublicUrl
} | ConvertTo-Json -Compress
