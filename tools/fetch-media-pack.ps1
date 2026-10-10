<#
.SYNOPSIS
    Download the SEST media pack's photographs from Wikimedia Commons into the
    repo, checking each file's licence on its own page as it goes.

.DESCRIPTION
    integration\media-pack\sources.json lists the 10 Oct 2026 media report's
    Commons items. The build container cannot reach Commons, so the PC fetches
    them: for every still marked "ship", this asks the Commons API for the
    file's size, licence and author, refuses it if the licence is not the one
    the report recorded (or is NonCommercial/NoDerivatives, or the page calls a
    public-domain file copyrighted - the report's Virginia-class rule), and
    saves a copy at most 3840 px wide - enough for a 4K crop, never upscaled -
    under integration\media-pack\source\images\<category>\.

    integration\media-pack\source\fetched.json records what came down: URL,
    size, SHA-256, the licence and author exactly as the file page gave them,
    and when. build_media.py in the container reads it to crop the loading
    screens and write the credits. Videos are stage two and are not fetched.

    Files already present with the recorded SHA-256 are kept, so a re-run only
    fetches what is missing. Nothing in the game install is touched.

.EXAMPLE
    # from the repo root:
    powershell -ExecutionPolicy Bypass -File .\tools\fetch-media-pack.ps1
    git add integration\media-pack\source ; git commit -m "Media pack photographs" ; git push
#>
[CmdletBinding()]
param(
    [int]$MaxWidth = 3840,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot  = Split-Path -Parent $scriptDir
$packDir   = Join-Path $repoRoot "integration\media-pack"
$srcDir    = Join-Path $packDir "source"
$record    = Join-Path $srcDir "fetched.json"
# Wikimedia asks every client to name itself and give a contact.
$agent     = "SEST-media-pack/1.0 (https://github.com/SEST-HOBBY/Seapower-mods)"

$spec = Get-Content -LiteralPath (Join-Path $packDir "sources.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$allowed = @{}
foreach ($p in $spec.allowed_licenses.PSObject.Properties) { $allowed[$p.Name] = $p.Value }

$previous = @{}
if ((Test-Path -LiteralPath $record) -and -not $Force) {
    foreach ($r in (Get-Content -LiteralPath $record -Raw -Encoding UTF8 | ConvertFrom-Json).files) { $previous[$r.id] = $r }
}

function Get-Meta($ext, [string]$name) {
    $v = $ext.$name
    if ($null -eq $v) { return "" }
    # extmetadata values are HTML fragments: keep the text only.
    $t = [regex]::Replace([string]$v.value, "<[^>]+>", "")
    return ([System.Net.WebUtility]::HtmlDecode($t) -replace "\s+", " ").Trim()
}

function Get-Sha256([string]$path) {
    (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLower()
}

$files = @(); $refused = @(); $n = 0
$stills = @($spec.sources | Where-Object { $_.kind -eq "still" -and $_.stage -eq "ship" })
Write-Host "SEST media pack: $($stills.Count) photograph(s) from Wikimedia Commons" -ForegroundColor Cyan
foreach ($s in $stills) {
    $n++
    $dir = Join-Path $srcDir ("images\" + $s.category)
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $out = Join-Path $dir ($s.id + ".jpg")
    $old = $previous[$s.id]
    if ($old -and (Test-Path -LiteralPath $out) -and (Get-Sha256 $out) -eq $old.sha256) {
        Write-Host ("  [{0,2}/{1}] {2,-22} kept (already fetched)" -f $n, $stills.Count, $s.id)
        $files += $old
        continue
    }
    $api = "https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo" +
           "&iiprop=url|size|mime|sha1|extmetadata&iiurlwidth=$MaxWidth&titles=" +
           [uri]::EscapeDataString("File:" + $s.title)
    try {
        $resp = Invoke-RestMethod -Uri $api -UserAgent $agent -TimeoutSec 60
    } catch {
        Write-Warning "$($s.id): Commons API request failed - $($_.Exception.Message)"
        $refused += [pscustomobject]@{ id = $s.id; reason = "API request failed: $($_.Exception.Message)" }
        continue
    }
    $page = @($resp.query.pages.PSObject.Properties)[0].Value
    if (-not $page.imageinfo) {
        $refused += [pscustomobject]@{ id = $s.id; reason = "no such file on Commons: $($s.title)" }
        Write-Warning "$($s.id): no such file on Commons"
        continue
    }
    $ii  = $page.imageinfo[0]
    $ext = $ii.extmetadata
    $lic = Get-Meta $ext "LicenseShortName"
    $copyrighted = Get-Meta $ext "Copyrighted"
    $why = $null
    if ($lic -match "\bNC\b|\bND\b|NonCommercial|NoDeriv|fair use|non-free") {
        $why = "file page licence '$lic' is NonCommercial/NoDerivatives/non-free"
    } elseif ($lic -notmatch $allowed[$s.license]) {
        $why = "file page licence '$lic' is not the $($s.license) the report recorded"
    } elseif ($s.license -eq "LicenseRef-PD-USGov" -and $copyrighted -eq "True") {
        $why = "file page says public domain but marks the file copyrighted"
    }
    if ($why) {
        Write-Warning "$($s.id): REFUSED - $why"
        $refused += [pscustomobject]@{ id = $s.id; reason = $why }
        continue
    }
    $url = if ($ii.width -gt $MaxWidth -and $ii.thumburl) { $ii.thumburl } else { $ii.url }
    $tmp = "$out.part"
    try {
        Invoke-WebRequest -Uri $url -OutFile $tmp -UserAgent $agent -UseBasicParsing -TimeoutSec 180
    } catch {
        Write-Warning "$($s.id): download failed - $($_.Exception.Message)"
        $refused += [pscustomobject]@{ id = $s.id; reason = "download failed: $($_.Exception.Message)" }
        if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp }
        continue
    }
    Move-Item -LiteralPath $tmp -Destination $out -Force
    $kb = [int]((Get-Item -LiteralPath $out).Length / 1KB)
    $files += [pscustomobject]@{
        id              = $s.id
        file            = ("source/images/" + $s.category + "/" + $s.id + ".jpg")
        title           = $s.title
        page            = $ii.descriptionurl
        download_url    = $url
        original_width  = $ii.width
        original_height = $ii.height
        commons_sha1    = $ii.sha1
        sha256          = (Get-Sha256 $out)
        license         = $lic
        license_url     = (Get-Meta $ext "LicenseUrl")
        usage_terms     = (Get-Meta $ext "UsageTerms")
        artist          = (Get-Meta $ext "Artist")
        credit          = (Get-Meta $ext "Credit")
        date            = (Get-Meta $ext "DateTimeOriginal")
        copyrighted     = $copyrighted
        retrieved_at    = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
    Write-Host ("  [{0,2}/{1}] {2,-22} {3,6} KB  {4}" -f $n, $stills.Count, $s.id, $kb, $lic)
    Start-Sleep -Milliseconds 800    # a polite pace for Commons
}

$doc = [pscustomobject]@{
    about   = "Written by tools/fetch-media-pack.ps1 - what came down from Commons and the licence each file page gave."
    agent   = $agent
    files   = $files
    refused = $refused
}
New-Item -ItemType Directory -Force -Path $srcDir | Out-Null
[System.IO.File]::WriteAllText($record, ($doc | ConvertTo-Json -Depth 5), (New-Object System.Text.UTF8Encoding($false)))
Write-Host ""
Write-Host "fetched $($files.Count) of $($stills.Count); refused $($refused.Count). Record: integration\media-pack\source\fetched.json" -ForegroundColor Cyan
if ($refused.Count) { $refused | ForEach-Object { Write-Host "  refused $($_.id): $($_.reason)" -ForegroundColor Yellow } }
