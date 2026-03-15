import subprocess, webbrowser, sys, os, warnings, json, time, ctypes, ctypes.wintypes
from concurrent.futures import ThreadPoolExecutor, as_completed
warnings.filterwarnings("ignore", message="urllib3")
import requests
from colorama import init, Fore, Back, Style
from collections import defaultdict

init(autoreset=True)

C_TITLE    = Fore.WHITE  + Style.BRIGHT
C_HEADER   = Fore.WHITE  + Style.BRIGHT
C_NUM      = Fore.YELLOW + Style.BRIGHT
C_NAME     = Fore.WHITE  + Style.BRIGHT
C_VIEWERS  = Fore.YELLOW
C_GAME     = Fore.WHITE
C_STREAM   = Style.DIM
C_RESET    = Style.RESET_ALL

def hr(char=chr(9472), width=110, color=Fore.WHITE + Style.DIM):
    print(color + char * width + C_RESET)

def resize_terminal(n_streams, by_game_mode):
    # Fixed rows: banner(2) + cache line(1) + blank(1) + header(2) + footer(3) + prompts(4) + slack(3)
    FIXED_ROWS = 16
    # In by-game mode each game adds a header bar row; rough estimate: assume avg 2 streams/game
    extra = (n_streams // 2) if by_game_mode else 0
    rows = FIXED_ROWS + n_streams + extra
    cols = 114  # 110 content + 4 for prefix icons/padding

    k32 = ctypes.windll.kernel32
    STDOUT = k32.GetStdHandle(-11)

    class COORD(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

    class SMALL_RECT(ctypes.Structure):
        _fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short),
                    ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]

    buf = COORD(cols, max(rows, 50))
    k32.SetConsoleScreenBufferSize(STDOUT, buf)

    win = SMALL_RECT(0, 0, cols - 1, rows - 1)
    k32.SetConsoleWindowInfo(STDOUT, True, ctypes.byref(win))

def banner():
    print()
    print(C_TITLE + "  TWITCH LIVE".center(110))
    hr(chr(9552), 110, Fore.WHITE)

def fmt_viewers(n):
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)

from config import CLIENT_ID, BEARER_TOKEN, USER_ID
API_HDR    = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {BEARER_TOKEN}"}
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "twitch_followed_cache.json")
CACHE_TTL  = 24 * 60 * 60  # seconds

force_refresh = "--refresh" in sys.argv or "-r" in sys.argv

# --- Phase 1: load followed IDs from cache, or fetch and cache them ---
def fetch_followed_ids():
    ids = []
    params = {"from_id": USER_ID, "first": 100}
    while True:
        r = requests.get(f"https://api.twitch.tv/helix/channels/followed?user_id={USER_ID}",
                         headers=API_HDR, params=params)
        data = r.json()
        for ch in data["data"]:
            ids.append(ch["broadcaster_id"])
        if "pagination" in data and "cursor" in data["pagination"]:
            params["after"] = data["pagination"]["cursor"]
        else:
            break
    return ids

cache_used = False
followed_ids = None

if not force_refresh and os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        age = time.time() - cache["timestamp"]
        if age < CACHE_TTL:
            followed_ids = cache["ids"]
            cache_used = True
    except Exception:
        pass  # corrupt cache - fall through to fresh fetch

if followed_ids is None:
    followed_ids = fetch_followed_ids()
    with open(CACHE_FILE, "w") as f:
        json.dump({"timestamp": time.time(), "ids": followed_ids}, f)

# --- Phase 2: fetch live streams in parallel (100 IDs per request) ---
def fetch_streams(id_chunk):
    r = requests.get("https://api.twitch.tv/helix/streams",
                     headers=API_HDR, params={"user_id": id_chunk, "first": 100})
    return r.json().get("data", [])

chunks = [followed_ids[i:i+100] for i in range(0, len(followed_ids), 100)]
stream_list = []
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(fetch_streams, chunk) for chunk in chunks]
    for f in as_completed(futures):
        stream_list.extend(f.result())

by_game = "--no-game" not in sys.argv and "-G" not in sys.argv

resize_terminal(len(stream_list), by_game)
banner()

if cache_used:
    import datetime
    with open(CACHE_FILE) as f:
        ts = json.load(f)["timestamp"]
    age_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    print(C_STREAM + f"  follows: cached ({age_str})  |  run with -r to refresh" + C_RESET)
else:
    print(C_STREAM + f"  follows: refreshed ({len(followed_ids)} channels cached)" + C_RESET)
print()
IDX_W  = 4
NAME_W = 16
VIEW_W = 7
GAME_W = 24
TTL_W  = 50
COL_W  = 110

def print_header():
    print(
        C_HEADER +
        f"  {'#':>{IDX_W}}  {'Streamer':<{NAME_W}}  {'Views':>{VIEW_W}}  {'Game':<{GAME_W}}  {'':2}{'Title':<{TTL_W}}" +
        C_RESET
    )
    hr()

# --- Favorite rules ---
ALWAYS_FAVORITE = {"Hearthstone"}
ALWAYS_FAVORITE_STREAMER = {"nyybeats"}
CONDITIONAL_FAVORITE = {"Dota 2": 10_000}   # game -> minimum total viewers to pin

def game_total_viewers(game_name):
    return sum(s["viewer_count"] for s in stream_list if s["game_name"] == game_name)

def is_favorite(s):
    if s["user_login"].lower() in ALWAYS_FAVORITE_STREAMER:
        return True
    g = s["game_name"]
    if g in ALWAYS_FAVORITE:
        return True
    if g in CONDITIONAL_FAVORITE and game_total_viewers(g) >= CONDITIONAL_FAVORITE[g]:
        return True
    return False

def print_row(i, stream, favorite=False):
    if favorite:
        prefix = Fore.YELLOW + Style.BRIGHT + "♥ " + C_RESET
        c_name = Fore.YELLOW + Style.BRIGHT
    else:
        prefix = "  "
        c_name = C_NAME
    drops      = any(t.lower() == "dropsenabled" for t in (stream.get("tags") or []))
    drop_pfx   = Fore.YELLOW + "★ " + C_RESET if drops else "  "
    raw_title  = stream["title"][:TTL_W]
    raw_title  = f"{raw_title:<{TTL_W}}"
    idx   = C_NUM     + f"{i:>{IDX_W}}" + C_RESET
    name  = c_name    + f"{stream['user_name']:<{NAME_W}}" + C_RESET
    views = C_VIEWERS + f"{fmt_viewers(stream['viewer_count']):>{VIEW_W}}" + C_RESET
    game  = C_GAME    + f"{stream['game_name'][:GAME_W]:<{GAME_W}}" + C_RESET
    title = drop_pfx + C_STREAM + raw_title + C_RESET
    print(f"{prefix}{idx}  {name}  {views}  {game}  {title}")

# --- Build sorted list: favorites first (sorted by viewers), then rest by viewers ---
favorites   = [s for s in stream_list if is_favorite(s)]
rest        = [s for s in stream_list if not is_favorite(s)]

favorites.sort(key=lambda x: x["viewer_count"], reverse=True)
rest.sort(key=lambda x: x["viewer_count"], reverse=True)

# stream_list in display order (important: selection by index uses this)
stream_list = favorites + rest

if by_game:
    # Group only non-favorites by game, sorted by total viewers per game
    non_fav_list = [s for s in stream_list if not is_favorite(s)]
    games = defaultdict(list)
    for s in non_fav_list:
        games[s["game_name"]].append(s)
    sorted_games = sorted(games.items(), key=lambda kv: sum(s["viewer_count"] for s in kv[1]), reverse=True)

    # rebuild stream_list: favorites first, then game-sorted rest
    stream_list = favorites[:]
    for game_name, streams in sorted_games:
        stream_list.extend(streams)

    print_header()
    for i, stream in enumerate(stream_list):
        print_row(i + 1, stream, favorite=is_favorite(stream))
else:
    print_header()
    for i, stream in enumerate(stream_list):
        print_row(i + 1, stream, favorite=is_favorite(stream))

hr(chr(9552), 110, Fore.WHITE)
print()

print(C_HEADER + "  Open in VLC" + C_RESET + "  " + C_STREAM + "(stream numbers, space-separated, blank to skip)" + C_RESET)
sys.stdout.write(C_NUM + "  > " + C_RESET)
sys.stdout.flush()
selection = input()

if selection.strip():
    for w in selection.split():
        try:
            stream_index = int(w) - 1
            if not (0 <= stream_index < len(stream_list)):
                print(Fore.RED + f"  x Invalid: {w} (valid 1-{len(stream_list)})" + C_RESET)
                continue
            wstring = stream_list[stream_index]["user_login"]
            print(Fore.GREEN + f"  > Opening {wstring} in VLC..." + C_RESET)
            if not os.path.exists("ls.vbs"):
                print(Fore.RED + "  x ls.vbs not found" + C_RESET)
                continue
            subprocess.call(f"cmd.exe /c start ls.vbs {wstring} best", shell=True)
        except ValueError:
            print(Fore.RED + f"  x '{w}' is not a valid number" + C_RESET)
        except Exception as e:
            print(Fore.RED + f"  x Error: {e}" + C_RESET)
    sys.exit()

print()
print(C_HEADER + "  Open in TwitchTheater" + C_RESET + "  " + C_STREAM + "(stream numbers, space-separated)" + C_RESET)
sys.stdout.write(C_NUM + "  > " + C_RESET)
sys.stdout.flush()
selection = input()

wordString = ""
for w in selection.split():
    wordString += "/" + stream_list[int(w) - 1]["user_login"]

if wordString:
    tturl = "www.twitchtheater.tv" + wordString
    print(Fore.GREEN + f"  > Opening {tturl}" + C_RESET)
    webbrowser.open(tturl)
