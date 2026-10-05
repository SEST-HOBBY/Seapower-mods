# Lists the download size of every Workshop mod in the SEST load order, as it sits
# in the Steam Workshop folder, plus the total. Writes mod-sizes.txt to the
# Desktop for the Steam collection page. Read-only. Run from the repo folder.
$order = Get-Content "$PSScriptRoot\..\data\load-order.tokens.txt" | Where-Object { $_ -match '^\d+$' }
$ws = $null
foreach ($lib in @("C:\Program Files (x86)\Steam\steamapps") + (Get-PSDrive -PSProvider FileSystem | ForEach-Object { Join-Path $_.Root "SteamLibrary\steamapps" })) {
    if (Test-Path "$lib\workshop\content\1286220") { $ws = "$lib\workshop\content\1286220" }
}
if (-not $ws) { throw "Sea Power Workshop folder not found" }
$total = 0
$rows = foreach ($id in @("3812461539") + $order) {
    $dir = Join-Path $ws $id
    if (-not (Test-Path $dir)) { "{0}`tNOT DOWNLOADED`t" -f $id; continue }
    $bytes = (Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
    $total += $bytes
    $name = ""
    $info = Join-Path $dir "_info.ini"
    if (Test-Path $info) {
        $m = Select-String -Path $info -Pattern '^Name=(.*)' | Select-Object -First 1
        if ($m) { $name = $m.Matches[0].Groups[1].Value.Trim() }
    }
    "{0}`t{1:N1} MB`t{2}" -f $id, ($bytes / 1MB), $name
}
$rows = @($rows) + ("TOTAL`t{0:N2} GB`t{1} items" -f ($total / 1GB), ($order.Count + 1))
$rows | Out-File "$env:USERPROFILE\Desktop\mod-sizes.txt" -Encoding utf8
$rows[-1]
