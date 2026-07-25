@echo off
:: Kick.com Stream Browser Launcher
:: This script launches the Python-based Kick stream browser

"C:\Users\m_ren\AppData\Local\Programs\Python\Python313\python.exe" "%~dp0kick.py"

if errorlevel 1 (
    echo.
    echo Error: Python script failed to run.
    echo Make sure Python is installed and the requests library is available.
    echo Install with: pip install requests
    echo.
    pause
)
