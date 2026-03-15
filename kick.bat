@echo off
:: Kick.com Stream Browser Launcher
:: This script launches the Python-based Kick stream browser

echo Starting Kick.com Stream Browser...
python "%~dp0kick.py"

if errorlevel 1 (
    echo.
    echo Error: Python script failed to run.
    echo Make sure Python is installed and the requests library is available.
    echo Install with: pip install requests
    echo.
    pause
)
