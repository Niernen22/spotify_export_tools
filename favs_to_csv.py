import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import requests
import urllib3
import csv
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

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
filenames = {"1": "top_tracks_4weeks.csv", "2": "top_tracks_6months.csv", "3": "top_tracks_alltime.csv"}

time_range = time_ranges.get(choice, "medium_term")
filename = filenames.get(choice, "top_tracks.csv")

# Fetch up to 50 top tracks (API limit)
results = sp.current_user_top_tracks(limit=50, time_range=time_range)
tracks = results["items"]

with open(filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Rank", "Artist(s)", "Song"])
    rank = 1
    for track in tracks:
        artists = ", ".join(a["name"] for a in track["artists"])
        if artists and track["name"]:
            writer.writerow([rank, artists, track["name"]])
        rank += 1

print(f"Saved {len(tracks)} tracks to {filename}")
