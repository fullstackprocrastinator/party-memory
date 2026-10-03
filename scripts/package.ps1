param([ValidateSet('Forever', 'Retail', '335')][string]$Client = 'Forever')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$destination = Join-Path $root 'dist'
$stage = Join-Path $destination $Client
New-Item -ItemType Directory -Force -Path $stage | Out-Null
Copy-Item -LiteralPath (Join-Path $root 'PartyMemory') -Destination $stage -Recurse -Force
Copy-Item -LiteralPath (Join-Path $root 'LICENSE') -Destination (Join-Path $stage 'PartyMemory/LICENSE') -Force
if ($Client -eq '335' -or $Client -eq 'Forever') {
    $toc = Join-Path $stage 'PartyMemory/PartyMemory.toc'
    $interface = if ($Client -eq 'Forever') { '40601' } else { '30300' }
    (Get-Content -LiteralPath $toc -Raw).Replace('120007', $interface) | Set-Content -LiteralPath $toc -Encoding utf8
}
$zip = Join-Path $destination "PartyMemory-0.1.0-$Client.zip"
Compress-Archive -LiteralPath (Join-Path $stage 'PartyMemory') -DestinationPath $zip -Force
Write-Output $zip
