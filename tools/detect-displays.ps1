<#
.SYNOPSIS
    Record the real monitor layout so the Second Screen pack can be built for it.

.DESCRIPTION
    integration/second-screen/build_pack.py parks the tactical map and the
    Formation Manager window on the second monitor, and it works out where that
    is from data\display-layout.json. This script writes that file from the
    actual desktop, so the geometry is measured rather than assumed - a wrong
    number here puts the tactical map somewhere no monitor shows.

    It reports three cases:

      two or more monitors  - the one on the chosen side becomes the 'panels'
                              region, the rest stay 'view'. Note that Unity
                              will not span monitors by itself: you still need
                              NVIDIA Surround / AMD Eyefinity, or a borderless
                              window sized to the pair. See docs\second-screen.md.
      one very wide monitor - if Surround/Eyefinity is already on, Windows sees
                              ONE display. Pass -SplitSingleDisplay 2 to treat
                              its halves as the two regions.
      one ordinary monitor  - writes mode=single-screen, which makes the pack a
                              deliberate no-op instead of hiding the map.

    Read-only unless -Write is passed. It never touches usersettings.ini; it
    only reads it to show what resolution the game is currently set to.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\tools\detect-displays.ps1

.EXAMPLE
    # Commit to it, then rebuild and deploy
    powershell -ExecutionPolicy Bypass -File .\tools\detect-displays.ps1 -Write
    python tools\build_all.py
    powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1

.EXAMPLE
    # Surround/Eyefinity already merged both screens into one 5120x1440 display
    powershell -ExecutionPolicy Bypass -File .\tools\detect-displays.ps1 -SplitSingleDisplay 2 -Write
#>
[CmdletBinding()]
param(
    [ValidateSet("right", "left")][string]$PanelSide = "right",
    [int]$SplitSingleDisplay = 0,
    [int]$Margin = 12,
    [string]$LayoutPath = (Join-Path (Split-Path $PSScriptRoot -Parent) "data\display-layout.json"),
    [string]$SettingsPath = (Join-Path $env:USERPROFILE "AppData\LocalLow\Triassic Games\Sea Power\usersettings.ini"),
    [switch]$Write
)

$ErrorActionPreference = "Stop"

# Without this, a DPI-unaware PowerShell host is handed SCALED coordinates -
# a 2560x1440 screen at 125% reports 2048x1152 and every computed position is
# quietly wrong. Harmless if the host is already aware.
try {
    Add-Type -Namespace SestNative -Name Dpi -MemberDefinition `
        '[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();' `
        -ErrorAction Stop
    [void][SestNative.Dpi]::SetProcessDPIAware()
} catch { Write-Verbose "SetProcessDPIAware unavailable: $($_.Exception.Message)" }

Add-Type -AssemblyName System.Windows.Forms

function ConvertTo-JsonText([string]$s) {
    return $s.Replace('\', '\\').Replace('"', '\"')
}

$screens = [System.Windows.Forms.Screen]::AllScreens | Sort-Object { $_.Bounds.X }
Write-Host "Displays Windows reports:" -ForegroundColor Cyan
foreach ($s in $screens) {
    $b = $s.Bounds
    $tag = if ($s.Primary) { " (primary)" } else { "" }
    Write-Host ("  {0,-14} {1}x{2} at {3},{4}{5}" -f $s.DeviceName, $b.Width, $b.Height, $b.X, $b.Y, $tag)
}

# Cross-check against the adapter's own idea of the mode. A mismatch usually
# means DPI scaling slipped through, and every number below would be short.
try {
    foreach ($c in Get-CimInstance Win32_VideoController -ErrorAction Stop) {
        if (-not $c.CurrentHorizontalResolution) { continue }
        $match = $screens | Where-Object {
            $_.Bounds.Width -eq $c.CurrentHorizontalResolution -and
            $_.Bounds.Height -eq $c.CurrentVerticalResolution }
        if (-not $match) {
            Write-Warning ("adapter '{0}' reports {1}x{2}, which matches no display above - " +
                "DPI scaling may be distorting these numbers; check the values before -Write." -f
                $c.Name, $c.CurrentHorizontalResolution, $c.CurrentVerticalResolution)
        }
    }
} catch { Write-Verbose "Win32_VideoController unavailable: $($_.Exception.Message)" }

# --- turn the displays into regions -----------------------------------------
$regions = @()
$mode = "second-screen"
$note = ""

if ($screens.Count -eq 1 -and $SplitSingleDisplay -gt 1) {
    $b = $screens[0].Bounds
    $n = $SplitSingleDisplay
    $slice = [int][math]::Floor($b.Width / $n)
    $x = $b.X
    for ($i = 0; $i -lt $n; $i++) {
        # The remainder goes to the last slice so the regions tile exactly.
        $w = $slice
        if ($i -eq $n - 1) { $w = $b.X + $b.Width - $x }   # remainder to the last slice
        $regions += [pscustomobject]@{ id = "part$($i + 1)"; role = "view"
                                       x = $x; y = $b.Y; width = $w; height = $b.Height }
        $x += $w
    }
    $note = "one $($b.Width)x$($b.Height) display split into $n regions (Surround/Eyefinity assumed)"
}
elseif ($screens.Count -eq 1) {
    $b = $screens[0].Bounds
    $mode = "single-screen"
    $regions += [pscustomobject]@{ id = "main"; role = "view"
                                   x = $b.X; y = $b.Y; width = $b.Width; height = $b.Height }
    $note = "one display: nothing to move the panels onto"
}
else {
    $i = 1
    foreach ($s in $screens) {
        $b = $s.Bounds
        $id = "aux$i"
        if ($s.Primary) { $id = "main" }
        $regions += [pscustomobject]@{ id = $id; role = "view"
                                       x = $b.X; y = $b.Y; width = $b.Width; height = $b.Height }
        $i++
    }
    $note = "$($screens.Count) displays"
}

if ($mode -eq "second-screen") {
    $target = if ($PanelSide -eq "right") {
        $regions | Sort-Object x | Select-Object -Last 1
    } else {
        $regions | Sort-Object x | Select-Object -First 1
    }
    $target.role = "panels"
}

# The builder refuses a layout whose regions do not tile one rectangle, because
# the spare area would be window over no monitor. Catch it here, where the fix
# (line the monitors up in Windows display settings) is obvious.
$left   = ($regions | Measure-Object x -Minimum).Minimum
$top    = ($regions | Measure-Object y -Minimum).Minimum
$right  = ($regions | ForEach-Object { $_.x + $_.width }  | Measure-Object -Maximum).Maximum
$bottom = ($regions | ForEach-Object { $_.y + $_.height } | Measure-Object -Maximum).Maximum
$covered = ($regions | ForEach-Object { $_.width * $_.height } | Measure-Object -Sum).Sum
if ($covered -ne ($right - $left) * ($bottom - $top)) {
    Write-Warning ("these displays do not form one rectangle (staggered or different heights), " +
        "so a spanning window would cover desktop that no monitor shows. Writing mode=single-screen; " +
        "align the monitors in Windows display settings and re-run, or edit the file by hand.")
    $mode = "single-screen"
    foreach ($r in $regions) { $r.role = "view" }
}

# --- render the layout file --------------------------------------------------
$stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm")
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('{')
$lines.Add('  "_comment": [')
$lines.Add('    "Where the game window lives, in Windows virtual-desktop pixels. Read by",')
$lines.Add('    "integration/second-screen/build_pack.py to work out where to park the tactical",')
$lines.Add('    "map and the Formation Manager window; rewritten from the real desktop by",')
$lines.Add('    "tools/detect-displays.ps1 -Write on the gaming PC.",')
$lines.Add('    "",')
$lines.Add('    "A region is normally one physical monitor. Under NVIDIA Surround / AMD",')
$lines.Add('    "Eyefinity the two monitors are ONE logical display to Windows, so the regions",')
$lines.Add('    "are instead the left and right halves of it - the arithmetic is the same.",')
$lines.Add('    "",')
$lines.Add('    "mode: ''second-screen'' places the panels in the ''panels'' region. ''single-screen''",')
$lines.Add('    "makes the pack a no-op that ships vanilla geometry - set it (or re-run the",')
$lines.Add('    "detector) before playing on one monitor, or the map is parked off-screen."')
$lines.Add('  ],')
$lines.Add('  "source": "' + (ConvertTo-JsonText "Detected by tools/detect-displays.ps1 on $env:COMPUTERNAME, $stamp - $note.") + '",')
$lines.Add('  "detected": true,')
$lines.Add('  "mode": "' + $mode + '",')
$lines.Add('  "margin": ' + $Margin + ',')
$lines.Add('  "regions": [')
for ($i = 0; $i -lt $regions.Count; $i++) {
    $r = $regions[$i]
    $comma = if ($i -lt $regions.Count - 1) { ',' } else { '' }
    $lines.Add(('    {{ "id": "{0}", "role": "{1}", "x": {2}, "y": {3}, "width": {4}, "height": {5} }}{6}' -f
        (ConvertTo-JsonText $r.id), $r.role, $r.x, $r.y, $r.width, $r.height, $comma))
}
$lines.Add('  ]')
$lines.Add('}')
$json = ($lines -join "`n") + "`n"

Write-Host ""
Write-Host $json

if ($Write) {
    # LF, no BOM: the repo's .gitattributes normalises these files and Python
    # reads them back as plain UTF-8.
    [System.IO.File]::WriteAllText($LayoutPath, $json)
    Write-Host "written: $LayoutPath" -ForegroundColor Green
} else {
    Write-Host "(dry run - pass -Write to save this to $LayoutPath)" -ForegroundColor Yellow
}

# --- what to do with it ------------------------------------------------------
$w = $right - $left
$h = $bottom - $top
Write-Host ""
if ($mode -eq "second-screen") {
    Write-Host "Next:" -ForegroundColor Cyan
    Write-Host "  1. Make the game window span $($w)x$($h): Surround/Eyefinity, or Steam launch options"
    Write-Host "     -screen-fullscreen 0 -popupwindow -screen-width $w -screen-height $h"
    Write-Host "  2. python tools\build_all.py"
    Write-Host "  3. powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1"
    Write-Host "  See docs\second-screen.md for which panels move and which cannot."
} else {
    Write-Host "Mode is single-screen: the pack will ship vanilla geometry and change nothing." -ForegroundColor Yellow
    Write-Host "  Rebuild and reinstall so the game stops using any previous second-screen layout:"
    Write-Host "  python tools\build_all.py; .\tools\install-sest-packs.ps1"
}

# The game's own display settings, for comparison. Read-only.
if (Test-Path -LiteralPath $SettingsPath) {
    $hits = Select-String -LiteralPath $SettingsPath -Pattern '^(.*(resolution|fullscreen|screen|display|monitor|vsync).*)$' -AllMatches
    if ($hits) {
        Write-Host ""
        Write-Host "usersettings.ini currently says:" -ForegroundColor Cyan
        $hits | Select-Object -First 12 | ForEach-Object { Write-Host "  $($_.Line.Trim())" }
    }
} else {
    Write-Host ""
    Write-Warning "usersettings.ini not found at $SettingsPath - skipped the comparison."
}
