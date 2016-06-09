@echo off
:: save as live.bat in livestreamer folder
:: use it in the same way [Win+R]: live twitch.tv/joindotared high
PUSHD %~dp0
echo On Error Resume Next> "%temp%\~1337run.vbs"
echo CreateObject("Wscript.Shell").Run "livestreamer "+WScript.Arguments(0)+" "+WScript.Arguments(1),0,False>> "%temp%\~1337run.vbs"
echo Err.Clear>> "%temp%\~1337run.vbs"
CALL CSCRIPT //nologo "%temp%\~1337run.vbs" %~1 %~2 &DEL /F /Q "%temp%\~1337run.vbs" &EXIT /B