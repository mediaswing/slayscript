@echo off
REM SlayScript Windows Build Script
REM Creates a standalone executable using PyInstaller

echo ========================================
echo   SlayScript Build Script for Windows
echo   Cast spells, slay bugs.
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not available
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo.
echo Building SlayScript executable...
echo.

REM Build the executable
pyinstaller --onefile ^
    --name slayscript ^
    --add-data "slayscript;slayscript" ^
    --hidden-import pyttsx3.drivers ^
    --hidden-import pyttsx3.drivers.sapi5 ^
    --console ^
    slayscript_cli.py

if errorlevel 1 (
    echo.
    echo Error: Build failed
    exit /b 1
)

echo.
echo ========================================
echo   Build complete!
echo   Executable: dist\slayscript.exe
echo ========================================
echo.
echo To run SlayScript:
echo   dist\slayscript.exe examples\hello_world.slay
echo.
echo To start the REPL:
echo   dist\slayscript.exe
echo.

pause
