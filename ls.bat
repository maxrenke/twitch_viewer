@echo off
::live --twitch-oauth-token OAUTHTOKEN twitch.tv/%1 source
streamlink twitch.tv/%1 %2
exit