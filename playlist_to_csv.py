import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import requests
import urllib3
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ["BROWSER"] = "chrome"

# Patch all requests sessions globally to skip SSL verification
_original_request = requests.Session.request
def _no_verify_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return _original_request(self, method, url, **kwargs)
requests.Session.request = _no_verify_request

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-read-private"
))

playlist_name = input("Enter playlist name: ")

playlists = sp.current_user_playlists()
target = next(
    (p for p in playlists["items"] if p["name"] == playlist_name),
    None
)

if not target:
    print("Playlist not found")
    exit()

print(f"Found playlist: {target['name']} (id: {target['id']})")

# Fetch all tracks (handles pagination)
results = sp.playlist_tracks(target["id"])
tracks = results["items"]
while results["next"]:
    results = sp.next(results)
    tracks.extend(results["items"])

print(f"Total items fetched: {len(tracks)}")

import csv
filename = f"{target['name']}.csv"
with open("exported_lists/" + filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Artist(s)", "Song"])
    for entry in tracks:
        track = entry.get("track") or entry.get("item")
        if track:
            artists = ", ".join(a["name"] for a in track["artists"])
            writer.writerow([artists, track["name"]])

print(f"Saved to {filename}")
