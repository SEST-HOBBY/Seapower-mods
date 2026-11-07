# SEST Integration Pack - unbind Contact Log's two default keys that clash
# with other mods' keys. SETUP runs this when Contact Log's settings file
# exists; run it by hand with the game closed:
#   powershell -ExecutionPolicy Bypass -File .\sest-ui-keys.ps1 -GameDir "<...>\common\Sea Power"
#
# Contact Log (BepInEx\config\com.seapower.contactlog.cfg, section [Input])
# ships ToggleWindow = F6 and RunProbe = F8. Its F6 clashes with Topographic
# Map's F6 and its F8 probe with Coordinated Strike Tool's F8 planner, and
# the diagnostic probe can stall the game. This sets each of those two keys
# to None only while it still holds exactly that default; any other value
# (F9, say, or a combination) is the player's choice and is kept. Contact
# Log's window stays on its bottom-bar button.
#
# It never creates a folder or a settings file: no file, nothing to do. It
# reads and checks the whole file before it writes a byte; a key listed
# twice leaves the file alone. Only the value text changes: every other
# byte, the byte-order mark and the line endings stay as they were. The
# first time it changes the file it keeps the file as it was beside it as
# com.seapower.contactlog.cfg.sest-ui-keys.bak (never overwritten); to undo,
# copy that back over the .cfg with the game closed.
param([Parameter(Mandatory = $true)][string]$GameDir)
$ErrorActionPreference = 'Stop'

if (Get-Process -Name 'Sea Power', 'SeaPower' -ErrorAction SilentlyContinue) { throw 'Sea Power is running; quit the game first.' }
$cfg = [IO.Path]::Combine($GameDir, 'BepInEx', 'config', 'com.seapower.contactlog.cfg')
if (-not (Test-Path -LiteralPath $cfg -PathType Leaf)) { return }

# BepInEx reads the file line by line: each line trimmed; a line starting
# with # is a comment; [Name] starts a section; Key = Value, the key and
# value trimmed. Read here one character per byte (ISO-8859-1), so the text
# maps back to exactly the bytes it came from, whatever the encoding.
$bytes = [IO.File]::ReadAllBytes($cfg)
$latin = [Text.Encoding]::GetEncoding(28591)
$text = $latin.GetString($bytes)
$from = 0
if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) { $from = 3 }
$defaults = @(@('ToggleWindow', 'F6'), @('RunProbe', 'F8'))
$found = @{}
foreach ($d in $defaults) { $found[$d[0]] = @() }
$ws = [char[]]@([char]' ', [char]"`t")
$section = $null
foreach ($m in [regex]::Matches($text.Substring($from), '[^\r\n]*')) {
    $raw = $m.Value
    $t = $raw.Trim($ws)
    if (-not $t -or $t.StartsWith('#')) { continue }
    if ($t.StartsWith('[') -and $t.EndsWith(']')) { $section = $t.Substring(1, $t.Length - 2); continue }
    if ($section -cne 'Input') { continue }
    $eq = $t.IndexOf([char]'=')
    if ($eq -lt 0) { continue }
    $key = $t.Substring(0, $eq).Trim($ws)
    foreach ($d in $defaults) {
        if ($key -cne $d[0]) { continue }
        $s = $raw.IndexOf([char]'=') + 1; $f = $raw.Length
        while ($s -lt $f -and $ws -contains $raw[$s]) { $s++ }
        while ($f -gt $s -and $ws -contains $raw[$f - 1]) { $f-- }
        $found[$d[0]] += , @{ At = $from + $m.Index + $s; Len = $f - $s; Value = $raw.Substring($s, $f - $s) }
    }
}

$twice = @($defaults | Where-Object { $found[$_[0]].Count -gt 1 } | ForEach-Object { $_[0] })
if ($twice.Count) {
    Write-Host ('  [ok]   Contact Log''s keys left alone: ' + ($twice -join ' and ') + ' is listed more than once in ' + $cfg) -ForegroundColor Green
    return
}
$edits = @(); $done = @(); $kept = @()
foreach ($d in $defaults) {
    if ($found[$d[0]].Count -ne 1) { continue }
    $e = $found[$d[0]][0]
    if ($e.Value -ceq $d[1]) { $edits += , $e; $done += ($d[0] + ' ' + $d[1]) }
    elseif ($e.Value -cne 'None') { $kept += ($d[0] + ' = ' + $e.Value) }
}
if ($edits.Count) {
    $new = $text
    foreach ($e in @($edits | Sort-Object { $_.At } -Descending)) { $new = $new.Substring(0, $e.At) + 'None' + $new.Substring($e.At + $e.Len) }
    $bak = $cfg + '.sest-ui-keys.bak'
    if (-not (Test-Path -LiteralPath $bak)) { [IO.File]::WriteAllBytes($bak, $bytes) }
    [IO.File]::WriteAllBytes($cfg, $latin.GetBytes($new))
    Write-Host ('  [done] Contact Log''s default keys unbound (F6 clashes with Topographic Map''s F6, the F8 probe with Coordinated Strike Tool''s F8 planner): ' + ($done -join ', ') + ' -> None') -ForegroundColor Green
} else {
    Write-Host '  [ok]   Contact Log''s keys: neither holds its clashing default' -ForegroundColor Green
}
if ($kept.Count) { Write-Host ('         kept as set: ' + ($kept -join ', ')) }
