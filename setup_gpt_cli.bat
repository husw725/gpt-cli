@echo off
setlocal
set "INSTALL_DIR=%~dp0"
cd /d "%INSTALL_DIR%"

echo Setting up gpt-cli for Windows...

REM Check if venv exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Python is not installed or not in PATH.
        exit /b 1
    )
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        exit /b 1
    )
    echo Installing dependencies...
    venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies.
        exit /b 1
    )
)

echo.
echo Success! You can now use 'gpt-cli.bat' from this directory.
echo.
echo To use 'gpt-cli' from any folder:
echo 1. Search for 'Edit the system environment variables' in the Start menu.
echo 2. Click 'Environment Variables'.
echo 3. Under 'User variables', select 'Path' and click 'Edit'.
echo 4. Click 'New' and add this folder: %INSTALL_DIR%
echo.
echo After adding to PATH, you can run: gpt-cli chat "hello"
pause
endlocal
