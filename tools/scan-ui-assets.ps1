<#
.SYNOPSIS
    List the picture names built into Sea Power's own Unity data. Read only.

.DESCRIPTION
    The SEST pack replaces every loading-screen picture the game reads as a
    file (ui\backgrounds\loading_screen_1..80.png). Some screens still show the
    game's own pictures (10 Oct 2026: screens between menu pages, a first
    load, the Mod Manager), so those come from inside the game's Unity data,
    where no mod file stands in for them - the main menu's film did too, and
    the SEST plugin swaps it by its clip name. To swap a picture the same way
    the plugin needs its name.

    This reads the game's serialized data files (*.assets, level*,
    globalgamemanagers) and its own code DLLs - never runs them, never changes
    them - and writes every name in them that reads like a background,
    loading, splash or menu picture, plus every ui/ path the code names, to
    -OutFile. The data is a few GB, so the scan takes a minute or two; the
    third line of the output records each file's size, and the scan is
    skipped when nothing has changed since the last one.

    tools\capture-context.ps1 runs this; on its own:
        powershell -ExecutionPolicy Bypass -File .\tools\scan-ui-assets.ps1 -DataDir "<...>\Sea Power_Data"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$DataDir,
    [string]$OutFile = (Join-Path (Split-Path -Parent $PSScriptRoot) "data\install-snapshot\ui-assets.txt"),
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$pictureWords = '(?i)background|loading|load_?screen|splash|wallpaper|mod ?manager|modmanager|main_?menu|menu_?bg|title_?screen'
$codeWords = $pictureWords + '|(?<![A-Za-z0-9])ui[/\\]'
$maxPerFile = 400
$latin1 = [System.Text.Encoding]::GetEncoding(28591)

# Every printable run (up to 120 characters) around each match of $words in
# $text, trimmed. A Unity file stores a name as a plain run of characters, so
# the run around "background" is the name that holds it.
function Get-Runs([string]$text, [string]$words, [hashtable]$into) {
    foreach ($m in [regex]::Matches($text, $words)) {
        $from = [Math]::Max(0, $m.Index - 60)
        $win = $text.Substring($from, [Math]::Min($text.Length - $from, 60 + $m.Length + 60))
        $at = $m.Index - $from
        $run = [regex]::Matches($win, '[\x20-\x7E]+') | Where-Object { $_.Index -le $at -and $_.Index + $_.Length -ge $at + $m.Length } | Select-Object -First 1
        if ($run) {
            $name = $run.Value.Trim()
            if ($name.Length -ge 4 -and $name.Length -le 120) { $into[$name] = $true }
        }
    }
}

# A serialized file, read in 32 MB pieces that overlap by 256 bytes so a name
# split between two pieces is still seen whole in one of them.
function Find-InData([string]$path, [string]$words) {
    $found = @{}
    $stream = [System.IO.File]::OpenRead($path)
    try {
        $size = 32MB; $overlap = 256
        $buf = New-Object byte[] ($size + $overlap)
        $carry = 0
        while ($true) {
            $n = $stream.Read($buf, $carry, $size)
            if ($n -le 0) { break }
            Get-Runs ($latin1.GetString($buf, 0, $carry + $n)) $words $found
            $keep = [Math]::Min($overlap, $carry + $n)
            [Array]::Copy($buf, $carry + $n - $keep, $buf, 0, $keep)
            $carry = $keep
        }
    } finally { $stream.Dispose() }
    return $found
}

# A code DLL: its type and member names are plain text, its string literals
# UTF-16 - read at both byte alignments.
function Find-InCode([string]$path, [string]$words) {
    $found = @{}
    $b = [System.IO.File]::ReadAllBytes($path)
    Get-Runs ($latin1.GetString($b)) $words $found
    Get-Runs ([System.Text.Encoding]::Unicode.GetString($b)) $words $found
    if ($b.Length -gt 1) { Get-Runs ([System.Text.Encoding]::Unicode.GetString($b, 1, $b.Length - 1)) $words $found }
    return $found
}

if (-not (Test-Path -LiteralPath $DataDir)) { throw "no such folder: $DataDir" }
$serialized = @(Get-ChildItem -LiteralPath $DataDir -File | Where-Object {
    $_.Extension -eq ".assets" -or $_.Name -match '^level\d+$' -or $_.Name -eq "globalgamemanagers" } | Sort-Object Name)
$managed = Join-Path $DataDir "Managed"
$code = @()
if (Test-Path -LiteralPath $managed) {
    $code = @(Get-ChildItem -LiteralPath $managed -Filter *.dll -File | Where-Object {
        $_.Name -notmatch '^(Unity|System|Mono|mscorlib|netstandard|Microsoft|Newtonsoft|DOTween|Rewired|Sirenix|Bee|nunit)' } | Sort-Object Name)
}
$stamp = "# files: " + ((@($serialized) + @($code) | ForEach-Object { "$($_.Name)=$($_.Length)" }) -join ";")
if (-not $Force -and (Test-Path -LiteralPath $OutFile) -and (@(Get-Content -LiteralPath $OutFile -TotalCount 3) -contains $stamp)) {
    Write-Host "  kept   ui-assets.txt (the game's data has not changed since the last scan)"
    return
}

$lines = @("# Names in Sea Power's Unity data and code that read like background, loading, splash",
           "# or menu pictures (tools\scan-ui-assets.ps1) - what a plugin must find to swap one.",
           $stamp, "", "Data folder: $DataDir", "")
foreach ($f in $serialized) {
    Write-Host ("  scanning {0} ({1:N0} MB)" -f $f.Name, ($f.Length / 1MB))
    $names = @((Find-InData $f.FullName $pictureWords).Keys | Sort-Object)
    if (-not $names.Count) { continue }
    $lines += ("== {0}  ({1:N0} MB)  {2} name(s)" -f $f.Name, ($f.Length / 1MB), $names.Count)
    $lines += @($names | Select-Object -First $maxPerFile | ForEach-Object { "  $_" })
    if ($names.Count -gt $maxPerFile) { $lines += "  ... and $($names.Count - $maxPerFile) more" }
    $lines += ""
}
foreach ($f in $code) {
    $names = @((Find-InCode $f.FullName $codeWords).Keys | Sort-Object)
    if (-not $names.Count) { continue }
    $lines += ("== Managed\{0}  (code)  {1} name(s)" -f $f.Name, $names.Count)
    $lines += @($names | Select-Object -First $maxPerFile | ForEach-Object { "  $_" })
    if ($names.Count -gt $maxPerFile) { $lines += "  ... and $($names.Count - $maxPerFile) more" }
    $lines += ""
}
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutFile) | Out-Null
[System.IO.File]::WriteAllText($OutFile, (($lines -join "`r`n") + "`r`n"))
Write-Host ("  wrote  {0,-30} {1} line(s)" -f (Split-Path -Leaf $OutFile), $lines.Count)
