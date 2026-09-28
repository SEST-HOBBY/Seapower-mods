<#
.SYNOPSIS
    Turn off debug switches that Workshop mods ship switched on.

.DESCRIPTION
    Some code mods ship with their own troubleshooting switch left on. With
    BepInEx and Anchor Chain installed their code runs, and a debug switch
    that logs on every physics tick can stall the game outright. Steam puts
    the author's file back whenever the mod updates, so sync-sest.ps1 runs
    this every time; it can also be run on its own.

    Each entry below names a Workshop id, a file inside that mod's folder, a
    key and the value that turns the logging off. Only that key's line is
    rewritten; the rest of the file, its encoding and its line endings are
    left as they were. A mod that is not downloaded, or a file that is not
    there, is reported and skipped.

      3789188689  PLA & PLAN & PLAAF AEP (Anchor Chain expansion pack)
                  debug.ini Enabled=1 makes its SubAmmunition code log a full
                  stack trace every time a sonobuoy or bomb moves - every
                  physics tick, for every one in the water. The file's own
                  comment says to set 1 only while chasing a missile that
                  self-destructs. With it on, Steel Highway froze on 28 Sep
                  (Windows: not responding) with the BepInEx log made of
                  nothing else (install snapshot 82a84d7c).

    Run with the game closed; the mod reads the switch when it loads.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\tools\quiet-mod-debug.ps1
#>
[CmdletBinding()]
param([switch]$WhatIfOnly)

$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
. (Join-Path $scriptDir "lib\common.ps1")

$switches = @(
    @{ Id = "3789188689"; File = "debug.ini"; Key = "Enabled"; Quiet = "0" }
)

$contentDirs = @(foreach ($lib in Get-SteamLibraries) {
    $c = Join-Path $lib "workshop\content"
    if (Test-Path -LiteralPath $c) { Get-ChildItem -LiteralPath $c -Directory -ErrorAction SilentlyContinue }
})

foreach ($s in $switches) {
    $label = "{0}\{1} {2}" -f $s.Id, $s.File, $s.Key
    $path = $null
    foreach ($app in $contentDirs) {
        $candidate = Join-Path $app.FullName (Join-Path $s.Id $s.File)
        if (Test-Path -LiteralPath $candidate) { $path = $candidate; break }
    }
    if (-not $path) { Write-Host ("  not present  {0} (mod not downloaded, or no such file)" -f $label); continue }
    $bytes = [IO.File]::ReadAllBytes($path)
    $bom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
    $text = (New-Object Text.UTF8Encoding($false)).GetString($bytes, $(if ($bom) { 3 } else { 0 }), $bytes.Length - $(if ($bom) { 3 } else { 0 }))
    $pattern = "(?m)^([ \t]*" + [regex]::Escape($s.Key) + "[ \t]*=[ \t]*)([^\r\n]*?)([ \t]*)(\r?)$"
    $m = [regex]::Match($text, $pattern)
    if (-not $m.Success) { Write-Warning ("{0}: no {1}= line in {2} - left alone" -f $s.Id, $s.Key, $path); continue }
    if ($m.Groups[2].Value -eq $s.Quiet) { Write-Host ("  already off  {0}={1}" -f $label, $s.Quiet); continue }
    if ($WhatIfOnly) { Write-Host ("  would set    {0}={1} (now {2})" -f $label, $s.Quiet, $m.Groups[2].Value); continue }
    $new = $text.Substring(0, $m.Index) + $m.Groups[1].Value + $s.Quiet + $m.Groups[3].Value + $m.Groups[4].Value +
           $text.Substring($m.Index + $m.Length)
    [IO.File]::WriteAllText($path, $new, (New-Object Text.UTF8Encoding($bom)))
    Write-Host ("  switched off {0}={1} (was {2})" -f $label, $s.Quiet, $m.Groups[2].Value) -ForegroundColor Yellow
}
