$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "[1/7] Validate required local assets..."
$requiredPaths = @(
    ".\main.py",
    ".\assets",
    ".\runtime\llama.cpp\llama-server.exe",
    ".\models\Qwen3-4B-Q4_K_M.gguf",
    ".\data\ai_auditor.db"
)
foreach ($path in $requiredPaths) {
    if (-not (Test-Path $path)) {
        throw "Required path not found: $path"
    }
}

Write-Host "[2/7] Clean previous build output..."
if (Test-Path ".\build") {
    Remove-Item ".\build" -Recurse -Force
}
if (Test-Path ".\dist\AI_Auditor") {
    Remove-Item ".\dist\AI_Auditor" -Recurse -Force
}
if (Test-Path ".\dist\AI_Auditor_Portable.zip") {
    Remove-Item ".\dist\AI_Auditor_Portable.zip" -Force
}
if (Test-Path ".\dist\AI_Auditor_Portable.zip.sha256.txt") {
    Remove-Item ".\dist\AI_Auditor_Portable.zip.sha256.txt" -Force
}

Write-Host "[3/7] Build PyInstaller onedir package..."
python -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --windowed `
    --name AI_Auditor `
    --add-data "assets;assets" `
    main.py
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE"
}

$distApp = ".\dist\AI_Auditor"
if (-not (Test-Path "$distApp\AI_Auditor.exe")) {
    throw "AI_Auditor.exe was not generated."
}

Write-Host "[4/7] Copy Local AI runtime, model, and database..."
Copy-Item ".\runtime" "$distApp\runtime" -Recurse -Force
Copy-Item ".\models" "$distApp\models" -Recurse -Force
Copy-Item ".\data" "$distApp\data" -Recurse -Force

Write-Host "[5/7] Verify final portable structure..."
$finalRequiredPaths = @(
    "$distApp\AI_Auditor.exe",
    "$distApp\runtime\llama.cpp\llama-server.exe",
    "$distApp\models\Qwen3-4B-Q4_K_M.gguf",
    "$distApp\data\ai_auditor.db",
    "$distApp\_internal"
)
foreach ($path in $finalRequiredPaths) {
    if (-not (Test-Path $path)) {
        throw "Final package validation failed. Missing: $path"
    }
}

Write-Host "[6/7] Create ZIP package..."
$tar = Get-Command tar.exe -ErrorAction SilentlyContinue
if (-not $tar) {
    throw "Windows tar.exe was not found. ZIP packaging cannot continue."
}
Push-Location ".\dist"
try {
    & tar.exe -a -c -f "AI_Auditor_Portable.zip" "AI_Auditor"
    if ($LASTEXITCODE -ne 0) {
        throw "ZIP creation failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

Write-Host "[7/7] Create SHA-256 checksum..."
$zipPath = ".\dist\AI_Auditor_Portable.zip"
if (-not (Test-Path $zipPath)) {
    throw "Portable ZIP was not generated."
}
$hash = Get-FileHash $zipPath -Algorithm SHA256
"$($hash.Hash)  AI_Auditor_Portable.zip" | Set-Content ".\dist\AI_Auditor_Portable.zip.sha256.txt" -Encoding ASCII

$modelSize = (Get-Item ".\models\Qwen3-4B-Q4_K_M.gguf").Length
$zipSize = (Get-Item $zipPath).Length

Write-Host ""
Write-Host "Portable build completed successfully."
Write-Host "Folder : $((Resolve-Path $distApp).Path)"
Write-Host "ZIP    : $((Resolve-Path $zipPath).Path)"
Write-Host ("Model  : {0:N2} GB" -f ($modelSize / 1GB))
Write-Host ("ZIP    : {0:N2} GB" -f ($zipSize / 1GB))
Write-Host "SHA256 : $($hash.Hash)"
