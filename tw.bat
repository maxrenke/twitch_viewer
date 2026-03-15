@echo off
python "%~dp0twitch.py" %*
if %ERRORLEVEL% neq 0 (
    echo ERROR: twitch.py failed with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)
