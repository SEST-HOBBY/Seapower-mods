<# Resolve the captured default UI-key collisions without replacing custom settings. #>
[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$GameDir,[switch]$CheckOnly)
$ErrorActionPreference = 'Stop'

if (Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue) {
    throw 'Close Sea Power before configuring its UI keys.'
}
$configDir = Join-Path $GameDir 'BepInEx/config'
if (-not $CheckOnly) { New-Item -ItemType Directory -Force -Path $configDir | Out-Null }
$script:SestUiKeyChangeRequired = $false

function Set-DefaultKey([string]$File, [string]$Section, [string]$Key, [string[]]$Defaults, [string]$Value) {
    $path = Join-Path $configDir $File
    $text = ''; $bom = $false
    if (Test-Path -LiteralPath $path) {
        $bytes = [IO.File]::ReadAllBytes($path)
        $bom = $bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191
        $text = [Text.Encoding]::UTF8.GetString($bytes)
        if ($bom) { $text = $text.Substring(1) }
    }
    $nl = "`n"; if ($text.Contains("`r`n")) { $nl = "`r`n" }
    $pattern = '(?ms)^\[' + [regex]::Escape($Section) + '\][^\r\n]*\r?\n(.*?)(?=^\[|\z)'
    $sectionMatch = [regex]::Match($text, $pattern)
    if ($sectionMatch.Success) {
        $body = $sectionMatch.Groups[1].Value
        $keyPattern = '(?m)^([ \t]*' + [regex]::Escape($Key) + '[ \t]*=[ \t]*)([^\r\n]*)'
        $keys = [regex]::Matches($body, $keyPattern)
        if ($keys.Count -gt 1) { throw ('Duplicate key in ' + $path + ': ' + $Key) }
        if ($keys.Count -eq 1) {
            $keyMatch = $keys[0]; $current = $keyMatch.Groups[2].Value.Trim()
            if (($current -replace '\s', '') -ieq ($Value -replace '\s', '')) { return }
            $wasDefault = @($Defaults | Where-Object { ($_ -replace '\s', '') -ieq ($current -replace '\s', '') }).Count -gt 0
            if (-not $wasDefault) {
                if (-not $CheckOnly) { Write-Host ('  kept custom binding: ' + $Key + ' = ' + $current) }
                return
            }
            $offset = $sectionMatch.Groups[1].Index + $keyMatch.Groups[2].Index
            $newText = $text.Substring(0, $offset) + $Value + $text.Substring($offset + $keyMatch.Groups[2].Length)
        } else {
            $offset = $sectionMatch.Groups[1].Index + $body.Length
            $newText = $text.Insert($offset, $nl + $Key + ' = ' + $Value + $nl)
        }
    } else {
        $newText = $text + $nl + '[' + $Section + ']' + $nl + $Key + ' = ' + $Value + $nl
    }
    $script:SestUiKeyChangeRequired = $true
    if ($CheckOnly) { return }
    $backup = $path + '.sest-ui-keys.bak'
    if ((Test-Path -LiteralPath $path) -and -not (Test-Path -LiteralPath $backup)) {
        [IO.File]::Copy($path, $backup)
    }
    [IO.File]::WriteAllText($path, $newText, (New-Object Text.UTF8Encoding($bom)))
    Write-Host ('  UI key: ' + $Key + ' = ' + $Value)
}

# Contacts keeps its existing bottom-bar control. Free its default F6 key for
# Topography's look cycle, preserving unrelated/custom shortcuts and UI state.
Set-DefaultKey 'com.seapower.contactlog.cfg' 'Input' 'ToggleWindow' 'F6' 'None'
Set-DefaultKey 'dev.sewerlabs.seapowertopo.cfg' '2. Overlay' 'Toggle key' 'F6' 'F7'
Set-DefaultKey 'dev.sewerlabs.seapowertopo.cfg' '2. Overlay' 'Look key' @('F6 + LeftShift','F7 + LeftShift') 'F6'
# The strike planner owns F8. A diagnostic probe walks types/UI and can stall
# the game, so leave the default probe unbound; custom probe shortcuts survive.
Set-DefaultKey 'com.seapower.contactlog.cfg' 'Input' 'RunProbe' 'F8' 'None'
if ($CheckOnly) { [pscustomobject]@{ Needed=$script:SestUiKeyChangeRequired } }
