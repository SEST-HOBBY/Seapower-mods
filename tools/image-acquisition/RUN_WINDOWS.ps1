# Run from PowerShell: .\RUN_WINDOWS.ps1
# Downloads licensed images to this folder; does not touch Sea Power.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) { & py -3 .\fetch_images.py --mode all }
else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) { throw 'Python 3 not found. Install Python 3.9+ from python.org, then run this script again.' }
    & python .\fetch_images.py --mode all
}
if ($LASTEXITCODE -ne 0) { throw "Image download script returned exit code $LASTEXITCODE" }
if (Test-Path -LiteralPath .\CONTACT_SHEET.html) { Invoke-Item .\CONTACT_SHEET.html }
