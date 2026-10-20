<#
.SYNOPSIS
    Test UiWorkerProbe using its session-only control API and capture the result.
.DESCRIPTION
    Leave Sea Power running in a fresh O10 mission. The default Off mode records
    15 seconds of new map errors, requests UiWorkerProbe off, verifies a fresh
    reply from this game process, and records another 15 seconds. It leaves the
    worker off until the game restarts. On restores it in the same session;
    Status only requests a fresh status report. No game files, load order, mod
    selection, aircraft definitions, or Git branches are changed.
#>
[CmdletBinding()]
param(
    [ValidateSet('Off', 'On', 'Status')][string]$Mode = 'Off',
    [ValidateRange(5, 30)][int]$Seconds = 15,
    [string]$UserDataDirectory,
    [string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$SESTGames = @(Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue | Sort-Object Id -Unique)
if ($SESTGames.Count -ne 1) { throw 'Run one copy of Sea Power, start a fresh O10 mission, and leave it running.' }
$SESTGamePid = $SESTGames[0].Id
if (-not $UserDataDirectory) { $UserDataDirectory = Join-Path $env:USERPROFILE 'AppData\LocalLow\Triassic Games\Sea Power' }
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $env:USERPROFILE 'Downloads' }
$SESTLive = Join-Path $UserDataDirectory 'Mods\UiWorkerProbe\live'
$SESTStatusPath = Join-Path $SESTLive 'status.txt'
$SESTRequestPath = Join-Path $SESTLive 'mode.request'
$SESTLogPath = Join-Path $UserDataDirectory 'Player.log'
$SESTEncoding = New-Object Text.UTF8Encoding($false)
if (-not (Test-Path -LiteralPath $SESTStatusPath -PathType Leaf)) { throw 'UiWorkerProbe has no status file. This test cannot control it; preserve a normal map capture instead.' }
if (-not (Test-Path -LiteralPath $SESTLogPath -PathType Leaf)) { throw 'Player.log was not found. Pass -UserDataDirectory with the Sea Power user-data folder.' }
function Read-SharedText([string]$Path) {
    $SESTStream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, ([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
    try {
        $SESTReader = New-Object IO.StreamReader($SESTStream, [Text.Encoding]::UTF8, $true)
        try { return $SESTReader.ReadToEnd() } finally { $SESTReader.Dispose() }
    } finally { $SESTStream.Dispose() }
}
function Read-WorkerReply {
    $SESTText = Read-SharedText $SESTStatusPath
    $SESTValues = @{}
    foreach ($SESTLine in ($SESTText -split '\r?\n')) {
        if ($SESTLine -match '^([^=]+)=(.*)$') { $SESTValues[$Matches[1]] = $Matches[2] }
    }
    return [pscustomobject]@{ Text = $SESTText; Values = $SESTValues }
}
function Send-WorkerRequest([string]$Command) {
    $SESTSent = [DateTimeOffset]::UtcNow
    [IO.File]::WriteAllText($SESTRequestPath, $Command.ToLowerInvariant(), $SESTEncoding)
    $SESTDeadline = $SESTSent.AddSeconds(10)
    do {
        if (-not (Get-Process -Id $SESTGamePid -ErrorAction SilentlyContinue)) { throw 'Sea Power closed before the worker acknowledged the request.' }
        try {
            $SESTReply = Read-WorkerReply
            $SESTReplyUtc = [DateTimeOffset]::MinValue
            $SESTFresh = [DateTimeOffset]::TryParse([string]$SESTReply.Values['UTC'], [ref]$SESTReplyUtc)
            if ($SESTFresh -and $SESTReplyUtc -ge $SESTSent -and $SESTReply.Values['PID'] -eq [string]$SESTGamePid) {
                if ($Command -eq 'Off' -and $SESTReply.Values['Active'] -ne 'False') { throw 'The worker acknowledged Off but is still active.' }
                if ($Command -eq 'On' -and $SESTReply.Values['Active'] -ne 'True') { throw ('The worker did not enable: ' + $SESTReply.Values['Failure']) }
                return $SESTReply
            }
        } catch [IO.IOException] { }
        Start-Sleep -Milliseconds 200
    } while ([DateTimeOffset]::UtcNow -lt $SESTDeadline)
    throw 'No fresh reply from this game process within 10 seconds. The worker state is unconfirmed; restart Sea Power to reset the session.'
}
function Get-LogPosition {
    return [long](Get-Item -LiteralPath $SESTLogPath).Length
}
function Read-LogWindow([long]$StartOffset, [string]$Label) {
    $SESTStream = [IO.File]::Open($SESTLogPath, [IO.FileMode]::Open, [IO.FileAccess]::Read, ([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
    try {
        $SESTEnd = $SESTStream.Length
        $SESTRotated = $SESTEnd -lt $StartOffset
        if ($SESTRotated) { $StartOffset = 0 }
        $SESTClipped = ($SESTEnd - $StartOffset) -gt 10485760
        if ($SESTClipped) { $StartOffset = $SESTEnd - 10485760 }
        $SESTStream.Position = $StartOffset
        $SESTBytes = New-Object byte[] ([int]($SESTEnd - $StartOffset))
        $SESTRead = 0
        while ($SESTRead -lt $SESTBytes.Length) {
            $SESTChunk = $SESTStream.Read($SESTBytes, $SESTRead, $SESTBytes.Length - $SESTRead)
            if ($SESTChunk -le 0) { break }
            $SESTRead += $SESTChunk
        }
        $SESTText = [Text.Encoding]::UTF8.GetString($SESTBytes, 0, $SESTRead)
        return [pscustomobject]@{
            Label = $Label; Seconds = $Seconds; StartOffset = $StartOffset; EndOffset = $SESTEnd
            Partial = ($SESTRotated -or $SESTClipped -or $SESTRead -ne $SESTBytes.Length)
            MapUpdateStackEntries = [regex]::Matches($SESTText, 'MapKnownUnits::Update').Count
            NullReferenceEntries = [regex]::Matches($SESTText, '(?m)^NullReferenceException:').Count
            Text = $SESTText
        }
    } finally { $SESTStream.Dispose() }
}
$SESTStarted = [DateTimeOffset]::UtcNow
Write-Host 'Checking the worker in this running game...'
$SESTBefore = Send-WorkerRequest 'Status'
Write-Host ('UiWorkerProbe {0}; PID {1}; Active={2}' -f $SESTBefore.Values['Version'], $SESTBefore.Values['PID'], $SESTBefore.Values['Active'])
$SESTWindows = @()
if ($Mode -ne 'Status') {
    Write-Host ('Keep the mission running: recording {0} seconds before {1}...' -f $Seconds, $Mode)
    $SESTOffset = Get-LogPosition
    Start-Sleep -Seconds $Seconds
    $SESTWindows += Read-LogWindow $SESTOffset 'before'
    $SESTAfter = Send-WorkerRequest $Mode
    Write-Host ('Acknowledged by PID {0}: Active={1}. Recording another {2} seconds...' -f $SESTGamePid, $SESTAfter.Values['Active'], $Seconds)
    $SESTOffset = Get-LogPosition
    Start-Sleep -Seconds $Seconds
    $SESTWindows += Read-LogWindow $SESTOffset 'after'
    # Refresh counters after the observation window; a startup status is stale.
    $SESTFinal = Send-WorkerRequest 'Status'
} else { $SESTAfter = $SESTBefore; $SESTFinal = $SESTBefore }
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$SESTStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$SESTSuffix = [guid]::NewGuid().ToString('N').Substring(0, 6)
$SESTStage = Join-Path ([IO.Path]::GetTempPath()) ('SEST-map-worker-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $SESTStage | Out-Null
function Write-ReviewText([string]$Name, [string]$Text) {
    if ($env:USERPROFILE) { $Text = $Text.Replace($env:USERPROFILE, '<USERPROFILE>').Replace($env:USERPROFILE.Replace('\', '/'), '<USERPROFILE>') }
    [IO.File]::WriteAllText((Join-Path $SESTStage $Name), $Text, $SESTEncoding)
}
Write-ReviewText 'worker-before.txt' $SESTBefore.Text
Write-ReviewText 'worker-after-command.txt' $SESTAfter.Text
Write-ReviewText 'worker-final.txt' $SESTFinal.Text
foreach ($SESTWindow in $SESTWindows) { Write-ReviewText ($SESTWindow.Label + '-Player.log') $SESTWindow.Text }
$SESTReport = [ordered]@{
    capture_version = 1; mission_requested = 'Southern Watch O10 - Ballistic Shield'
    started_utc = $SESTStarted.ToString('o'); finished_utc = [DateTimeOffset]::UtcNow.ToString('o')
    game_pid = $SESTGamePid; command = $Mode; initial_active = $SESTBefore.Values['Active']
    final_active = $SESTFinal.Values['Active']; final_failure = $SESTFinal.Values['Failure']
    request_acknowledged_by_current_process = $true
    windows = @($SESTWindows | Select-Object -Property @('Label', 'Seconds', 'StartOffset', 'EndOffset', 'Partial', 'MapUpdateStackEntries', 'NullReferenceEntries'))
    game_files_or_mod_selection_changed = $false
    note = 'Session control only. Off leaves Harmony hooks installed but bypasses worker processing. Log counts do not establish aircraft visibility or a root cause.'
}
Write-ReviewText 'review.json' ($SESTReport | ConvertTo-Json -Depth 6)
# Freeze and hash all inputs before opening the manifest, avoiding self-hashing.
$SESTFiles = @(Get-ChildItem -LiteralPath $SESTStage -File)
$SESTManifest = @(foreach ($SESTFile in $SESTFiles) {
    [pscustomobject]@{ Path = $SESTFile.Name; Bytes = $SESTFile.Length; SHA256 = (Get-FileHash -LiteralPath $SESTFile.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
})
$SESTManifest | Export-Csv -LiteralPath (Join-Path $SESTStage 'file-manifest.csv') -NoTypeInformation -Encoding UTF8
$SESTZip = Join-Path $OutputDirectory ('SEST-map-worker-' + $SESTStamp + '-' + $SESTSuffix + '.zip')
Compress-Archive -Path (Join-Path $SESTStage '*') -DestinationPath $SESTZip
Remove-Item -LiteralPath $SESTStage -Recurse -Force
foreach ($SESTWindow in $SESTWindows) { Write-Host ('{0}: {1} map-update stack entries; partial={2}' -f $SESTWindow.Label, $SESTWindow.MapUpdateStackEntries, $SESTWindow.Partial) }
Write-Host ('UiWorkerProbe Active={0}; no mod reinstall. Restart Sea Power to reset this session.' -f $SESTFinal.Values['Active'])
Write-Host ('Capture ready: ' + $SESTZip)
Write-Host 'Check the Eagles and UAV labels, then attach the capture ZIP with your observations.'
