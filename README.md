# twitch_viewer
python script to integrate with livestreamer on Windows

Twitch Oauth Code - https://twitchapps.com/tmi/

Livestreamer - http://docs.livestreamer.io/

Python 2.7 - https://www.python.org/download/releases/2.7/

VLC - http://www.videolan.org/vlc/index.html

# Installation

Install VLC

Install Livestreamer

Install Python 2.7

Place twitch.py, tw.bat, and ls.bat in your User Directory (Windows)

Modify twitch.py with your username and place it where [USERNAME] is

Modify twitch.py with your oauth code (empty in repository) and place it where [OAUTHCODE] is

# Usage

From run or command line type 'tw' OR 'python twitch.py'

You can select one or more than one stream. They will open up in separate instances of VLC. The original window will close

# Configuration

You need to add your oauth code to the twitch.py script.

You may want to change how ls.bat works, I have it hard coded for 'source' quality

tw.bat is just what I use as an alias on Windows

# Notes

Sometimes channels you follow won't appear in the script, you'll need to go to Twitch.com and re-follow them to show up.
