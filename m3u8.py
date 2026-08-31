import requests

url = "https://fa723fc1b171.us-west-2.playback.live-video.net/api/video/v1/us-west-2.196233775518.channel.NH8IpsfoBirH.m3u8?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzM4NCJ9.eyJhd3M6Y2hhbm5lbC1hcm4iOiJhcm46YXdzOml2czp1cy13ZXN0LTI6MTk2MjMzNzc1NTE4OmNoYW5uZWwvTkg4SXBzZm9CaXJIIiwiYXdzOmFjY2Vzcy1jb250cm9sLWFsbG93LW9yaWdpbiI6Imh0dHBzOi8va2ljay5jb20saHR0cHM6Ly9wbGF5ZXIua2ljay5jb20saHR0cHM6Ly9hZG1pbi5raWNrLmNvbSxodHRwczovL3d3dy5nc3RhdGljLmNvbSIsImF3czpzdHJpY3Qtb3JpZ2luLWVuZm9yY2VtZW50IjpmYWxzZSwiZXhwIjoxNzEwNDQ2NDU3fQ.3WYHf9ddrrqNmJNg1gJ_jfKZQXYIg9Au-nOvCk4C4pDhhyu64vx0J4NArZnf88pYwl-5GVsSZuOllykYaLcpjjiv0c28DYzqbFijCGj54rPEvSOrfTpfyq7Y3Et0qI0a&player_version=1.18.0"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept": "application/x-mpegURL, application/vnd.apple.mpegurl, application/json, text/plain",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://kick.com/",
    "Origin": "https://kick.com",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Sec-GPC": "1",
    "permissions-policy": "interest-cohort=()",
    "TE": "trailers"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Response content:")
    print(response.content)
else:
    print(f"Error: Status code {response.status_code}")
