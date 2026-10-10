$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$AppDir = Join-Path $ProjectRoot "dist\AI_Auditor"
$OutputDir = Join-Path $PSScriptRoot "output"
$WixExe = Join-Path $env:USERPROFILE ".dotnet\tools\wix.exe"
$Source = Join-Path $PSScriptRoot "AI_Auditor.wxs"
$Msi = Join-Path $OutputDir "AI_Auditor_Setup.msi"
$ModelSource = Join-Path $AppDir "models\Qwen3-4B-Q4_K_M.gguf"
$ModelOutput = Join-Path $OutputDir "Qwen3-4B-Q4_K_M.gguf"
$LauncherSource = Join-Path $PSScriptRoot "AI_Auditor_Install.cmd"
$LauncherOutput = Join-Path $OutputDir "AI_Auditor_Install.cmd"

if (-not (Test-Path $WixExe)) {
    throw "WiX executable not found: $WixExe"
}
if (-not (Test-Path (Join-Path $AppDir "AI_Auditor.exe"))) {
    throw "AI Auditor distribution folder not found: $AppDir"
}
if (-not (Test-Path (Join-Path $AppDir "runtime\llama.cpp\llama-server.exe"))) {
    throw "llama-server.exe not found."
}
if (-not (Test-Path $ModelSource)) {
    throw "Qwen3-4B model not found: $ModelSource"
}
if (-not (Test-Path $LauncherSource)) {
    throw "Installer launcher not found: $LauncherSource"
}

New-Item -ItemType Directory -Force $OutputDir | Out-Null
Get-ChildItem $OutputDir -Force | Remove-Item -Recurse -Force

& $WixExe build `
    -acceptEula wix7 `
    -arch x64 `
    -bindpath "app=$AppDir" `
    $Source `
    -o $Msi

if ($LASTEXITCODE -ne 0) {
    throw "WiX MSI build failed. Exit code: $LASTEXITCODE"
}

# The GGUF model exceeds the Windows Installer File-table per-file limit.
# Stage it beside the MSI; AI_Auditor_Install.cmd copies it after MSI install.
Copy-Item $ModelSource $ModelOutput -Force
Copy-Item $LauncherSource $LauncherOutput -Force

# PDB is useful for installer debugging but is not part of the final deployment set.
$WixPdb = Join-Path $OutputDir "AI_Auditor_Setup.wixpdb"
if (Test-Path $WixPdb) {
    Remove-Item $WixPdb -Force
}

Write-Host "MSI package build completed."
Write-Host "Deployment folder: $OutputDir"
Get-ChildItem $OutputDir | Select-Object Name, Length
