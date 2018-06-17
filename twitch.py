import urllib, json, os, subprocess, string
url = "https://api.twitch.tv/kraken/users/[USERNAME]/follows/channels?limit=100?client_id=[CLIENT_ID]"
response = urllib.urlopen(url)
data = json.loads(response.read())
follows = data['follows']
count = 1
names = []
for i in follows:
	name = i['channel']['name']
	n_url = "https://api.twitch.tv/kraken/streams/" + name + "?client_id=[CLIENT_ID]"
	n_response = urllib.urlopen(n_url)
	n_data = json.loads(n_response.read())
	n_string = n_data['stream']
	if not (n_string==None):
		n_viewers = n_string['viewers']
		n_game = n_string['game']
		n_channel = n_string['channel']
		n_title = n_channel['status']
		filtered_n_title = filter(lambda x: x in string.printable, n_title)
		if (n_string['stream_type']=='live'):
			if 'rerun' not in filtered_n_title.lower():
				print "[",count,"] ",name,"-",filtered_n_title,"-",n_game,"-",n_viewers
				names.append(name)
				count = count + 1
				
url = "https://api.twitch.tv/kraken/streams?limit=25&client_id=[CLIENT_ID]"
response = urllib.urlopen(url)
data = json.loads(response.read())
streams = data['streams']
for i in streams:
	name = i['channel']['name']
	n_url = "https://api.twitch.tv/kraken/streams/" + name + "?client_id=[CLIENT_ID]"
	n_response = urllib.urlopen(n_url)
	n_data = json.loads(n_response.read())
	n_string = n_data['stream']
	if not (n_string==None):
		n_viewers = n_string['viewers']
		n_game = n_string['game']
		n_channel = n_string['channel']
		n_title = n_channel['status']
		filtered_n_title = filter(lambda x: x in string.printable, n_title)
		if (n_string['stream_type']=='live'):
			if 'rerun' not in filtered_n_title.lower():
				print "[",count,"] ",name,"-",filtered_n_title,"-",n_game,"-",n_viewers
				names.append(name)
				count = count + 1

selection = raw_input("Select stream(s): ")
words = selection.split()
wordString = "/"
for w in words:
	subprocess.call('start ls ' + names[int(w)-1] + ' 720p', shell=True)
	wordString = wordString + names[int(w)-1] + "/";
