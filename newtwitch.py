import subprocess
import webbrowser
import requests

# Set up the API endpoint and headers
endpoint = "https://api.twitch.tv/helix/channels/followed?user_id=26714826"
headers = {
    "Client-ID": "",
    "Authorization": "Bearer "
}

# Set up the query parameters
params = {
    "from_id": "26714826", # user id of the user whose followed channels we want to get
    "first": 100 # maximum number of results to return per page
}

user_ids = []
stream_list = []
# Make the API request
while True:
    response = requests.get(endpoint, headers=headers, params=params)

    # Parse the JSON response
    data = response.json()

    for channel in data["data"]:
        user_ids.append(channel["broadcaster_id"])


    # Get the live streams for the followed user IDs
    streams_url = "https://api.twitch.tv/helix/streams"
    streams_params = {"user_id": user_ids}
    streams_response = requests.get(streams_url, headers={"Client-ID": "piz7lb40q3umjxhgt9mbux2cvnkppsx", "Authorization": "Bearer 7smpkxcby3g830r730vzrw9iq2clma"}, params=streams_params)
    streams_data = streams_response.json()

    for stream in streams_data["data"]:
        stream_list.append(stream)
        #print(f"{stream['user_name']} | {stream['viewer_count']}")
    user_ids = []

    # Check if there are more pages to fetch
    if "pagination" in data and "cursor" in data["pagination"]:
        params["after"] = data["pagination"]["cursor"]

    else:
        break

# Sort the streams by viewer count
stream_list.sort(key=lambda x: x['viewer_count'], reverse=True)

for i, stream in enumerate(stream_list):
    print(" {:<2} | {:^15} | {:>7} | {:^22} | {:^50}".format(i+1,stream['user_name'], stream['viewer_count'], stream['game_name'][:25], stream['title'][:50]))

selection = input("Select stream(s) [vlc]: ")
words = selection.split()
for w in words:
    wstring = stream_list[int(w)-1]['user_login']
    print("opening stream: " + wstring + " in vlc")
    subprocess.call('start ls.vbs ' + wstring + ' best', shell=True)

if( selection != "" ): exit()

selection = input("Select stream(s) [tt]: ")
words = selection.split()
wordString = ""
for w in words:
	wordString = wordString + "/" + stream_list[int(w)-1]['user_login']
if wordString:
    tturl = "www.twitchtheater.tv" + wordString
    #tturl = "https://multitwitch.tv" + wordString
    #tturl = "www.multistre.am" + wordString
    print("opening: " + tturl)
    
    #firefox_path = "\"C:\\Program Files\\Mozilla Firefox\\firefox.exe\""
    #browser_path = "\"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe\""
    #subprocess.call(browser_path + " " + tturl, shell=False)
    webbrowser.open(tturl)