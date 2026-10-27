<# Correct the reviewed REDFOR metadata on the captured game build only. #>
[CmdletBinding()]
param(
    [string]$GameDirectory = 'C:\Program Files (x86)\Steam\steamapps\common\Sea Power',
    [string]$WorkshopContentDir = 'C:\Program Files (x86)\Steam\steamapps\workshop\content\1286220',
    [string]$BackupDirectory,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
function Get-SestRedforTree([string]$Directory) {
    if (@(Get-ChildItem -LiteralPath $Directory -Recurse -File -Filter *.dll).Count) { throw 'REDFOR now contains code; compatibility needs a new review.' }
    $records = @{}
    foreach ($file in @(Get-ChildItem -LiteralPath $Directory -Recurse -File -Filter *.ini | Where-Object { $_.Name -ine '_info.ini' })) {
        $relative = $file.FullName.Substring($Directory.TrimEnd('\','/').Length + 1).Replace('\','/').ToLowerInvariant()
        $records[$relative] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    [string[]]$keys = @($records.Keys); [Array]::Sort($keys, [StringComparer]::Ordinal)
    $text = New-Object Text.StringBuilder
    foreach ($key in $keys) { [void]$text.Append($key).Append("`n").Append($records[$key]).Append("`n") }
    $sha = [Security.Cryptography.SHA256]::Create()
    try { $digest = [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($text.ToString()))).Replace('-','').ToLowerInvariant() } finally { $sha.Dispose() }
    [pscustomobject]@{ Files=$keys.Count; SHA256=$digest }
}
function Get-SestRedforPlan([string]$WorkshopDirectory, [string]$NativeHash, [string]$GameVersion) {
    $folder = Join-Path $WorkshopDirectory '3732654992'; $info = Join-Path $folder '_info.ini'
    if (-not (Test-Path -LiteralPath $info)) { throw 'The reviewed REDFOR Workshop copy is missing.' }
    if ($GameVersion -ne '0.8.7' -or $NativeHash -ne 'eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd') { throw 'The REDFOR correction requires the captured Sea Power 0.8.7 build.' }
    $tree = Get-SestRedforTree $folder
    if ($tree.Files -ne 330 -or $tree.SHA256 -ne '7604ab8c65d409c29b6128350d34095d4a94086bb3d9928b0d8b28957410641f') { throw 'REDFOR definitions changed after review. Its compatibility declaration was left alone.' }
    $text = [IO.File]::ReadAllText($info)
    $hash = (Get-FileHash -LiteralPath $info -Algorithm SHA256).Hash.ToLowerInvariant()
    $marker = '; SEST marked this mod compatible (reviewed REDFOR 0.8.8 declaration on native 0.8.7); SETUP -RestoreModFiles puts it back'
    $already = $text.Contains($marker) -and $text -match '(?m)^ApproximateVersion=0\.8\.7\r?$'
    if (-not $already -and $hash -ne '6728cad1289c167e5555f6654657673fdfb157de15e2bcf8e7c3eb7be921ddff') { throw 'REDFOR metadata changed after review. No compatibility correction was applied.' }
    $replacement = if ($already) { $text } else { $text.Replace('ApproximateVersion=0.8.8', $marker + "`r`nApproximateVersion=0.8.7") }
    [pscustomobject]@{ Path=$info; Before=$hash; Text=$replacement; Already=$already }
}
function Invoke-SestRedforPlan($Plan,[string]$KeepDirectory) {
    if ($Plan.Already) { Write-Host '  [ok]   reviewed REDFOR metadata correction already applied' -ForegroundColor Green; return }
    if ((Get-FileHash -LiteralPath $Plan.Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Plan.Before) { throw 'REDFOR changed while the update was being prepared.' }
    New-Item -ItemType Directory -Force -Path $KeepDirectory | Out-Null
    $original = Join-Path $KeepDirectory '3732654992._info.ini'
    if (Test-Path -LiteralPath $original) {
        $oldHash = (Get-FileHash -LiteralPath $original -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($oldHash -ne $Plan.Before) {
            $archive = $original + '.before-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,6) + '.bak'
            Move-Item -LiteralPath $original -Destination $archive
        }
    }
    if (-not (Test-Path -LiteralPath $original)) { Copy-Item -LiteralPath $Plan.Path -Destination $original }
    $bytes = [IO.File]::ReadAllBytes($Plan.Path); $bom = $bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191
    try { [IO.File]::WriteAllText($Plan.Path, $Plan.Text, (New-Object Text.UTF8Encoding($bom))) }
    catch { Copy-Item -LiteralPath $original -Destination $Plan.Path -Force; throw }
    Write-Host '  [done] REDFOR 0.8.8 metadata corrected for the reviewed 0.8.7 installation; author file backed up' -ForegroundColor Green
}
if ($MyInvocation.InvocationName -eq '.') { return }
if (Get-Process -Name 'Sea Power','SeaPower' -ErrorAction SilentlyContinue) { throw 'Close Sea Power first.' }
$native = Join-Path $GameDirectory 'Sea Power_Data\Managed\Seapower-Scripts.dll'
if (-not (Test-Path -LiteralPath $native)) { throw 'Sea Power native assembly not found.' }
$version = $null
foreach ($changelog in @((Join-Path $GameDirectory 'changelog.txt'),(Join-Path $GameDirectory 'Sea Power_Data\changelog.txt'))) {
    if ($version -or -not (Test-Path -LiteralPath $changelog)) { continue }
    $match = [regex]::Match([IO.File]::ReadAllText($changelog),'(?m)^\d{1,2}-[A-Za-z]{3}-\d{4}:\s+(\d+\.\d+\.\d+)\s+Build')
    if ($match.Success) { $version = $match.Groups[1].Value }
}
$plan = Get-SestRedforPlan $WorkshopContentDir ((Get-FileHash -LiteralPath $native -Algorithm SHA256).Hash.ToLowerInvariant()) $version
if ($CheckOnly) { return $plan }
if ([string]::IsNullOrWhiteSpace($BackupDirectory)) {
    $local = [Environment]::GetFolderPath('LocalApplicationData'); if (-not $local) { $local = $env:LOCALAPPDATA }
    if (-not $local) { throw 'Pass a nonempty -BackupDirectory.' }
    $BackupDirectory = Join-Path $local 'SEST\compat-originals'
}
Invoke-SestRedforPlan $plan $BackupDirectory
