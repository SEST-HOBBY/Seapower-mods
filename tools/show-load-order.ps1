<#
.SYNOPSIS
    Print the mod order Sea Power is actually using, with real names.

.DESCRIPTION
    Reads the live [LoadOrder] out of usersettings.ini and prints it as a
    numbered list, resolving each opaque workshop id to the mod's real name
    from mods-source\<id>\_info.ini. Without that resolution the list is 137
    lines of digits and tells you nothing.

    It then compares against data\load-order.tokens.txt and reports the four
    things that actually go wrong:
      * entries sitting in a different position to the canonical order
      * mods the game knows about that the canonical list does not
      * canonical entries the game has never seen
      * SEST packs that are present but DISABLED - the usual reason a patch
        appears to do nothing

    Read-only. It never writes to usersettings.ini; use set-mod-order.ps1 or
    fix-load-order.ps1 for that.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\tools\show-load-order.ps1

.EXAMPLE
    # Just the parts that differ from canonical, and the SEST packs
    powershell -ExecutionPolicy Bypass -File .\tools\show-load-order.ps1 -DiffOnly

.EXAMPLE
    # Write it to a file you can paste or attach
    powershell -ExecutionPolicy Bypass -File .\tools\show-load-order.ps1 -OutFile load-order.txt
#>
[CmdletBinding()]
param(
    [string]$SettingsPath = (Join-Path $env:USERPROFILE "AppData\LocalLow\Triassic Games\Sea Power\usersettings.ini"),
    [switch]$DiffOnly,
    [string]$OutFile
)

$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = Split-Path -Parent $scriptDir

if (-not (Test-Path -LiteralPath $SettingsPath)) { throw "settings file not found: $SettingsPath" }

function Read-Utf8([string]$Path) {
    # Mod names are UTF-8 and several are Chinese. Windows PowerShell 5.1
    # decodes Get-Content with the system ANSI codepage, which turns them into
    # mojibake, so decode explicitly.
    return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

# Console output needs to be UTF-8 too, or the names are mangled on the way out.
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

# --- workshop id -> mod name, from the exported configs ----------------------
$names = @{}
$modsSource = Join-Path $repoRoot "mods-source"
if (Test-Path -LiteralPath $modsSource) {
    foreach ($d in Get-ChildItem -LiteralPath $modsSource -Directory -ErrorAction SilentlyContinue) {
        $info = Join-Path $d.FullName "_info.ini"
        if (Test-Path -LiteralPath $info) {
            $m = [regex]::Match((Read-Utf8 $info), '(?m)^Name=(.+)$')
            if ($m.Success) { $names[$d.Name] = $m.Groups[1].Value.Trim() }
        }
        if (-not $names.ContainsKey($d.Name)) {
            # Some mods ship no _info.ini at all (the P-8 Poseidon, for one).
            # They ARE exported, so say what they contain rather than claiming
            # they are missing - the unit ids identify them well enough.
            $unit = Get-ChildItem -LiteralPath $d.FullName -File -Recurse -Filter "*.ini" `
                        -ErrorAction SilentlyContinue |
                    Where-Object { $_.Directory.Name -in @("aircraft","vessels","submarines","land_units") -and
                                   $_.Name -notlike "*_squadrons.ini" -and $_.Name -notlike "*_variants.ini" } |
                    Select-Object -First 1
            if ($unit) { $names[$d.Name] = "(no _info.ini - ships $($unit.Directory.Name)/$($unit.BaseName))" }
        }
    }
}
# Local SEST packs carry their name in the pack folder's own _info.ini.
foreach ($p in Get-ChildItem -LiteralPath (Join-Path $repoRoot "integration") -Directory -ErrorAction SilentlyContinue) {
    foreach ($pack in Get-ChildItem -LiteralPath $p.FullName -Directory -Filter "SEST_*" -ErrorAction SilentlyContinue) {
        $info = Join-Path $pack.FullName "_info.ini"
        if (Test-Path -LiteralPath $info) {
            $m = [regex]::Match((Read-Utf8 $info), '(?m)^Name=(.+)$')
            if ($m.Success) { $names[$pack.Name] = $m.Groups[1].Value.Trim() }
        }
    }
}

# --- the live order ----------------------------------------------------------
$text = Get-Content -LiteralPath $SettingsPath -Raw
$sec = [regex]::Match($text, "(?s)\[LoadOrder\]\r?\n(.*?)(?=\r?\n\[|$)")
if (-not $sec.Success) { throw "[LoadOrder] section not found in $SettingsPath" }
$activeCount = [int][regex]::Match($sec.Groups[1].Value, "NumberOfModFiles=(\d+)").Groups[1].Value

$live = New-Object System.Collections.Generic.List[object]
$seen = @{}
foreach ($em in [regex]::Matches($sec.Groups[1].Value, "Mod(\d+)Directory=([^,\r\n]+),(True|False)")) {
    if ([int]$em.Groups[1].Value -gt $activeCount) { continue }
    $tok = $em.Groups[2].Value
    if ($seen.ContainsKey($tok)) { continue }
    $seen[$tok] = $true
    $live.Add([pscustomobject]@{ Token = $tok; Enabled = ($em.Groups[3].Value -eq "True") })
}

$canonical = @()
$tokensPath = Join-Path $repoRoot "data\load-order.tokens.txt"
if (Test-Path -LiteralPath $tokensPath) {
    $canonical = @(Get-Content -LiteralPath $tokensPath | Where-Object { $_ -and $_ -notmatch "^#" })
}

# Canonical position of each token, counting only ones the game actually has.
$expected = @($canonical | Where-Object { $seen.ContainsKey($_) })
$expectedIndex = @{}
for ($i = 0; $i -lt $expected.Count; $i++) { $expectedIndex[$expected[$i]] = $i + 1 }

$out = New-Object System.Collections.Generic.List[string]
function Emit([string]$s) { $out.Add($s); Write-Host $s }

Emit ""
Emit "Sea Power load order - $($live.Count) entries (NumberOfModFiles=$activeCount)"
Emit "Settings: $SettingsPath"
Emit ("Canonical: {0} entries in data\load-order.tokens.txt" -f $canonical.Count)
Emit ("-" * 78)

$moved = 0
for ($i = 0; $i -lt $live.Count; $i++) {
    $e = $live[$i]
    $pos = $i + 1
    $want = if ($expectedIndex.ContainsKey($e.Token)) { $expectedIndex[$e.Token] } else { $null }
    $note = ""
    if ($null -eq $want) { $note = "  [not in canonical list]" }
    elseif ($want -ne $pos) { $note = "  [canonical position $want]"; $moved++ }
    $flag = if ($e.Enabled) { " " } else { "x" }
    $name = if ($names.ContainsKey($e.Token)) { $names[$e.Token] }
            else { "(NOT in mods-source - run tools\export-mod-configs.ps1)" }
    $line = "{0,4}. [{1}] {2,-24} {3}{4}" -f $pos, $flag, $e.Token, $name, $note
    if (-not $DiffOnly -or $note -or -not $e.Enabled -or $e.Token -like "SEST_*") { Emit $line }
}

Emit ("-" * 78)
Emit ("entries out of canonical position : {0}" -f $moved)

$unknown = @($live | Where-Object { $canonical -notcontains $_.Token })
if ($unknown) { Emit ("not in data\load-order.tokens.txt   : {0}" -f (($unknown | ForEach-Object { $_.Token }) -join ", ")) }

$notSeen = @($canonical | Where-Object { -not $seen.ContainsKey($_) })
if ($notSeen) { Emit ("canonical but the game has not seen : {0}" -f ($notSeen -join ", ")) }

$unexported = @($live | Where-Object { -not $names.ContainsKey($_.Token) })
if ($unexported) {
    Emit ("not in mods-source, so unvalidated  : {0}" -f
          (($unexported | ForEach-Object { $_.Token }) -join ", "))
    Emit "  (re-run tools\export-mod-configs.ps1 so the build scripts can see them)"
}
$noInfo = @($live | Where-Object { $names.ContainsKey($_.Token) -and $names[$_.Token] -like "(no _info.ini*" })
if ($noInfo) {
    Emit ("exported but ship no _info.ini      : {0}" -f
          (($noInfo | ForEach-Object { $_.Token }) -join ", "))
    Emit "  (harmless - they load fine, they just have no name to show)"
}

$off = @($live | Where-Object { -not $_.Enabled })
if ($off) { Emit ("DISABLED                            : {0}" -f (($off | ForEach-Object { $_.Token }) -join ", ")) }

$sestOff = @($live | Where-Object { $_.Token -like "SEST_*" -and -not $_.Enabled })
if ($sestOff) {
    Emit ""
    Emit ("WARNING: SEST packs installed but DISABLED - their patches do nothing: {0}" -f
          (($sestOff | ForEach-Object { $_.Token }) -join ", "))
}
if ($moved -eq 0 -and -not $unknown -and -not $sestOff) {
    Emit ""
    Emit "Order matches canonical and every SEST pack is enabled."
}

if ($OutFile) {
    $path = if ([System.IO.Path]::IsPathRooted($OutFile)) { $OutFile } else { Join-Path (Get-Location) $OutFile }
    [System.IO.File]::WriteAllLines($path, $out, [System.Text.Encoding]::UTF8)
    Write-Host ""
    Write-Host "Written to: $path"
}
