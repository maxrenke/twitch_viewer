@echo off
"C:\Users\m_ren\AppData\Local\Programs\Python\Python313\python.exe" "%~dp0twitch.py" %*
if %ERRORLEVEL% neq 0 (
    echo ERROR: twitch.py failed with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)
