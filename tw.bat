@echo off
C:\Users\m_ren\AppData\Local\Programs\Python\Python313\python.exe C:\users\m_ren\newtwitch.py %*
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python script failed with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)