@echo off
:: Multiple optimized streamlink configurations for Twitch viewing
:: Usage: lsh_optimized_configs.bat [channel] [quality] [config_number]
:: Config 1: Minimal GPU (default)
:: Config 2: Balanced CPU/GPU  
:: Config 3: Ultra low resource
:: Config 4: Audio-only mode

set channel=%1
set quality=%2
set config=%3

if "%config%"=="" set config=1

echo Using configuration %config% for %channel% at %quality%

if "%config%"=="1" goto :minimal_gpu
if "%config%"=="2" goto :balanced
if "%config%"=="3" goto :ultra_low
if "%config%"=="4" goto :audio_only

:minimal_gpu
echo Configuration 1: Minimal GPU Usage
streamlink --player-args="--no-video-title --avcodec-hw none --vout win32 --aout directsound --network-caching=3000 --live-caching=1500 --no-audio-time-stretch --drop-late-frames --skip-frames --no-overlay --priority high --threads 4 --no-stats --quiet --no-osd" --stream-segment-attempts 3 --stream-segment-timeout 10 --stream-timeout 60 --retry-streams 2 --retry-max 3 --player-continuous-http twitch.tv/%channel% %quality% >nul 2>&1
exit

:balanced
echo Configuration 2: Balanced CPU/GPU
streamlink --player-args="--no-video-title --avcodec-hw auto --vout directx --aout directsound --network-caching=2000 --live-caching=1000 --no-audio-time-stretch --drop-late-frames --skip-frames --priority high --threads 2" --stream-segment-attempts 3 --stream-segment-timeout 10 --stream-timeout 60 --retry-streams 2 --retry-max 3 --player-continuous-http twitch.tv/%channel% %quality% >nul 2>&1
exit

:ultra_low
echo Configuration 3: Ultra Low Resource
streamlink --player-args="--no-video-title --avcodec-hw none --vout win32 --aout directsound --network-caching=5000 --live-caching=2000 --no-audio-time-stretch --drop-late-frames --skip-frames --no-overlay --priority belownormal --threads 1 --video-filter scale --scale=0.5" --stream-segment-attempts 2 --stream-segment-timeout 15 --stream-timeout 90 --retry-streams 1 --retry-max 2 --player-continuous-http twitch.tv/%channel% %quality% >nul 2>&1
exit

:audio_only
echo Configuration 4: Audio Only Mode
streamlink --player-args="--no-video-title --avcodec-hw none --vout dummy --aout directsound --network-caching=1000 --live-caching=500 --no-video --audio-only --priority low --threads 1" --stream-segment-attempts 2 --stream-segment-timeout 15 --stream-timeout 90 --retry-streams 1 --retry-max 2 --player-continuous-http twitch.tv/%channel% audio_only >nul 2>&1
exit
