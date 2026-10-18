<#
.SYNOPSIS
    Every tools\*.ps1, tools\lib\*.ps1 and tools\tests\*.ps1 parses: a syntax
    error in a script that only runs on the gaming PC (capture-context.ps1,
    fix-load-order.ps1) would otherwise surface there first.

.DESCRIPTION
    Parses each file with PowerShell's own parser and runs nothing. Exit
    code 1 when any file has a parse error, naming the file, the line and
    the message.

        pwsh -File tools/tests/test_scripts_parse.ps1
    (Windows PowerShell 5.1 runs it too.)
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$tools = Split-Path -Parent $PSScriptRoot
$failed = 0
$files = @(Get-ChildItem -LiteralPath $tools -File -Filter *.ps1) +
         @(Get-ChildItem -LiteralPath (Join-Path $tools "lib") -File -Filter *.ps1) +
         @(Get-ChildItem -LiteralPath (Join-Path $tools "tests") -File -Filter *.ps1)
foreach ($f in ($files | Sort-Object FullName)) {
    $tokens = $null; $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors -and $errors.Count) {
        $failed++
        Write-Host ("  FAILED {0}" -f $f.Name)
        foreach ($e in $errors) { Write-Host ("         line {0}: {1}" -f $e.Extent.StartLineNumber, $e.Message) }
    } else {
        Write-Host ("  ok     {0}" -f $f.Name)
    }
}

if ($failed) { Write-Host "$failed file(s) failed to parse"; exit 1 }
Write-Host "all checks passed ($($files.Count) files parsed)"
