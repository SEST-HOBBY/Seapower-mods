# Lists every ship, aircraft and land unit the game can see (base game + Workshop +
# StreamingAssets packs) that has no name section in any language_en names file -
# the units the encyclopedia files under "Missing Type / Missing Class".
# Writes unnamed-units.txt to the Desktop. Read-only.
$roots = @()
foreach ($lib in @("C:\Program Files (x86)\Steam\steamapps") + (Get-PSDrive -PSProvider FileSystem | ForEach-Object { Join-Path $_.Root "SteamLibrary\steamapps" })) {
    if (Test-Path "$lib\common\Sea Power") { $roots += "$lib\common\Sea Power" }
    if (Test-Path "$lib\workshop\content\1286220") { $roots += "$lib\workshop\content\1286220" }
}
$named = @{}
$units = @()
foreach ($r in $roots) {
    Get-ChildItem -Path $r -Recurse -File -Filter *.ini -ErrorAction SilentlyContinue | ForEach-Object {
        $dir = $_.DirectoryName
        if ($dir -match '\\language_en(\\|$)') {
            foreach ($line in [System.IO.File]::ReadAllLines($_.FullName)) {
                if ($line -match '^\s*\uFEFF?\[([^\]]+)\]') { $named[$Matches[1].Trim()] = $true }
            }
        } elseif ((Split-Path $dir -Leaf) -in @('vessels', 'aircraft', 'land_units') -and
                  $_.BaseName -notmatch '_variants$|_OVWR$') {
            $units += [pscustomobject]@{ Id = $_.BaseName; Path = $_.FullName }
        }
    }
}
$out = $units | Where-Object { -not $named.ContainsKey($_.Id) } | ForEach-Object {
    "{0}`t{1}`t{2}" -f $_.Id, $_.LastWriteTime, $_.Path
}
$out | Out-File "$env:USERPROFILE\Desktop\unnamed-units.txt" -Encoding utf8
"{0} unnamed units (of {1}) listed from: {2}" -f @($out).Count, $units.Count, ($roots -join '; ')
$out
