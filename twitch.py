import urllib, json, os, subprocess, string
clientID = ""
count = 1
names = []
offset = 0
offset_interval = 100

print "----------------------\n-- Followed Streams --\n----------------------"
url = "https://api.twitch.tv/kraken/users/stupidgeek314/follows/channels?limit=100&client_id=" + clientID
response = urllib.urlopen(url)
data = json.loads(response.read())
follows = data['follows']
while len(follows) > 0:
	for i in follows:
		name = i['channel']['name']
		n_url = "https://api.twitch.tv/kraken/streams/" + name + "?client_id=" + clientID
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
					n_output = name + "-" + filtered_n_title + "-" + n_game + "-" + str(n_viewers)
					names.append([n_viewers, n_output, name])
					count = count + 1
	
	offset = offset + offset_interval
	url = "https://api.twitch.tv/kraken/users/stupidgeek314/follows/channels?limit=100&client_id=" + clientID + "&offset=" + str(offset)
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	follows = data['follows']

names = sorted(names, key=lambda name: name[0], reverse=True)

i = 1
for name in names:
	if i < 10:
		print "[ ",i,"]",str(name[1])
	else:
		print "[",i,"]",str(name[1])
	i = i + 1
	
print "---------------------\n-- Popular Streams --\n---------------------"
url = "https://api.twitch.tv/kraken/streams?limit=25&client_id=" + clientID
response = urllib.urlopen(url)
data = json.loads(response.read())
streams = data['streams']
for i in streams:
	name = i['channel']['name']
	n_url = "https://api.twitch.tv/kraken/streams/" + name + "?client_id=" + clientID
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
				n_output = name + "-" + filtered_n_title + "-" + n_game + "-" + str(n_viewers)
				print "[",count,"]",n_output
				names.append([n_viewers, n_output, name])
				count = count + 1
				
selection = raw_input("Select stream(s): ")
words = selection.split()
wordString = "/"
for w in words:
	subprocess.call('start ls ' + str(names[int(w)-1][2]) + ' 720p60', shell=True)
	wordString = wordString + str(names[int(w)-1][2]) + "/";