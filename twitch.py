import urllib, json, os, subprocess
url = "https://api.twitch.tv/kraken/users/[USERNAME]/follows/channels?oauth_token=oauth:[OATHCODE]"
response = urllib.urlopen(url)
data = json.loads(response.read())
follows = data['follows']
count = 1
names = []
for i in follows:
	name = i['channel']['name']
	n_url = "https://api.twitch.tv/kraken/streams/" + name
	n_response = urllib.urlopen(n_url)
	n_data = json.loads(n_response.read())
	n_string = n_data['stream']
	if not (n_string==None):
		print "[",count,"] ",name
		names.append(name)
		count = count + 1
selection = raw_input("Select stream(s): ")
words = selection.split()
for w in words:
	subprocess.call('start ls ' + names[int(w)-1] + ' best', shell=True)
