import requests
import subprocess
import webbrowser
import sys
from typing import List, Dict, Any, Optional
import json

# Configuration constants
BASE_URL = "https://kick.com/api/v2"
REQUEST_TIMEOUT = 10
MAX_STREAMS_DISPLAY = 50

# Set up session for connection reuse and better performance
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

def get_live_streams(category: str = None, page: int = 1, limit: int = 50) -> List[Dict[str, Any]]:
    """Get live streams from Kick.com API."""
    endpoint = f"{BASE_URL}/channels/live"
    
    params = {
        "page": page,
        "limit": min(limit, MAX_STREAMS_DISPLAY)
    }
    
    if category:
        params["category"] = category
    
    try:
        response = session.get(endpoint, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        # Kick API returns data in different formats, handle both cases
        if isinstance(data, dict):
            if "data" in data:
                return data["data"]
            elif "channels" in data:
                return data["channels"]
        elif isinstance(data, list):
            return data
            
        return []
        
    except requests.RequestException as e:
        print(f"Error fetching live streams: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {e}")
        return []

def get_categories() -> List[Dict[str, Any]]:
    """Get available categories from Kick.com."""
    endpoint = f"{BASE_URL}/categories"
    
    try:
        response = session.get(endpoint, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "data" in data:
            return data["data"]
            
        return []
        
    except requests.RequestException as e:
        print(f"Error fetching categories: {e}")
        return []

def search_channels(query: str) -> List[Dict[str, Any]]:
    """Search for channels on Kick.com."""
    endpoint = f"{BASE_URL}/search/channels"
    
    params = {
        "query": query,
        "limit": 20
    }
    
    try:
        response = session.get(endpoint, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        elif isinstance(data, list):
            return data
            
        return []
        
    except requests.RequestException as e:
        print(f"Error searching channels: {e}")
        return []

def display_streams(streams: List[Dict[str, Any]], title: str = "Live Streams") -> None:
    """Display streams in a formatted table."""
    if not streams:
        print(f"No {title.lower()} found.")
        return
        
    print(f"\n{title} ({len(streams)} found):\n")
    print(" #  |        Username        | Viewers |        Category        |                    Title")
    print("-" * 100)
    
    for i, stream in enumerate(streams, 1):
        # Handle different possible data structures
        username = ""
        viewers = 0
        category = "Unknown"
        title = "No title"
        
        # Extract username
        if "slug" in stream:
            username = stream["slug"]
        elif "user" in stream and isinstance(stream["user"], dict):
            username = stream["user"].get("username", "Unknown")
        elif "username" in stream:
            username = stream["username"]
        
        # Extract viewer count
        if "viewer_count" in stream:
            viewers = stream["viewer_count"]
        elif "viewers_count" in stream:
            viewers = stream["viewers_count"]
        elif "concurrent_viewers" in stream:
            viewers = stream["concurrent_viewers"]
        
        # Extract category
        if "category" in stream and isinstance(stream["category"], dict):
            category = stream["category"].get("name", "Unknown")
        elif "category_name" in stream:
            category = stream["category_name"]
        elif "game" in stream:
            category = stream["game"]
        
        # Extract title
        if "session_title" in stream:
            title = stream["session_title"]
        elif "title" in stream:
            title = stream["title"]
        elif "livestream" in stream and isinstance(stream["livestream"], dict):
            title = stream["livestream"].get("session_title", "No title")
        
        # Truncate long text for display
        username = username[:20]
        category = category[:20]
        title = title[:40] if title else "No title"
        
        print(f" {i:<2} | {username:^22} | {viewers:>7} | {category:^22} | {title:<40}")

def parse_selection(selection: str, max_streams: int) -> List[int]:
    """Parse user selection and return valid stream indices."""
    if not selection.strip():
        return []
        
    indices = []
    words = selection.split()
    
    for word in words:
        try:
            # Handle ranges like "1-5"
            if "-" in word:
                start, end = map(int, word.split("-", 1))
                for i in range(start, min(end + 1, max_streams + 1)):
                    if 1 <= i <= max_streams:
                        indices.append(i - 1)
            else:
                index = int(word)
                if 1 <= index <= max_streams:
                    indices.append(index - 1)  # Convert to 0-based index
                else:
                    print(f"Warning: {index} is out of range (1-{max_streams})")
        except ValueError:
            print(f"Warning: '{word}' is not a valid number or range")
            
    return list(set(indices))  # Remove duplicates

def get_stream_username(stream: Dict[str, Any]) -> str:
    """Extract username from stream data."""
    if "slug" in stream:
        return stream["slug"]
    elif "user" in stream and isinstance(stream["user"], dict):
        return stream["user"].get("username", "unknown")
    elif "username" in stream:
        return stream["username"]
    return "unknown"

def open_vlc_streams(stream_list: List[Dict[str, Any]], indices: List[int]) -> None:
    """Open selected streams in VLC using the lsk.vbs launcher."""
    for index in indices:
        username = get_stream_username(stream_list[index])
        print(f"Opening Kick stream: {username} in VLC")
        try:
            # Use the existing lsk.vbs script to launch streams
            command = f'cmd.exe /c start lsk.vbs {username} best'
            subprocess.call(command, shell=True, cwd=r"C:\Users\m_ren\repos\twitch_viewer")
        except Exception as e:
            print(f"Error opening stream for {username}: {e}")

def open_browser_streams(stream_list: List[Dict[str, Any]], indices: List[int]) -> None:
    """Open selected streams in browser."""
    for index in indices:
        username = get_stream_username(stream_list[index])
        url = f"https://kick.com/{username}"
        print(f"Opening: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening browser for {username}: {e}")

def show_main_menu() -> str:
    """Display main menu and get user choice."""
    print("\n" + "="*60)
    print("              KICK.COM STREAM BROWSER")
    print("="*60)
    print("1. Browse live streams (sorted by viewers)")
    print("2. Search for specific channel")
    print("3. Browse by category")
    print("4. Exit")
    print("-"*60)
    
    return input("Select option (1-4): ").strip()

def main():
    """Main application loop."""
    while True:
        choice = show_main_menu()
        
        if choice == "1":
            # Browse live streams
            print("\nFetching live streams...")
            streams = get_live_streams(limit=MAX_STREAMS_DISPLAY)
            
            if not streams:
                print("No live streams found or error occurred.")
                continue
                
            # Sort by viewer count
            streams.sort(key=lambda x: x.get('viewer_count', x.get('viewers_count', x.get('concurrent_viewers', 0))), reverse=True)
            
            display_streams(streams, "Popular Live Streams")
            
            # VLC selection
            print(f"\nEnter stream numbers to open in VLC (1-{len(streams)}):")
            print("Examples: '1' for single stream, '1 3 5' for multiple, '1-5' for range")
            selection = input("VLC streams: ").strip()
            
            if selection:
                indices = parse_selection(selection, len(streams))
                if indices:
                    open_vlc_streams(streams, indices)
                    continue
            
            # Browser selection
            print("\nEnter stream numbers to open in browser:")
            selection = input("Browser streams: ").strip()
            
            if selection:
                indices = parse_selection(selection, len(streams))
                if indices:
                    open_browser_streams(streams, indices)
        
        elif choice == "2":
            # Search channels
            query = input("\nEnter channel name to search: ").strip()
            if not query:
                continue
                
            print(f"Searching for '{query}'...")
            channels = search_channels(query)
            
            if not channels:
                print("No channels found.")
                continue
                
            display_streams(channels, f"Search Results for '{query}'")
            
            print(f"\nEnter channel numbers to open (1-{len(channels)}):")
            selection = input("Select channels: ").strip()
            
            if selection:
                indices = parse_selection(selection, len(channels))
                if indices:
                    # Ask whether to open in VLC or browser
                    mode = input("Open in (v)lc or (b)rowser? ").lower().strip()
                    if mode.startswith('v'):
                        open_vlc_streams(channels, indices)
                    else:
                        open_browser_streams(channels, indices)
        
        elif choice == "3":
            # Browse by category
            print("\nFetching categories...")
            categories = get_categories()
            
            if not categories:
                print("Could not fetch categories.")
                continue
            
            print("\nAvailable categories:")
            for i, cat in enumerate(categories[:20], 1):  # Show first 20 categories
                cat_name = cat.get("name", "Unknown") if isinstance(cat, dict) else str(cat)
                print(f"{i:2}. {cat_name}")
            
            try:
                cat_choice = int(input(f"\nSelect category (1-{min(len(categories), 20)}): "))
                if 1 <= cat_choice <= min(len(categories), 20):
                    selected_cat = categories[cat_choice - 1]
                    cat_name = selected_cat.get("name", "Unknown") if isinstance(selected_cat, dict) else str(selected_cat)
                    
                    print(f"\nFetching streams for category: {cat_name}")
                    streams = get_live_streams(category=cat_name)
                    
                    if streams:
                        # Sort by viewer count
                        streams.sort(key=lambda x: x.get('viewer_count', x.get('viewers_count', x.get('concurrent_viewers', 0))), reverse=True)
                        display_streams(streams, f"Live Streams in {cat_name}")
                        
                        print(f"\nEnter stream numbers to open in VLC (1-{len(streams)}):")
                        selection = input("Select streams: ").strip()
                        
                        if selection:
                            indices = parse_selection(selection, len(streams))
                            if indices:
                                open_vlc_streams(streams, indices)
                    else:
                        print(f"No live streams found in category: {cat_name}")
                else:
                    print("Invalid category selection.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        elif choice == "4":
            print("\nExiting...")
            break
        
        else:
            print("Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
