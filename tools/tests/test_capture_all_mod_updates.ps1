<#
.SYNOPSIS
    capture-all-mod-updates.ps1 against a disposable Git clone and a fake
    Workshop folder: it refuses the deploy branch and a dirty clone, writes
    the review ZIP, exports the mods into the clone, says when the
    installed game is not the exported one, and never commits, pushes or
    changes the Workshop folder.

.DESCRIPTION
    The Python inventory tools are left out of the fixture on purpose, so
    their stages fail and the test also proves a failed stage is recorded
    and the ZIP is still written. Nothing outside the temporary fixture is
    read or written; USERPROFILE points into it while the script runs.

        pwsh -File tools/tests/test_capture_all_mod_updates.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$src = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$root = Join-Path ([IO.Path]::GetTempPath()) ("SEST-capture-all-" + [guid]::NewGuid().ToString("N"))
$clone = Join-Path $root "clone"
$workshop = Join-Path $root "steamapps\workshop\content\1286220"
$profileDir = Join-Path $root "profile"
$savedProfile = $env:USERPROFILE
$failed = 0
function Check([bool]$ok, [string]$what) {
    if ($ok) { Write-Host "  ok     $what" } else { Write-Host "  FAILED $what"; $script:failed++ }
}
function Invoke-FixtureGit([string[]]$GitArgs) {
    $saved = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { $out = @(& git -C $clone -c user.name=test -c user.email=test@example.invalid @GitArgs 2>&1 | ForEach-Object { [string]$_ }) }
    finally { $ErrorActionPreference = $saved }
    return $out
}
function Get-TreeHash([string]$Dir) {
    $sha = [Security.Cryptography.SHA256]::Create()
    $parts = @(Get-ChildItem -LiteralPath $Dir -Recurse -File | Sort-Object FullName | ForEach-Object {
        $_.FullName.Substring($Dir.Length) + "=" + [BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($_.FullName)))
    })
    return ($parts -join "|")
}

try {
    foreach ($dir in @((Join-Path $clone "tools\lib"), (Join-Path $clone "data"), (Join-Path $clone "mods-source"), $workshop,
                       (Join-Path $profileDir "AppData\LocalLow\Triassic Games\Sea Power"))) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    foreach ($name in @("capture-all-mod-updates.ps1", "capture-context.ps1", "export-mod-configs.ps1")) {
        Copy-Item -LiteralPath (Join-Path $src "tools\$name") -Destination (Join-Path $clone "tools")
    }
    Copy-Item -LiteralPath (Join-Path $src "tools\lib\common.ps1") -Destination (Join-Path $clone "tools\lib")
    [IO.File]::WriteAllText((Join-Path $clone "tools\scan-ui-assets.ps1"), "param([string]`$DataDir, [string]`$OutFile)`r`n")
    [IO.File]::WriteAllText((Join-Path $clone "data\deploy-branch.txt"), "deploy-test`n")
    [IO.File]::WriteAllText((Join-Path $clone "data\load-order.tokens.txt"), "SEST_Integration`n3812454152`n")
    [IO.File]::WriteAllText((Join-Path $clone "data\mod-fingerprints.json"), '{"mods":{"3812454152":{"fingerprint":"old-hash"}}}')
    [IO.File]::WriteAllText((Join-Path $clone "mods-source\README.txt"), "fixture`n")
    # The export holds 0.9.0 and the last capture found a newer release: the
    # fixture has no game folder, so the live capture leaves this copy alone.
    New-Item -ItemType Directory -Path (Join-Path $clone "mods-source\_vanilla"), (Join-Path $clone "data\install-snapshot") -Force | Out-Null
    [IO.File]::WriteAllText((Join-Path $clone "mods-source\_vanilla\changelog.txt"), "11-Nov-2026: 0.9.0 Build 261111 Public Release`n")
    [IO.File]::WriteAllText((Join-Path $clone "data\install-snapshot\changelog.live.txt"), "20-Nov-2026: 0.9.1 Build 261120 Public Release`n11-Nov-2026: 0.9.0 Build 261111 Public Release`n")
    [IO.File]::WriteAllText((Join-Path $profileDir "AppData\LocalLow\Triassic Games\Sea Power\usersettings.ini"),
        "[LoadOrder]`r`nNumberOfModFiles=1`r`nMod1Directory=SEST_Integration,True`r`n")
    [IO.File]::WriteAllText((Join-Path $profileDir "AppData\LocalLow\Triassic Games\Sea Power\Player.log"), "clean session`r`n")
    foreach ($entry in @(@("3812454152", "Updated Mod"), @("3819427362", "New Mod"))) {
        $folder = Join-Path $workshop $entry[0]
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        [IO.File]::WriteAllText((Join-Path $folder "_info.ini"), "Name=" + $entry[1])
        [IO.File]::WriteAllText((Join-Path $folder "settings.ini"), "[Mod]`r`nEnabled=True`r`n")
    }
    $null = Invoke-FixtureGit @("init", "-q", "-b", "deploy-test")
    $null = Invoke-FixtureGit @("add", "-A")
    $null = Invoke-FixtureGit @("commit", "-q", "-m", "fixture")
    $head = "$(Invoke-FixtureGit @('rev-parse', 'HEAD'))".Trim()
    $workshopBefore = Get-TreeHash $workshop
    $env:USERPROFILE = $profileDir
    $script = Join-Path $clone "tools\capture-all-mod-updates.ps1"
    $out1 = Join-Path $root "out-deploy"

    $refused = $false
    try { & $script -WorkshopContentDir $workshop -OutputDir $out1 *> (Join-Path $root "run-deploy.txt") }
    catch { $refused = $_.Exception.Message -match "deploy branch" }
    Check $refused "refuses to run on the deploy branch"
    Check (-not (Test-Path -LiteralPath $out1)) "writes nothing when it refuses"

    $null = Invoke-FixtureGit @("checkout", "-q", "-b", "chore/workshop-refresh-test")
    [IO.File]::WriteAllText((Join-Path $clone "mods-source\README.txt"), "edited`n")
    $refused = $false
    try { & $script -WorkshopContentDir $workshop -OutputDir $out1 *> (Join-Path $root "run-dirty.txt") }
    catch { $refused = $_.Exception.Message -match "uncommitted" }
    Check $refused "refuses a clone with uncommitted changes"
    $null = Invoke-FixtureGit @("checkout", "-q", "--", "mods-source/README.txt")

    $out = Join-Path $root "out"
    & $script -WorkshopContentDir $workshop -OutputDir $out *> (Join-Path $root "run.txt")
    $zip = "$out.zip"
    Check (Test-Path -LiteralPath $zip -PathType Leaf) "writes the review ZIP"
    $readme = Get-Content -LiteralPath (Join-Path $out "review\README.txt") -Raw
    Check ($readme.Contains("Nothing was committed, pushed or uploaded.")) "README says nothing was committed or pushed"
    Check ($readme -match "PROBLEM: fingerprint_mods\.py exited") "a failed Python stage is recorded, not fatal"
    Check ($readme.Contains("Installed game: 20-Nov-2026: 0.9.1 Build 261120 Public Release") -and
           $readme.Contains("Exported game (mods-source\_vanilla): 11-Nov-2026: 0.9.0 Build 261111 Public Release")) "README names the installed and the exported game"
    Check ($readme.Contains("THE INSTALLED GAME IS NOT THE EXPORTED ONE") -and $readme.Contains("run the game export next")) "README says the game has moved and what to run"
    Check ((Test-Path -LiteralPath (Join-Path $out "review\snapshot\game-build.txt") -PathType Leaf) -and
           (Test-Path -LiteralPath (Join-Path $out "review\snapshot\game-files-dropped.txt") -PathType Leaf)) "the bundle carries the game build and the dropped-files list"
    $console = Get-Content -LiteralPath (Join-Path $root "run.txt") -Raw
    Check ($console.Contains("THE INSTALLED GAME IS NOT THE EXPORTED ONE")) "the console says it too"
    Check (Test-Path -LiteralPath (Join-Path $clone "mods-source\3819427362\_info.ini")) "exports the new mod into the clone"
    Check (Test-Path -LiteralPath (Join-Path $out "review\changed-mod-configs\mods-source\3819427362\_info.ini")) "copies the new mod's files into the bundle"
    $updates = Get-Content -LiteralPath (Join-Path $clone "data\install-snapshot\workshop-updates.txt") -Raw
    Check ($updates.Contains("3819427362  New Mod")) "the update check names the new subscription"
    Check ("$(Invoke-FixtureGit @('rev-parse', 'HEAD'))".Trim() -eq $head) "makes no commit"
    Check (@(Invoke-FixtureGit @("remote")).Count -eq 0) "the fixture has no remote, so nothing can be pushed"
    Check ((Get-TreeHash $workshop) -eq $workshopBefore) "leaves the Workshop folder unchanged"
    $text = Get-Content -LiteralPath (Join-Path $src "tools\capture-all-mod-updates.ps1") -Raw
    Check (-not ($text -match '(?im)(&\s*git|Invoke-Git)\b[^\r\n]*\b(push|commit)\b')) "the script runs no git push or commit"
    $vanilla = @($text -split "`n" | Where-Object { $_ -match 'export-mod-configs\.ps1' -and $_ -match 'IncludeVanilla' })
    Check ($vanilla.Count -eq 0) "the script never runs the export with -IncludeVanilla"
}
finally {
    $env:USERPROFILE = $savedProfile
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
$global:LASTEXITCODE = 0
if ($failed) { Write-Host "$failed check(s) failed"; exit 1 }
Write-Host "all checks passed"
