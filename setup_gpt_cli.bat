@echo off
set "INSTALL_DIR=%~dp0"
echo Setting up gpt-cli for Windows...

REM Check if venv exists
if not exist "%INSTALL_DIR%venv" (
    echo Virtual environment not found at %INSTALL_DIR%venv
    echo Please run 'python -m venv venv' and 'venv\Scripts\pip install -r requirements.txt' first.
    exit /b 1
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
