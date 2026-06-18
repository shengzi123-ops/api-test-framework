@echo off
chcp 65001 >nul
title API Test Framework Launcher

echo ===============================================
echo          API Test Framework v1.0
echo ===============================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%.."
set PROJECT_ROOT=%cd%

echo [INFO] Project root: %PROJECT_ROOT%
echo.

echo [INFO] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python first.
    pause
    exit /b 1
)

if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo [INFO] Starting test runner...
python "%SCRIPT_DIR%run_tests.py"

echo.
echo ===============================================
echo              Tests completed! Press any key to exit.
echo ===============================================
pause >nul