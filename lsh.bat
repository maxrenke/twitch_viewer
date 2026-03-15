@echo off

streamlink ^
  --twitch-low-latency ^
  --stream-segment-attempts 5 ^
  --stream-segment-timeout 10 ^
  --retry-streams 3 ^
  --retry-max 5 ^
  --player-continuous-http ^
  --player-no-close ^
  --player-args="--play-and-exit --no-video-title-show --qt-minimal-view --avcodec-hw=dxva2 --network-caching=900" ^
  twitch.tv/%1 best

if errorlevel 1 (
    echo.
    echo Streamlink failed with exit code %errorlevel%
    echo Press any key to continue...
    pause >nul
)
