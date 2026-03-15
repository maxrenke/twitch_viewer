@echo off
streamlink --player-args="--intf dummy --play-and-exit --no-video-title --avcodec-hw any --network-caching=1000 --live-caching=500 --no-audio-time-stretch --drop-late-frames --skip-frames" --hls-segment-attempts 5 --hls-segment-timeout 15 --hls-timeout 60 --retry-streams 2 --retry-max 3 --player-continuous-http --player-no-close twitch.tv/%1 %2
