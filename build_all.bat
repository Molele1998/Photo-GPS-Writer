@echo off
chcp 65001 >nul
echo ========================================
echo Photo GPS Writer - Build All Versions
echo ========================================
echo.

echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo Clean complete!
echo.

echo [1/2] Building single-file version...
python -m PyInstaller --noconfirm PhotoGPSWriter_singlefile.spec
if errorlevel 1 (
    echo Error: Failed to build single-file version
    pause
    exit /b 1
)
echo Single-file version built successfully!
echo.

echo [2/2] Building folder version...
python -m PyInstaller --noconfirm PhotoGPSWriter_folder.spec
if errorlevel 1 (
    echo Error: Failed to build folder version
    pause
    exit /b 1
)
echo Folder version built successfully!
echo.

echo ========================================
echo Build complete!
echo ========================================
echo Single-file: dist\PhotoGPSWriter.exe
echo Folder version: dist\PhotoGPSWriter\
echo ========================================
echo.
pause
