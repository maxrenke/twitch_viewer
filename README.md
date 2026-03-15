# twitch_viewer

> ⚠️ **Personal use tool** — built for my own setup (Windows, VLC, specific follows/favorites).
> If you want to adapt it, you'll likely need to change credentials, favorites, pinning logic,
> and launcher paths. It works great for me but makes no attempt to be a general-purpose app.

A terminal-based Twitch stream browser. Shows your followed channels that are live, lets you
pick streams to open in VLC or TwitchTheater.

## Features

- Lists all live followed channels sorted by viewer count
- Favorites pinned to the top (configurable streamers + games)
- Game-grouped view by default (`--no-game` / `-G` for flat list)
- Drops-enabled streams flagged with a ★
- Opens streams in VLC via streamlink, or in TwitchTheater for multi-stream
- Followed channel list cached for 24h (run with `-r` to force refresh)

## Dependencies

- [Python 3.10+](https://www.python.org/) with `requests` and `colorama`
- [Streamlink](https://github.com/streamlink/streamlink)
- [VLC Media Player](https://www.videolan.org/vlc/)

```bash
pip install requests colorama
```

## Setup

1. Copy `config.example.py` to `config.py` and fill in your Twitch credentials:
   - **Client ID + Bearer Token**: [Twitch Developer Console](https://dev.twitch.tv/console)
   - **User ID**: [Find your user ID here](https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/)

2. Edit the favorites/pinning rules in `newtwitch.py`:
   ```python
   ALWAYS_FAVORITE          = {"Hearthstone"}           # games always pinned
   ALWAYS_FAVORITE_STREAMER = {"nyybeats"}              # streamers always pinned
   CONDITIONAL_FAVORITE     = {"Dota 2": 10_000}        # games pinned if viewers >= threshold
   ```

3. Update `tw.bat` with your Python path if needed.

## Usage

```
tw              # launch (game-grouped by default)
tw -r           # force refresh followed channel cache
tw --no-game    # flat list sorted by viewers
```

Select streams by number at the prompt — space-separated for multiple.
Opens in VLC (via streamlink) or TwitchTheater.

## Files

| File | Description |
|---|---|
| `twitch.py` | Main script |
| `tw.bat` | Launcher (calls twitch.py) |
| `ls.vbs` | Opens a stream in VLC via streamlink |
| `lsh.bat` | Streamlink wrapper with VLC args |
| `config.py` | Your credentials — **gitignored, never committed** |
| `config.example.py` | Template for config.py |
| `kick.py` / `kick.bat` | Kick.com browser (experimental, API unstable) |
