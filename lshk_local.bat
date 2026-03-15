@echo off
:: Kick.com streamlink launcher with optimized VLC settings
:: Usage: lshk_local.bat <channel_name> <quality>
:: Example: lshk_local.bat channelname best

:: Optimized streamlink settings for reduced GPU load and better performance
:: VLC player args for hardware decoding, reduced caching, and performance optimization
CALL "cmd /c streamlink --player-args="--intf dummy --play-and-exit --no-video-title --avcodec-hw any --network-caching=1000 --live-caching=500 --no-audio-time-stretch --drop-late-frames --skip-frames" --hls-segment-attempts 5 --hls-segment-timeout 15 --hls-timeout 60 --retry-streams 2 --retry-max 3 --player-continuous-http --player-no-close kick.com/%1 %2"
exit
