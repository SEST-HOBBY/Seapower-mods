# Lists every unit profile picture the game can see (base game + Workshop + local packs),
# with its pixel size, into profiles-on-pc.txt on the Desktop. Read-only.
Add-Type -AssemblyName System.Drawing
$roots = @()
foreach ($lib in @("C:\Program Files (x86)\Steam\steamapps") + (Get-PSDrive -PSProvider FileSystem | ForEach-Object { Join-Path $_.Root "SteamLibrary\steamapps" })) {
    if (Test-Path "$lib\common\Sea Power") { $roots += "$lib\common\Sea Power" }
    if (Test-Path "$lib\workshop\content\1286220") { $roots += "$lib\workshop\content\1286220" }
}
$out = foreach ($r in $roots) {
    Get-ChildItem -Path $r -Recurse -File -Include *.png,*.jpg -ErrorAction SilentlyContinue |
        Where-Object { $_.DirectoryName -match '\\profiles($|\\)' } |
        ForEach-Object {
            $w = $h = 0
            try { $img = [System.Drawing.Image]::FromFile($_.FullName); $w = $img.Width; $h = $img.Height; $img.Dispose() } catch {}
            "{0}x{1}`t{2}" -f $w, $h, $_.FullName.Replace($r, (Split-Path $r -Leaf))
        }
}
$out | Out-File "$env:USERPROFILE\Desktop\profiles-on-pc.txt" -Encoding utf8
"{0} profile images listed from: {1}" -f $out.Count, ($roots -join '; ')
