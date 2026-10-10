$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$AppDir = Join-Path $ProjectRoot "dist\AI_Auditor"
$OutputDir = Join-Path $PSScriptRoot "output"
$WixExe = Join-Path $env:USERPROFILE ".dotnet\tools\wix.exe"
$Source = Join-Path $PSScriptRoot "AI_Auditor.wxs"
$Msi = Join-Path $OutputDir "AI_Auditor_Setup.msi"

if (-not (Test-Path $WixExe)) {
    throw "WiX 실행파일을 찾을 수 없습니다: $WixExe"
}
if (-not (Test-Path (Join-Path $AppDir "AI_Auditor.exe"))) {
    throw "최종 ZIP(EXE) 후보 폴더가 없습니다: $AppDir"
}
if (-not (Test-Path (Join-Path $AppDir "runtime\llama.cpp\llama-server.exe"))) {
    throw "llama-server.exe가 없습니다."
}
if (-not (Test-Path (Join-Path $AppDir "models\Qwen3-4B-Q4_K_M.gguf"))) {
    throw "Qwen3-4B 모델이 없습니다."
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
    throw "WiX MSI 빌드가 실패했습니다. 종료코드: $LASTEXITCODE"
}

Write-Host "MSI build completed: $Msi"
Get-ChildItem $OutputDir | Select-Object Name, Length
