import webbrowser
import http.server
import socketserver
import requests

# Set up the OAuth parameters
client_id = "piz7lb40q3umjxhgt9mbux2cvnkppsx"
redirect_uri = "http://localhost"
scope = "user:read:follows"

# Set up the authorization URL
auth_url = f"https://id.twitch.tv/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=token&scope={scope}"

# Open the authorization URL in the user's default web browser
webbrowser.open(auth_url)

# Set up the HTTP server to listen for the redirect URI
class TwitchOAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the access token from the URL fragment
        access_token = self.path.split("access_token=")[1].split("&")[0]
        
        # Print the access token
        print(f"Access Token: {access_token}")
        
        # Send a response to the user's web browser
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Authorization Successful!</h1><p>You can now close this window.</p></body></html>")
        
        # Shut down the HTTP server
        server.shutdown()

# Start the HTTP server to listen for the redirect URI
with socketserver.TCPServer(("", 8000), TwitchOAuthHandler) as server:
    server.serve_forever()
