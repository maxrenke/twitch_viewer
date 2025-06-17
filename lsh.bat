@echo off
::live --twitch-oauth-token  twitch.tv/%1 source
CALL "cmd /c streamlink twitch.tv/%1 %2"
exit