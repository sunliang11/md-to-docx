# Remove Explorer context menus installed by desktop/windows/install.ps1.
$ErrorActionPreference = "Continue"

$InstallDir = Join-Path $env:LOCALAPPDATA "md-to-docx"

$keys = @(
    "HKCU:\Software\Classes\SystemFileAssociations\.md\shell\md-to-docx-convert",
    "HKCU:\Software\Classes\SystemFileAssociations\.markdown\shell\md-to-docx-convert",
    "HKCU:\Software\Classes\SystemFileAssociations\.docx\shell\md-to-docx-reverse"
)

foreach ($k in $keys) {
    if (Test-Path -LiteralPath $k) {
        Remove-Item -LiteralPath $k -Recurse -Force
        Write-Host "Removed $k"
    }
}

if (Test-Path -LiteralPath $InstallDir) {
    Remove-Item -LiteralPath $InstallDir -Recurse -Force
    Write-Host "Removed $InstallDir"
}

Write-Host "Removed Explorer context menus for md-to-docx."
Write-Host "(CLI package itself was not uninstalled.)"
