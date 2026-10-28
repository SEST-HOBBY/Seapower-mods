<#
.SYNOPSIS
    Stop the Mod Manager's start-up warning about mods "not compatible" with
    this game version, by marking each such mod compatible on this PC.

.DESCRIPTION
    The Mod Manager reads [Compatibility] from every mod's _info.ini and
    lists each mod the game does not accept as not compatible at every
    start-up, although it loads and plays. The rule, read from the game's
    code (ModCompatibility.Matches, Sea Power 0.8.7): an ExactVersion must
    equal the game's MAJOR.MINOR.PATCH; failing that, an ApproximateVersion
    must be written MAJOR.MINOR.PATCH with the game's MAJOR and MINOR and a
    PATCH no higher than the game's; failing both, the range keys must admit
    the game. On 18 Oct 2026 68 of the collection's mods failed it, last set
    for 0.4 to 0.7.

    This uses the players' SETUP's own code for it: the Compat* functions in
    integration\campaign\setup\sest-setup.ps1, loaded from that file, so
    the two cannot drift apart. For each Workshop mod whose ApproximateVersion
    was made for an OLDER game version (also one like 0.7 or 0.8 that is not
    written MAJOR.MINOR.PATCH), it rewrites that one value to the game's
    MAJOR.MINOR.0, which every patch of that game version accepts, and puts
    one comment line above it saying so. Nothing else in the file changes:
    its encoding, byte-order mark and line endings stay as they were. The
    author's own file is kept under %LOCALAPPDATA%\SEST\compat-originals,
    and tools\export-mod-configs.ps1 exports that kept copy, so mods-source
    stays the authors' files. A file marked earlier is judged again: after a
    game update that lists it again, only its value is rewritten and the kept
    copy stays the author's. If the game went back a version (a player
    leaving a public beta, say), so that an earlier mark is now ahead of it,
    the author's kept copy decides: the value is rewritten again if this
    would mark the author's file, and the author's file goes back if this
    would leave it alone (the game accepts it, or it was made for a newer
    game version too).

    Left alone and named: a mod made for a NEWER game version (it may need
    that game), unless SETUP's reviewed list (CompatReviewed) names it and
    its folder holds no .dll; an ExactVersion or a range the game rejects;
    a file that is not UTF-8 text. Left alone silently: mods the game
    accepts; mods with no [Compatibility] section; SEST's own Workshop item.

    Steam puts a mod's own _info.ini back whenever the mod updates, so
    tools\sync-sest.ps1 runs this every time. It only touches this PC. Since
    25 Oct 2026 the pack's own SETUP does the same for a player, for the
    mods its LOAD-ORDER.txt lists, with the same marker and the same kept
    copies (sest-setup.ps1 -RestoreModFiles puts them back), so either
    tool's -Restore undoes the other's marks.

    Run with the game closed; the Mod Manager reads the files at start-up.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\tools\mark-mods-compatible.ps1
    powershell -ExecutionPolicy Bypass -File .\tools\mark-mods-compatible.ps1 -WhatIfOnly
    # Put every author's file back:
    powershell -ExecutionPolicy Bypass -File .\tools\mark-mods-compatible.ps1 -Restore
#>
[CmdletBinding()]
param(
    [switch]$Restore,
    [switch]$WhatIfOnly,
    [string]$WorkshopContentDir,
    [string]$GameVersion,
    [string]$GameDir,
    [string]$StreamingAssetsDir,
    [string]$BackupDir
)

$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
. (Join-Path $scriptDir "lib\common.ps1")

if (-not $WorkshopContentDir) { $WorkshopContentDir = Find-WorkshopContent }
if (-not $WorkshopContentDir -or -not (Test-Path -LiteralPath $WorkshopContentDir)) {
    throw "Sea Power's Workshop folder not found. Re-run with -WorkshopContentDir '<...>\steamapps\workshop\content\1286220'"
}
if (-not $BackupDir) { $BackupDir = Get-CompatBackupDir }
$utf8 = New-Object Text.UTF8Encoding($false)

function Read-Text([byte[]]$bytes) {
    $bom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
    $skip = 0
    if ($bom) { $skip = 3 }
    return @{ Bom = $bom; Text = $utf8.GetString($bytes, $skip, $bytes.Length - $skip) }
}

function Write-Text([string]$path, [string]$text, [bool]$bom) {
    [IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding($bom)))
}

$mods = @(Get-ChildItem -LiteralPath $WorkshopContentDir -Directory |
    Where-Object { $SestOwnWorkshopIds -notcontains $_.Name } | Sort-Object Name)

# --- Restore ------------------------------------------------------------------
if ($Restore) {
    $put = 0; $stale = 0
    foreach ($kept in @(Get-ChildItem -LiteralPath $BackupDir -Filter "*._info.ini" -File -ErrorAction SilentlyContinue)) {
        $id = $kept.Name.Substring(0, $kept.Name.Length - "._info.ini".Length)
        $live = Join-Path (Join-Path $WorkshopContentDir $id) "_info.ini"
        $marked = (Test-Path -LiteralPath $live) -and
                  ((Read-Text ([IO.File]::ReadAllBytes($live))).Text.IndexOf($SestCompatMarker, [StringComparison]::Ordinal) -ge 0)
        if ($WhatIfOnly) {
            if ($marked) { Write-Host ("  would restore {0}" -f $id) } else { Write-Host ("  would drop    {0} (Steam has since replaced the file)" -f $id) }
            continue
        }
        if ($marked) { [IO.File]::WriteAllBytes($live, [IO.File]::ReadAllBytes($kept.FullName)); $put++ } else { $stale++ }
        Remove-Item -LiteralPath $kept.FullName -Force
    }
    Write-Host ("{0} author's _info.ini put back; {1} kept copies dropped because Steam had already replaced the file." -f $put, $stale)
    return
}

# --- The game's rule ---------------------------------------------------------
# The rule, SETUP's reviewed list and the edit itself: SETUP's own Compat*
# functions, loaded from its file so the two tools cannot drift apart.
$setupScript = Join-Path (Join-Path (Join-Path (Join-Path (Split-Path -Parent $scriptDir) "integration") "campaign") "setup") "sest-setup.ps1"
$parseTokens = $null; $parseErrors = $null
$setupAst = [System.Management.Automation.Language.Parser]::ParseFile($setupScript, [ref]$parseTokens, [ref]$parseErrors)
if ($parseErrors -and $parseErrors.Count) { throw "$setupScript does not parse: $($parseErrors[0].Message)" }
foreach ($fn in @($setupAst.FindAll({ param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -like 'Compat*' }, $false))) {
    . ([scriptblock]::Create($fn.Extent.Text))
}
foreach ($need in 'CompatVer', 'CompatPlan', 'CompatBack', 'CompatMark', 'CompatIsUtf8') {
    if (-not (Get-Command -Name $need -CommandType Function -ErrorAction SilentlyContinue)) { throw "$setupScript has no $need function" }
}

# --- The game's version -----------------------------------------------------
# The first "dd-Mon-yyyy: X.Y.Z Build #N" line of the game's changelog.txt,
# as tools/check_game_version.py reads it.
if (-not $GameVersion) {
    if (-not $GameDir) {
        $sa = $StreamingAssetsDir
        if (-not $sa) { $sa = Find-StreamingAssets }
        # The folder above StreamingAssets, as tools\capture-context.ps1 reads
        # it: changelog.txt is there or one level up.
        if ($sa) { $GameDir = Split-Path -Parent $sa }
    }
    $candidates = @()
    if ($GameDir) {
        $candidates += Join-Path $GameDir "changelog.txt"
        $up = Split-Path -Parent $GameDir
        if ($up) { $candidates += Join-Path $up "changelog.txt" }
    }
    foreach ($chg in $candidates) {
        if (-not (Test-Path -LiteralPath $chg)) { continue }
        $m = [regex]::Match((Get-Content -LiteralPath $chg -Raw), '(?m)^\d{1,2}-[A-Za-z]{3}-\d{4}:\s+(\d+\.\d+\.\d+)\s+Build')
        if ($m.Success) { $GameVersion = $m.Groups[1].Value; break }
    }
}
$gameV = $null
if ($GameVersion) { $gameV = CompatVer $GameVersion }
if ($null -eq $gameV) {
    throw "The game's version was not found in its changelog.txt, or is not X.Y.Z. Re-run with -GameVersion X.Y.Z"
}
$newVer = "{0}.{1}.0" -f $gameV[0], $gameV[1]
Write-Host ("Game version {0}: marking the mods made for an older game version (their ApproximateVersion becomes {1})" -f $GameVersion, $newVer)

# --- Mark ---------------------------------------------------------------------
$marked = 0; $again = 0; $already = 0; $fine = 0; $range = 0; $none = 0; $left = 0; $back = 0
foreach ($mod in $mods) {
    $path = Join-Path $mod.FullName "_info.ini"
    if (-not (Test-Path -LiteralPath $path)) { $none++; continue }
    $bytes = [IO.File]::ReadAllBytes($path)
    $r = Read-Text $bytes
    $text = $r.Text
    $was = $text.IndexOf($SestCompatMarker, [StringComparison]::Ordinal) -ge 0
    $plan = CompatPlan $text $gameV $mod.Name $mod.FullName
    $c = $plan.C
    if ($plan.Why -eq 'ok') {
        if ($was) { $already++ }
        elseif ($c.ExactVersion -or $c.ApproximateVersion) { $fine++ }
        elseif ($c.GreaterThanVersion -or $c.GreaterThanEqualToVersion -or $c.LessThanVersion -or $c.LessThanEqualToVersion -or $c.ExcludeVersions.Trim(', ')) { $range++ }
        else { $none++ }
        continue
    }
    if ($was -and $plan.Why -eq "newer") {
        # This tool's (or SETUP's) own mark is ahead of the game: judged by the
        # author's kept copy (CompatBack).
        $kp = Join-Path $BackupDir ("{0}._info.ini" -f $mod.Name); $kb = $null
        if (Test-Path -LiteralPath $kp) { $kb = [IO.File]::ReadAllBytes($kp) }
        if (CompatBack $plan $kb $SestCompatMarker $gameV $mod.Name $mod.FullName) {
            $how = "{0}, as its author shipped it ({1}); the earlier mark ({2}) was ahead of the game" -f $(if ($plan.Why -eq "ok") { "accepted" } else { "made for a newer game version" }), $plan.What, $c.ApproximateVersion
            if ($WhatIfOnly) { Write-Host ("  would put back {0}  {1}" -f $mod.Name, $how); $back++; continue }
            [IO.File]::WriteAllBytes($path, $kb)
            Remove-Item -LiteralPath $kp -Force
            Write-Host ("  put back     {0}  {1}" -f $mod.Name, $how) -ForegroundColor Yellow
            $back++
            continue
        }
    }
    if ($plan.Mark -and -not (CompatIsUtf8 $bytes)) { $plan.Mark = $false; $plan.What += ", not UTF-8 text" }
    if (-not $plan.Mark) {
        $why = "declared in a way this does not change"
        if ($plan.Why -eq "newer") { $why = "made for a newer game version" }
        Write-Host ("  left alone   {0}  {1} ({2})" -f $mod.Name, $why, $plan.What)
        $left++
        continue
    }
    $how = "ApproximateVersion {0} -> {1}" -f $c.ApproximateVersion, $newVer
    if ($plan.Why -eq "newer") { $how += " (made for a newer game version; reviewed)" }
    if ($WhatIfOnly) { Write-Host ("  would mark   {0}  {1}" -f $mod.Name, $how); $marked++; continue }

    if ($was) {
        # Marked before: only the value changes; the kept copy stays the author's.
        Write-Text $path (CompatMark $text $c $newVer "") $r.Bom
        Write-Host ("  re-marked    {0}  {1}" -f $mod.Name, $how) -ForegroundColor Yellow
        $again++
    } else {
        New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
        [IO.File]::WriteAllBytes((Join-Path $BackupDir ("{0}._info.ini" -f $mod.Name)), $bytes)
        $note = "{0} (its author's ApproximateVersion was {1}); tools\mark-mods-compatible.ps1 -Restore puts it back" -f $SestCompatMarker, $c.ApproximateVersion
        Write-Text $path (CompatMark $text $c $newVer $note) $r.Bom
        Write-Host ("  marked       {0}  {1}" -f $mod.Name, $how) -ForegroundColor Yellow
    }
    $marked++
}
$verb = "marked compatible"
if ($WhatIfOnly) { $verb = "would be marked compatible" }
if ($again) { $verb += " ($again of them marked before, for another game version)" }
Write-Host ("{0} mod(s) {1}; {2} already marked; {3} accepted as their authors declared them; {4} declare only a range the game accepts; {5} with no version line; {6} left alone (listed above)." -f
    $marked, $verb, $already, $fine, $range, $none, $left)
if ($back) {
    $verb = "put back"
    if ($WhatIfOnly) { $verb = "would be put back" }
    Write-Host ("{0} author's _info.ini {1}: an earlier mark was ahead of game version {2}, and this does not mark the author's file (listed above)." -f $back, $verb, $GameVersion)
}
