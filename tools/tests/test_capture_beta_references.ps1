[CmdletBinding()]
param([string]$StableAssembly = '')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$capture = Join-Path $repo 'tools/capture-beta-references.ps1'
$reference = Join-Path $repo 'integration/runtime-fixes/SEST.RuntimeFixes.dll'
$temp = Join-Path ([IO.Path]::GetTempPath()) ('SEST-Capture-Test-' + [guid]::NewGuid().ToString('N'))
$checks = 0
function Assert([bool]$Passed, [string]$Message) {
    if (!$Passed) { throw $Message }
    $script:checks++
}
function Put([string]$Relative, [string]$Text) {
    $path = Join-Path $temp $Relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $path) -Force | Out-Null
    [IO.File]::WriteAllText($path, $Text)
    return $path
}
function Put-Dll([string]$Relative) {
    $path = Put $Relative ''
    Copy-Item -LiteralPath $reference -Destination $path -Force
    return $path
}
function Source-Hashes {
    $result = @{}
    foreach ($root in @('game', 'workshop one', 'workshop two', 'player')) {
        foreach ($file in @(Get-ChildItem -LiteralPath (Join-Path $temp $root) -File -Recurse)) {
            $result[$file.FullName] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        }
    }
    return $result
}
try {
    $native = Put-Dll 'game/Sea Power_Data/Managed/Seapower-Scripts.dll'
    $null = Put-Dll 'game/Sea Power_Data/Managed/Noesis.NoesisGUI.dll'
    $null = Put-Dll 'game/Sea Power_Data/Managed/UnityEngine.ParticleSystemModule.dll'
    $null = Put-Dll 'game/BepInEx/core/0Harmony.dll'
    $null = Put-Dll 'game/BepInEx/plugins/nested/AnchorChain.Preloader.dll'
    $null = Put-Dll 'workshop one/3380210757/AnchorChain.dll'
    $null = Put-Dll 'workshop two/3790594162/nested/IdentifyExpanded.dll'
    $null = Put 'workshop two/3790594162/native.dll' 'not a managed assembly'
    $null = Put 'workshop two/3790594162/audio/broadcast/track.mp3' 'PRIVATE MEDIA'
    $null = Put 'game/Sea Power_Data/StreamingAssets/IdentifyExpanded/audio/broadcast/local.mp3' 'LOCAL MEDIA'
    $null = Put 'game/BepInEx/config/private.cfg' 'PRIVATE CONFIG'
    $null = Put 'player/saves/test.sav' 'PRIVATE SAVE'
    $null = Put 'player/usersettings.ini' "[Private]`nSecret=DO-NOT-CAPTURE`n[LoadOrder]`nNumberOfModFiles=2`nMod1Directory=3790594162,True`nMod2Directory=IdentifyExpanded,False`n[Other]`nSecret=ALSO-PRIVATE`n"
    $null = Put 'game/BepInEx/LogOutput.log' 'File C:\Users\SamplePerson\Steam; Steam ID 76561198012345678'
    $null = Put 'player/Player.log' 'Beta launched and exited'
    $before = Source-Hashes
    $options = @{
        GameRoot = (Join-Path $temp 'game')
        WorkshopContentRoot = @((Join-Path $temp 'workshop one'), (Join-Path $temp 'workshop two'))
        PlayerDataRoot = (Join-Path $temp 'player')
        OutDirectory = (Join-Path $temp 'output with spaces')
    }
    & $capture @options
    $archives = @(Get-ChildItem -LiteralPath $options.OutDirectory -Filter '*.zip')
    Assert ($archives.Count -eq 1) 'Expected one capture ZIP'
    $extract = Join-Path $temp 'extracted'
    Expand-Archive -LiteralPath $archives[0].FullName -DestinationPath $extract
    $receipt = Get-Content -LiteralPath (Join-Path $extract 'capture.json') -Raw | ConvertFrom-Json
    Assert ($receipt.installation_changed -eq $false) 'Capture must not install anything'
    Assert ($receipt.build_status -eq 'unreviewed-build-captured-for-inspection') 'Unknown build must remain unreviewed'
    Assert ($receipt.references.Count -eq 7) 'All seven managed references across both libraries must be present'
    Assert ($receipt.native_sha256 -eq (Get-FileHash -LiteralPath $native -Algorithm SHA256).Hash.ToLowerInvariant()) 'Native hash mismatch'
    foreach ($item in $receipt.references) {
        $path = Join-Path $extract $item.path
        Assert (Test-Path -LiteralPath $path -PathType Leaf) ('Missing reference: ' + $item.path)
        Assert (((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()) -eq $item.sha256) ('Bad hash: ' + $item.path)
    }
    $names = @(Get-ChildItem -LiteralPath $extract -File -Recurse | ForEach-Object { $_.FullName.Substring($extract.Length + 1).Replace('\', '/') })
    Assert ($names -contains 'references/workshop/library-2/3790594162/nested/IdentifyExpanded.dll') 'Second Steam library omitted'
    Assert (@($names | Where-Object { $_ -match '\.(mp3|sav|cfg)$|native\.dll$|usersettings\.ini$' }).Count -eq 0) 'Private/media/native files were included'
    $loadOrder = [IO.File]::ReadAllText((Join-Path $extract 'reports/load-order.ini'))
    Assert ($loadOrder -match '3790594162,True' -and $loadOrder -notmatch 'PRIVATE|Secret') 'Only load order should be captured'
    $log = [IO.File]::ReadAllText((Join-Path $extract 'reports/BepInEx.log'))
    Assert ($log -match '<USER>' -and $log -match '<STEAM_ID>' -and $log -notmatch 'SamplePerson|76561198012345678') 'Log redaction failed'
    Assert ([IO.File]::ReadAllText((Join-Path $extract 'reports/local-mod-folders.txt')) -match 'IdentifyExpanded') 'Local generated folder was not reported'
    $after = Source-Hashes
    Assert ($before.Count -eq $after.Count) 'Capture added or removed a source file'
    foreach ($name in $before.Keys) { Assert ($before[$name] -eq $after[$name]) ('Source changed: ' + $name) }
    $unsafeOptions = $options.Clone()
    $unsafeOptions.OutDirectory = Join-Path $options.GameRoot 'capture-output'
    $blocked = $false
    try { & $capture @unsafeOptions } catch { $blocked = $_.Exception.Message -match 'outside the game' }
    Assert $blocked 'An output inside the game should be rejected'
    Assert (!(Test-Path -LiteralPath $unsafeOptions.OutDirectory)) 'Rejected output still wrote into the game'
    if ($StableAssembly) {
        Copy-Item -LiteralPath $StableAssembly -Destination $native -Force
        $stableOptions = $options.Clone()
        $stableOptions.OutDirectory = Join-Path $temp 'stable-must-not-write'
        $blocked = $false
        try { & $capture @stableOptions } catch { $blocked = $_.Exception.Message -match 'stable build' }
        Assert $blocked 'Known stable build should be rejected'
        Assert (!(Test-Path -LiteralPath $stableOptions.OutDirectory)) 'Stable rejection wrote an output'
    }
    # Steam can report the same library through registry values, a default
    # path and libraryfolders.vdf with different slash/dot/trailing forms.
    $autoRoot = Join-Path $temp 'auto/Steam'
    $null = Put-Dll 'auto/Steam/steamapps/common/Sea Power/Sea Power_Data/Managed/Seapower-Scripts.dll'
    $autoAlias = $autoRoot.Replace('\', '/') + '/.'
    $vdfText = '"libraryfolders" { "0" { "path" "' + $autoRoot.Replace('\', '\\') + '" } "1" { "path" "' + $autoAlias.Replace('\', '\\') + '" } }'
    $null = Put 'auto/Steam/steamapps/libraryfolders.vdf' $vdfText
    $oldPrograms = [Environment]::GetEnvironmentVariable('ProgramFiles')
    $oldProgramsX86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
    try {
        [Environment]::SetEnvironmentVariable('ProgramFiles', (Join-Path $temp 'auto'))
        [Environment]::SetEnvironmentVariable('ProgramFiles(x86)', (Join-Path $temp 'auto'))
        function Get-ItemProperty {
            param([string]$LiteralPath)
            return [pscustomobject]@{ SteamPath = $autoRoot; InstallPath = $autoAlias }
        }
        $autoOptions = $options.Clone()
        $autoOptions.Remove('GameRoot')
        $autoOptions.OutDirectory = Join-Path $temp 'auto-output'
        & $capture @autoOptions
        $autoArchives = @(Get-ChildItem -LiteralPath $autoOptions.OutDirectory -Filter '*.zip')
        Assert ($autoArchives.Count -eq 1) 'Aliases of a single installation should be selected automatically'
        $autoExtract = Join-Path $temp 'auto-extracted'
        Expand-Archive -LiteralPath $autoArchives[0].FullName -DestinationPath $autoExtract
        $autoReceipt = Get-Content -LiteralPath (Join-Path $autoExtract 'capture.json') -Raw | ConvertFrom-Json
        Assert ($autoReceipt.references.Count -eq 3) 'Automatic selection should capture one game and both Workshop libraries once'
        $null = Put-Dll 'second/steamapps/common/Sea Power/Sea Power_Data/Managed/Seapower-Scripts.dll'
        $secondLibrary = Join-Path $temp 'second'
        $vdfText += ' "2" { "path" "' + $secondLibrary.Replace('\', '\\') + '" }'
        $null = Put 'auto/Steam/steamapps/libraryfolders.vdf' $vdfText
        $blocked = $false
        try { & $capture @autoOptions } catch {
            $blocked = $_.Exception.Message -match 'Multiple Sea Power installations' -and
                $_.Exception.Message.Contains($secondLibrary)
        }
        Assert $blocked 'Two different installations must be listed instead of silently choosing one'
    } finally {
        Remove-Item -LiteralPath 'Function:\Get-ItemProperty'
        [Environment]::SetEnvironmentVariable('ProgramFiles', $oldPrograms)
        [Environment]::SetEnvironmentVariable('ProgramFiles(x86)', $oldProgramsX86)
    }
    Write-Host "Beta reference capture passed: $checks assertions (fixture, not a Windows beta gameplay test)." -ForegroundColor Green
} finally {
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Recurse -Force }
}
