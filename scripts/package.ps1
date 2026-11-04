param([ValidateSet('Forever', 'Retail', '335')][string]$Client = 'Forever')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$destination = Join-Path $root 'dist'
$sourceToc = Get-Content -LiteralPath (Join-Path $root 'FamiliarFaces/FamiliarFaces.toc') -Raw
$versionMatch = [regex]::Match($sourceToc, '(?m)^## Version: (\d+\.\d+\.\d+)\s*$')
if (-not $versionMatch.Success) { throw 'Missing addon version in FamiliarFaces.toc.' }
$version = $versionMatch.Groups[1].Value
$stage = Join-Path $destination "$version-$Client"
New-Item -ItemType Directory -Force -Path $stage | Out-Null
Copy-Item -LiteralPath (Join-Path $root 'FamiliarFaces') -Destination $stage -Recurse -Force
Copy-Item -LiteralPath (Join-Path $root 'LICENSE') -Destination (Join-Path $stage 'FamiliarFaces/LICENSE') -Force
if ($Client -eq '335' -or $Client -eq 'Forever') {
    $toc = Join-Path $stage 'FamiliarFaces/FamiliarFaces.toc'
    $interface = if ($Client -eq 'Forever') { '16001' } else { '30300' }
    $packagedToc = $sourceToc -replace '(?m)^## Interface: [^\r\n]+', "## Interface: $interface"
    [IO.File]::WriteAllText($toc, $packagedToc, [Text.UTF8Encoding]::new($false))
}
$zip = Join-Path $destination "FamiliarFaces-$version-$Client.zip"
Compress-Archive -LiteralPath (Join-Path $stage 'FamiliarFaces') -DestinationPath $zip -Force
Write-Output $zip
