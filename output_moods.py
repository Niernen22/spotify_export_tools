import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import requests
import urllib3
from collections import Counter
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, LASTFM_API_KEY

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ["BROWSER"] = "chrome"

_original_request = requests.Session.request
def _no_verify_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return _original_request(self, method, url, **kwargs)
requests.Session.request = _no_verify_request

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-top-read"
))

print("Time range options:")
print("  1 - Last 4 weeks")
print("  2 - Last 6 months")
print("  3 - All time")
choice = input("Choose (1/2/3): ").strip()

time_ranges = {"1": "short_term", "2": "medium_term", "3": "long_term"}
time_range = time_ranges.get(choice, "medium_term")

# Fetch top 50 artists from Spotify
results = sp.current_user_top_artists(limit=50, time_range=time_range)
artists = [a["name"] for a in results["items"]]

def get_lastfm_tags(artist_name):
    try:
        resp = requests.get("http://ws.audioscrobbler.com/2.0/", params={
            "method": "artist.gettoptags",
            "artist": artist_name,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        }, timeout=5)
        tags = resp.json().get("toptags", {}).get("tag", [])
        return [t["name"].lower() for t in tags[:10]]
    except Exception:
        return []

print(f"\nFetching tags for {len(artists)} artists from Last.fm...")
all_tags = []
for name in artists:
    tags = get_lastfm_tags(name)
    all_tags.extend(tags)

IGNORE_TAGS = {
    "usa", "american", "united states", "russian", "dutch", "italy", "italian",
    "french", "german", "british", "canadian", "australian", "swedish", "norwegian",
    "hungarian", "hungary", "chicago", "london", "boston",
    "los angeles", "california", "minnesota", "netherlands", "belgium", "belgian",
    "australia", "uk", "us", "korean", "chinese", "polish", "finnish",
    "female vocalists", "female vocal", "male vocalists", "male vocalist", "ai-generated", "ai",
    "my top songs", "all", "booba", "seen live", "favorites", "good", "my ladies",
    "4", "dj", "pixel", "hairy chest", "hunks", "70s", "80s", "90s", "00s",
    "lost frequencies", "eurovision", "russia", "germany", "arabic", "england", "united kingdom",
    "norway", "norwegian", "irish", "ireland", "latvia", "latvian", "icelandic", "iceland",
    "colombia", "colombian", "world",
    "to tag", "multiple artists", "upcoming album 2024", "papa pappa ping",
    "xiqix", "3", "cait", "the worst thing ever to happen to music",
    "murder republicans", "anti-trump", "tones and i", "missio",
    "female singer", "new russian wave", "3-5", "singles", "collection",
    "deezer", "yandex music", "ai slop", "onerepublic", "david guetta", "hollywood undead",
    "under 2000 listeners", "5 stars", "need to rate", "the green man festival 2005",
    "next big thing", "various artists are a pita on lastfm", "rating 5 stars - ok",
    "gambling addiction", "girl group", "stellar", "sexy",
    "daddy yankee", "madison beer", "sabrina carpenter", "nessa barrett",
    "international", "eclectic", "turkey", "turkish", "european"
}

MOOD_KEYWORDS = {
    "Dark":               ["dark", "goth", "black metal", "doom", "death metal", "horror", "occult",
                           "sinister", "darkwave", "witch house", "industrial", "noise"],
    "Sad / Melancholic":  ["sad", "melanchol", "emo", "grief", "heartbreak", "tearjerker",
                           "depressing", "emotional", "crying"],
    "Angry / Intense":    ["metal", "hardcore", "punk", "rage", "aggressive", "brutal",
                           "thrash", "grindcore", "screamo", "heavy"],
    "Rock":               ["rock", "hard rock", "progressive rock", "symphonic prog", "classic rock",
                           "grunge", "garage rock", "stoner rock", "arena rock", "glam rock"],
    "Happy / Upbeat":     ["happy", "feel-good", "sunshine", "cheerful", "fun", "joyful",
                           "positive", "upbeat", "summer", "bop"],
    "Chill / Relaxed":    ["chill", "lo-fi", "lofi", "relax", "mellow", "laid-back", "ambient",
                           "sleep", "calm", "peaceful", "soft", "slow",
                           "reggae", "psybient", "psydub", "new age", "downtempo",
                           "lounge", "trip-hop", "trip hop"],
    "Latino":             ["latin", "latino", "latina", "reggaeton", "salsa", "cumbia", "bachata",
                           "merengue", "flamenco", "samba", "bossa nova", "cuba", "cuban",
                           "spanish", "tropical", "urbano", "dembow", "mexican",
                           "puerto rico", "puerto rican"],
    "Energetic":          ["energetic", "hype", "workout", "power", "adrenaline", "uplifting",
                           "motivational", "epicore", "epic"],
    "Dance / Electronic": ["dance", "edm", "electro", "house", "techno", "trance", "rave",
                           "club", "disco", "synth", "dubstep", "drum and bass", "dnb",
                           "chiptune", "pico pico", "vaporwave", "future bass",
                           "hardbass", "speedcore"],
    "Acoustic / Folk":    ["acoustic", "folk", "singer-songwriter", "singer songwriter",
                           "singer and songwriter", "unplugged", "country", "bluegrass",
                           "americana", "roots", "guitar", "ukulele"],
    "Romantic":           ["romantic", "love", "soul", "r&b", "rnb", "smooth", "sensual", "passion",
                           "ballad", "slow jam", "wedding"],
    "Instrumental":       ["instrumental", "classical", "orchestra", "jazz", "piano",
                           "cinematic", "soundtrack", "score", "neoclassical"],
    "Hip-Hop / Rap":      ["hip hop", "hip-hop", "rap", "trap", "drill", "boom bap", "grime"],
    "Indie / Alternative":["indie", "alternative", "alt rock", "alt-z", "alt z", "altz", "alt", "dream pop",
                           "shoegaze", "shogaze", "dreamgaze", "post-punk", "art rock",
                           "experimental", "psychedelic", "bedroom pop", "lo fi", "noise pop",
                           "twee", "jangle pop", "new wave"],
    "J-Pop / Anime":      ["vocaloid", "otacore", "shibuya-kei", "anime", "j-pop", "jpop",
                           "j pop", "visual kei", "city pop", "japanese"],
    "Pop":                ["pop", "teen pop", "electropop", "synth-pop", "k-pop", "disney"],
}

mood_counts = Counter()
other_tags = []
for tag in all_tags:
    if tag in IGNORE_TAGS:
        continue
    matched = False
    for mood, keywords in MOOD_KEYWORDS.items():
        if any(kw in tag for kw in keywords):
            mood_counts[mood] += 1
            matched = True
            break
    if not matched:
        mood_counts["Other"] += 1
        other_tags.append(tag)

total = sum(mood_counts.values())

print(f"Total tags collected: {len(all_tags)}\n")
print(f"{'Rank':<6} {'Mood / Style':<26} {'Tags':<8} {'Share'}")
print("-" * 55)
for rank, (mood, count) in enumerate(mood_counts.most_common(10), start=1):
    bar = "█" * int((count / total) * 25)
    print(f"{rank:<6} {mood:<26} {count:<8} {bar} {count/total*100:.1f}%")

print("\nTop unclassified 'Other' tags:")
for tag, count in Counter(other_tags).most_common(20):
    print(f"  {count:>4}x  {tag}")
