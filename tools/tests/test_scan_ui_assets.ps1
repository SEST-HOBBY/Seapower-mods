<#
.SYNOPSIS
    tools\scan-ui-assets.ps1 on a synthetic data folder: every name listed,
    runs followed to their ends, over-long runs cut and marked, UTF-16 names
    in code, and a name across the 32 MB piece boundary.

.DESCRIPTION
    The scan reads the game's Unity data on the PC, which this machine does
    not have, so the test writes a stand-in folder and runs the scan on it:
      - sharedassets0.assets: random bytes with known names planted in them,
        each bracketed by zero bytes the way Unity's length-prefixed strings
        are: a short name, a 168-character XAML line (over the old 120 limit),
        and a 2,510-character run with "background" in its middle;
      - resources.assets: 32 MB of zeros with one name across the piece
        boundary at 32 MB;
      - Managed\Fake-Scripts.dll: bytes, not code (the scan reads files and
        runs nothing) - 450 distinct ui/ names, over the old 400 cap, and one
        UTF-16 name at an odd byte offset.
    Then it checks the output file. Exit code 1 on any failed check.

        pwsh -File tools/tests/test_scan_ui_assets.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$scan = Join-Path (Split-Path -Parent $PSScriptRoot) "scan-ui-assets.ps1"
$root = Join-Path ([System.IO.Path]::GetTempPath()) ("sest-scan-test-" + [Guid]::NewGuid().ToString("N").Substring(0, 8))
$failed = 0

function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok     $what" } else { Write-Host "  FAILED $what"; $script:failed++ }
}

# $text as Latin-1 bytes, with four zero bytes either side so the run ends there.
function Plant([byte[]]$buf, [int]$at, [string]$text) {
    $b = [System.Text.Encoding]::GetEncoding(28591).GetBytes($text)
    for ($i = 0; $i -lt 4; $i++) { $buf[$at + $i] = 0; $buf[$at + 4 + $b.Length + $i] = 0 }
    [Array]::Copy($b, 0, $buf, $at + 4, $b.Length)
}

try {
    New-Item -ItemType Directory -Force -Path (Join-Path $root "Managed") | Out-Null

    # --- sharedassets0.assets: 64 KB of seeded noise, three names planted ----
    $rnd = New-Object System.Random 20261014
    $noise = New-Object byte[] 65536
    $rnd.NextBytes($noise)
    $short = "ui/loading/background1"
    $xaml = '<Image Source="{Binding BackgroundImage}" Stretch="UniformToFill" Visibility="{Binding BackgroundVisible, Converter={StaticResource BoolToVisibility}}" Opacity="0.85"/>'
    $long = ("L" * 1250) + "background" + ("R" * 1250)
    Plant $noise 1000 $short
    Plant $noise 5000 $xaml
    Plant $noise 20000 $long
    [System.IO.File]::WriteAllBytes((Join-Path $root "sharedassets0.assets"), $noise)

    # --- resources.assets: a name across the 32 MB piece boundary ----------
    $boundary = "loading_screen_on_the_boundary"
    $fs = [System.IO.File]::Create((Join-Path $root "resources.assets"))
    try {
        $fs.SetLength(32MB + 4096)
        $fs.Position = 32MB - 12
        $b = [System.Text.Encoding]::ASCII.GetBytes($boundary)
        $fs.Write($b, 0, $b.Length)
    } finally { $fs.Dispose() }

    # --- Managed\Fake-Scripts.dll: 450 names, and one in UTF-16 at an odd offset
    $names = 1..450 | ForEach-Object { "ui/pictures/picture_{0:D3}" -f $_ }
    $ms = New-Object System.IO.MemoryStream
    $ms.WriteByte(0)   # one byte, so the UTF-16 string below sits at an odd offset
    $u = [System.Text.Encoding]::Unicode.GetBytes("menu_bg_still_utf16")
    $ms.Write($u, 0, $u.Length); $ms.WriteByte(0); $ms.WriteByte(0)
    foreach ($n in $names) {
        $a = [System.Text.Encoding]::ASCII.GetBytes($n)
        $ms.Write($a, 0, $a.Length); $ms.WriteByte(0)
    }
    [System.IO.File]::WriteAllBytes((Join-Path (Join-Path $root "Managed") "Fake-Scripts.dll"), $ms.ToArray())

    # --- run the scan -------------------------------------------------------
    $out = Join-Path $root "ui-assets.txt"
    & $scan -DataDir $root -OutFile $out -Force
    $lines = @(Get-Content -LiteralPath $out)
    $listed = @($lines | Where-Object { $_ -match '^  ' } | ForEach-Object { $_.Substring(2) })

    Check ($listed -contains $short) "short name listed whole: $short"
    Check ($listed -contains $xaml) ("a {0}-character XAML line listed whole" -f $xaml.Length)
    $cut = @($listed | Where-Object { $_ -like "...L*background*R..." })
    Check ($cut.Count -eq 1 -and $cut[0].Length -eq (3 + 1000 + 10 + 1000 + 3)) "a 2,510-character run is cut 1,000 either side of the word and marked ... at both ends"
    Check ($listed -contains $boundary) "a name across the 32 MB piece boundary listed whole: $boundary"
    Check (-not ($listed | Where-Object { $_ -ne $boundary -and $_ -like "*$($boundary.Substring(0, 12))*" })) "and no cut version of it"
    $missing = @($names | Where-Object { $listed -notcontains $_ })
    Check ($missing.Count -eq 0) "all 450 code names listed (missing: $($missing.Count))"
    Check (($lines | Where-Object { $_ -match '^== Managed\\Fake-Scripts\.dll  \(code\)  451 name\(s\)$' }).Count -eq 1) "the code file's count line says 451 name(s)"
    Check (-not ($lines | Where-Object { $_ -match '^  \.\.\. and \d+ more$' })) "no '... and N more' line"
    Check ($listed -contains "menu_bg_still_utf16") "a UTF-16 name at an odd offset listed"
} finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}

if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
