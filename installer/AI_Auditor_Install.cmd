@echo off
setlocal EnableExtensions

for %%D in ("%~dp0.") do set "BASE=%%~fD"
set "MSI=%BASE%\AI_Auditor_Setup.msi"
set "MODEL=%BASE%\Qwen3-4B-Q4_K_M.gguf"
set "TARGET_DIR=%LOCALAPPDATA%\Programs\AI Auditor\models"
set "TARGET_MODEL=%TARGET_DIR%\Qwen3-4B-Q4_K_M.gguf"

if not exist "%MSI%" (
    echo [ERROR] AI_Auditor_Setup.msi not found.
    pause
    exit /b 1
)

if not exist "%MODEL%" (
    echo [ERROR] Qwen3-4B-Q4_K_M.gguf not found.
    pause
    exit /b 2
)

echo [1/3] Installing AI Auditor...
start /wait msiexec.exe /i "%MSI%"
set "MSI_RC=%ERRORLEVEL%"
if not "%MSI_RC%"=="0" (
    echo [ERROR] MSI installation failed or was cancelled. Exit code: %MSI_RC%
    pause
    exit /b %MSI_RC%
)

echo [2/3] Copying local AI model...
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

robocopy "%BASE%" "%TARGET_DIR%" "Qwen3-4B-Q4_K_M.gguf" /R:2 /W:1 /COPY:DAT /DCOPY:T /NFL /NDL /NJH /NJS /NP
set "RC=%ERRORLEVEL%"
if %RC% GEQ 8 (
    echo [ERROR] Model copy failed. Robocopy exit code: %RC%
    pause
    exit /b %RC%
)

for %%I in ("%MODEL%") do set "SOURCE_SIZE=%%~zI"
for %%I in ("%TARGET_MODEL%") do set "TARGET_SIZE=%%~zI"

if not defined TARGET_SIZE (
    echo [ERROR] Installed model was not found.
    pause
    exit /b 20
)

if not "%SOURCE_SIZE%"=="%TARGET_SIZE%" (
    echo [ERROR] Model size verification failed.
    echo Source: %SOURCE_SIZE%
    echo Target: %TARGET_SIZE%
    pause
    exit /b 21
)

echo [3/3] Installation completed successfully.
echo Installed to: %LOCALAPPDATA%\Programs\AI Auditor
pause
exit /b 0
