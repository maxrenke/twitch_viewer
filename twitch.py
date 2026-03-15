import subprocess, webbrowser, sys, os, warnings, json, time, ctypes, ctypes.wintypes, msvcrt
from concurrent.futures import ThreadPoolExecutor, as_completed
warnings.filterwarnings("ignore", message="urllib3")
import requests, unicodedata
from colorama import init, Fore, Style
from collections import defaultdict

init(autoreset=True)

# --- Color constants ---
C_TITLE   = Fore.WHITE  + Style.BRIGHT
C_HEADER  = Fore.WHITE  + Style.BRIGHT
C_NUM     = Fore.YELLOW + Style.BRIGHT
C_NAME    = Fore.WHITE  + Style.BRIGHT
C_VIEWERS = Fore.YELLOW
C_GAME    = Fore.WHITE
C_STREAM  = Style.DIM
C_RESET   = Style.RESET_ALL

# --- Layout constants ---
IDX_W  = 4
NAME_W = 16
VIEW_W = 7
GAME_W = 24
TTL_W  = 50
WIDTH  = 110

# --- Emoji replacement table (module-level, built once) ---
EMOJI_REPLACEMENTS = {
    '\U0001f525': '[~]',   # 🔥 fire
    '\U0001f4a5': '[!]',   # 💥 explosion
    '\U0001f3c6': '[*]',   # 🏆 trophy
    '\U0001f4af': '[%]',   # 💯 100
    '\u2764':     '<3',    # ❤ heart
    '\U0001f499': '<3',    # 💙 blue heart
    '\U0001f49c': '<3',    # 💜 purple heart
    '\U0001f49a': '<3',    # 💚 green heart
    '\U0001f34e': '[o]',   # 🍎
    '\U0001f480': '[x]',   # 💀 skull
    '\u26a1':     '[z]',   # ⚡ lightning
    '\u2b50':     '[*]',   # ⭐ star
    '\U0001f31f': '[*]',   # 🌟 glowing star
    '\U0001f3b5': '[p]',   # 🎵 music note
    '\U0001f3b6': '[p]',   # 🎶 music notes
    '\U0001f6ab': '[no]',  # 🚫
    '\U0001f4e2': '[!]',   # 📢 megaphone
    '\U0001f4a1': '[i]',   # 💡 bulb
}


# --- Helpers ---
def read_line(prompt="  > "):
    """Read a line of input without the CMD newline-after-prompt bug."""
    sys.stdout.write(prompt)
    sys.stdout.flush()
    chars = []
    while True:
        ch = msvcrt.getwch()
        if ch in ('\r', '\n'):
            sys.stdout.write('\n')
            sys.stdout.flush()
            return ''.join(chars)
        elif ch == '\x08':  # backspace
            if chars:
                chars.pop()
                sys.stdout.write('\x08 \x08')
                sys.stdout.flush()
        elif ch == '\x03':  # ctrl+c
            raise KeyboardInterrupt
        else:
            chars.append(ch)
            sys.stdout.write(ch)
            sys.stdout.flush()

def hr(char=chr(9472), width=WIDTH, color=Fore.WHITE + Style.DIM):
    print(color + char * width + C_RESET)

def fmt_viewers(n):
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)

def clean_title(text):
    """Replace colored emoji with plain placeholders, drop the rest."""
    result = []
    for ch in text:
        if ch in EMOJI_REPLACEMENTS:
            result.append(EMOJI_REPLACEMENTS[ch])
        else:
            cat = unicodedata.category(ch)
            if cat.startswith(('L', 'N', 'P', 'Z')) or cat in ('Sm', 'Sc') or ch in (' ', '\t'):
                result.append(ch)
    return ''.join(result).strip()

def parse_selection(raw, stream_list):
    """Parse space-separated stream numbers. Returns valid indices, prints errors for bad input."""
    valid = []
    for w in raw.split():
        try:
            idx = int(w) - 1
            if not (0 <= idx < len(stream_list)):
                print(Fore.RED + f"  x {w} out of range (valid 1-{len(stream_list)})" + C_RESET)
            else:
                valid.append(idx)
        except ValueError:
            print(Fore.RED + f"  x '{w}' is not a number — skipping" + C_RESET)
    return valid

def resize_terminal(n_streams):
    # Fixed rows: banner(2) + login(1) + cache(1) + blank(1) + header(2) + explainer(1) + footer(3) + prompts(4) + slack(3)
    FIXED_ROWS = 18
    rows = FIXED_ROWS + n_streams
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
    print(C_TITLE + "  TWITCH LIVE".center(WIDTH))
    hr(chr(9552), WIDTH, Fore.WHITE)

def print_header():
    print(C_HEADER +
        f"  {'#':>{IDX_W}}  {'Streamer':<{NAME_W}}  {'Views':>{VIEW_W}}  {'Game':<{GAME_W}}  {'':2}{'Title':<{TTL_W}}" +
        C_RESET)
    hr()


# --- Config & API ---
try:
    from config import CLIENT_ID, BEARER_TOKEN, USER_ID
except ImportError:
    CLIENT_ID = BEARER_TOKEN = USER_ID = None

API_HDR    = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {BEARER_TOKEN}"} if CLIENT_ID else {}
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "twitch_followed_cache.json")
CACHE_TTL  = 24 * 60 * 60  # seconds

force_refresh = "--refresh" in sys.argv or "-r" in sys.argv
by_game       = "--no-game" not in sys.argv and "-G" not in sys.argv

# --- API fetch functions ---
def fetch_login():
    """Return logged-in username, or None. Also detects expired token."""
    if not CLIENT_ID:
        return None, "no_config"
    try:
        r = requests.get("https://api.twitch.tv/helix/users", headers=API_HDR, timeout=5)
        if r.status_code == 401:
            return None, "expired"
        data = r.json().get("data", [])
        return (data[0]["login"], "ok") if data else (None, "error")
    except Exception:
        return None, "error"

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

def fetch_streams(id_chunk):
    r = requests.get("https://api.twitch.tv/helix/streams",
                     headers=API_HDR, params={"user_id": id_chunk, "first": 100})
    return r.json().get("data", [])


# --- Phase 1: load followed IDs (cache or fetch) ---
cache_used   = False
followed_ids = None

if not force_refresh and os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        if time.time() - cache["timestamp"] < CACHE_TTL:
            followed_ids = cache["ids"]
            cache_used = True
    except Exception:
        pass  # corrupt cache — fall through to fresh fetch

if followed_ids is None:
    followed_ids = fetch_followed_ids()
    with open(CACHE_FILE, "w") as f:
        json.dump({"timestamp": time.time(), "ids": followed_ids}, f)

# --- Phase 2: fetch streams + login in parallel ---
chunks = [followed_ids[i:i+100] for i in range(0, len(followed_ids), 100)]
stream_list = []

with ThreadPoolExecutor() as executor:
    login_future   = executor.submit(fetch_login)
    stream_futures = [executor.submit(fetch_streams, chunk) for chunk in chunks]
    for f in as_completed(stream_futures):
        stream_list.extend(f.result())
    login, login_status = login_future.result()

# --- Render banner & status line ---
resize_terminal(len(stream_list))
banner()

if cache_used:
    import datetime
    with open(CACHE_FILE) as f:
        ts = json.load(f)["timestamp"]
    age_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    left = f"  follows: cached ({age_str})  |  run with -r to refresh"
else:
    left = f"  follows: refreshed ({len(followed_ids)} channels cached)"

if login_status == "ok":
    right = f"logged in as: {login}  "
    right_colored = C_STREAM + right
elif login_status == "expired":
    right = "token expired — regenerate Bearer token  "
    right_colored = Fore.RED + right
else:
    right = "not logged in — see config.py  "
    right_colored = Fore.RED + right

print(C_STREAM + left + right_colored.rjust(WIDTH - len(left)) + C_RESET)
print()


# --- Favorite rules ---
ALWAYS_FAVORITE          = {"Hearthstone"}
ALWAYS_FAVORITE_STREAMER = {"nyybeats"}
CONDITIONAL_FAVORITE     = {"Dota 2": 10_000}   # game -> minimum total viewers to pin

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
    prefix  = (Fore.YELLOW + Style.BRIGHT + "♥ " + C_RESET) if favorite else "  "
    c_name  = (Fore.YELLOW + Style.BRIGHT) if favorite else C_NAME
    drops   = any(t.lower() == "dropsenabled" for t in (stream.get("tags") or []))
    drop_pfx = Fore.YELLOW + "★ " + C_RESET if drops else "  "
    raw_title = f"{clean_title(stream['title'])[:TTL_W]:<{TTL_W}}"
    idx   = C_NUM     + f"{i:>{IDX_W}}" + C_RESET
    name  = c_name    + f"{stream['user_name']:<{NAME_W}}" + C_RESET
    views = C_VIEWERS + f"{fmt_viewers(stream['viewer_count']):>{VIEW_W}}" + C_RESET
    game  = C_GAME    + f"{stream['game_name'][:GAME_W]:<{GAME_W}}" + C_RESET
    title = drop_pfx + C_STREAM + raw_title + C_RESET
    print(f"{prefix}{idx}  {name}  {views}  {game}  {title}")

# --- Build sorted list: favorites first, then rest by viewers ---
favorites   = [s for s in stream_list if is_favorite(s)]
rest        = [s for s in stream_list if not is_favorite(s)]
favorites.sort(key=lambda x: x["viewer_count"], reverse=True)
rest.sort(key=lambda x: x["viewer_count"], reverse=True)
stream_list = favorites + rest

# --- Group by game if needed (favorites always stay on top) ---
if by_game:
    non_fav_list = [s for s in stream_list if not is_favorite(s)]
    games = defaultdict(list)
    for s in non_fav_list:
        games[s["game_name"]].append(s)
    sorted_games = sorted(games.items(), key=lambda kv: sum(s["viewer_count"] for s in kv[1]), reverse=True)
    stream_list = favorites[:]
    for _, streams in sorted_games:
        stream_list.extend(streams)

# --- Render stream list ---
if not stream_list:
    print(C_STREAM + "  No followed channels are live right now." + C_RESET)
    print()
else:
    print_header()
    for i, stream in enumerate(stream_list):
        print_row(i + 1, stream, favorite=is_favorite(stream))


# --- Selection prompts ---
hr(chr(9552), WIDTH, Fore.WHITE)
print(C_STREAM + "  Enter stream numbers below. Blank VLC → skip to TwitchTheater. Blank both → exit." + C_RESET)
print()
print(C_HEADER + "  Open in VLC" + C_RESET + "  " + C_STREAM + "(space-separated, blank to skip)" + C_RESET)
vlc_selection = read_line()

if vlc_selection.strip():
    indices = parse_selection(vlc_selection, stream_list)
    if not indices:
        print(Fore.RED + "  x No valid streams selected." + C_RESET)
    else:
        ls_vbs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ls.vbs")
        if not os.path.exists(ls_vbs):
            print(Fore.RED + f"  x ls.vbs not found at {ls_vbs}" + C_RESET)
            sys.exit(1)
        for idx in indices:
            wstring = stream_list[idx]["user_login"]
            print(Fore.GREEN + f"  > Opening {wstring} in VLC..." + C_RESET)
            subprocess.call(f'cmd.exe /c start "" "{ls_vbs}" {wstring} best', shell=True)
    sys.exit()

print()
print(C_HEADER + "  Open in TwitchTheater" + C_RESET + "  " + C_STREAM + "(space-separated, blank to exit)" + C_RESET)
tt_selection = read_line()

if not tt_selection.strip():
    sys.exit()

indices = parse_selection(tt_selection, stream_list)
if not indices:
    print(Fore.RED + "  x No valid streams selected." + C_RESET)
else:
    word_string = "".join("/" + stream_list[idx]["user_login"] for idx in indices)
    tturl = "www.twitchtheater.tv" + word_string
    print(Fore.GREEN + f"  > Opening {tturl}" + C_RESET)
    webbrowser.open(tturl)
