# Non-destructive Windows test launcher. Does not modify the stock game files.
[CmdletBinding()]
param(
    [string]$GameRoot = 'C:\Program Files (x86)\Steam\steamapps\common\Sea Power',
    [ValidateSet('Hormuz','Breakthrough')][string]$Mission = 'Hormuz',
    [ValidateSet('front','grid')][string]$Mode = 'front',
    [switch]$Install
)
$ErrorActionPreference='Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$stream = Join-Path $GameRoot 'Sea Power_Data\StreamingAssets'
$src = if ($Mission -eq 'Hormuz') {
    Join-Path $stream 'original\missions\NATO\Hormuz.ini'
} else {
    Join-Path $stream 'original\missions\Warsaw Pact\Breakthrough.ini'
}
if (-not (Test-Path -LiteralPath $src -PathType Leaf)) { throw "Vanilla source scenario was not found: $src. Pass -GameRoot to your Steam install directory." }
$py = Get-Command py -ErrorAction SilentlyContinue
$pythonExe = if ($py) { 'py' } else { 'python' }
if (-not (Get-Command $pythonExe -ErrorAction SilentlyContinue)) {throw 'Python 3 required. Install Python 3 or run tools\patch_vanilla_mission.py from an existing Python setup.'}
$out = Join-Path $root 'examples\MNO-Environmental-Playtest'
$hashBefore = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash
& $pythonExe $(if ($pythonExe -eq 'py') {'-3'}) (Join-Path $root 'tools\patch_vanilla_mission.py') --source $src --output-dir $out --mode $Mode
if ($LASTEXITCODE -ne 0) { throw 'Weather scenario generator returned an error.' }
$hashAfter = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash
if ($hashBefore -ne $hashAfter) { throw 'WARNING: Source hash changed unexpectedly; generator should never modify source.' }
Write-Host "Original source unchanged SHA256: $hashAfter" -ForegroundColor Green
if ($Install) {
  $target = Join-Path $stream 'content\MNO-Environmental-Playtest'
  if (Test-Path -LiteralPath $target) { throw "Installation already exists: $target. Inspect/remove it manually; this script never overwrites an installed mod." }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
  Copy-Item -LiteralPath $out -Destination $target -Recurse -ErrorAction Stop
  Write-Host "Installed LOCAL playtest mod to: $target" -ForegroundColor Cyan
  Write-Host 'Enable the local mod in Sea Power if applicable, then launch MNO Weather Lab from the Scenarios menu.'
} else {
  Write-Host "Generated isolated playtest folder: $out" -ForegroundColor Cyan
  Write-Host 'Add -Install to copy it into StreamingAssets\content without changing original missions.'
}
Write-Host 'No Steam upload, no Git push, and no R15 overwrite occurred.'
