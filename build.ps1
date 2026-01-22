# SlayScript Windows Build Script (PowerShell)
# Creates a standalone executable using PyInstaller

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SlayScript Build Script for Windows" -ForegroundColor Cyan
Write-Host "  Cast spells, slay bugs." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org"
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "Step 1: Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Could not install all requirements" -ForegroundColor Yellow
}

pip install pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install PyInstaller" -ForegroundColor Red
    exit 1
}

# Clean previous builds
Write-Host ""
Write-Host "Step 2: Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "slayscript.spec") { Remove-Item -Force "slayscript.spec" }

# Build
Write-Host ""
Write-Host "Step 3: Building executable..." -ForegroundColor Yellow
pyinstaller --onefile `
    --name slayscript `
    --add-data "slayscript;slayscript" `
    --hidden-import pyttsx3.drivers `
    --hidden-import pyttsx3.drivers.sapi5 `
    --console `
    --noconfirm `
    slayscript_cli.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: Build failed" -ForegroundColor Red
    exit 1
}

# Copy examples
Write-Host ""
Write-Host "Step 4: Copying examples..." -ForegroundColor Yellow
if (Test-Path "dist/examples") { Remove-Item -Recurse -Force "dist/examples" }
Copy-Item -Recurse "examples" "dist/examples"

# Done
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Build complete!" -ForegroundColor Green
Write-Host "  Executable: dist\slayscript.exe" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To run SlayScript:"
Write-Host "  .\dist\slayscript.exe examples\hello_world.slay" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the REPL:"
Write-Host "  .\dist\slayscript.exe" -ForegroundColor Cyan
Write-Host ""
