# Spotify Export Tools

A collection of Python scripts to export and analyze your Spotify listening data.

## Setup

### 1. Install dependencies
```
pip install spotipy yt-dlp
```

### 2. Create a Spotify Developer App
1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Set the Redirect URI to `http://127.0.0.1:5000`
4. Note your **Client ID** and **Client Secret**

### 3. Create a Last.fm API account
1. Go to https://www.last.fm/api/account/create
2. Note your **API key**

### 4. Configure credentials
Create a `config.py` file in the project folder:
```python
SPOTIFY_CLIENT_ID     = "your_spotify_client_id"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"
SPOTIFY_REDIRECT_URI  = "http://127.0.0.1:5000"
LASTFM_API_KEY        = "your_lastfm_api_key"
```

### 5. First run (authentication)
On the first run of any Spotify script, a browser window will open asking you to log in and authorize the app. After approving, a `.cache` file is created and you won't need to log in again.

---

## Scripts

### `playlist_to_csv.py`
Exports a Spotify playlist to a CSV file.

```
python playlist_to_csv.py
```
- Prompts for a playlist name
- Saves `PlaylistName.csv` with columns: `Artist(s)`, `Song`

---

### `favs_to_csv.py`
Exports your top 50 most listened tracks to a CSV file.

```
python favs_to_csv.py
```
- Choose time range: last 4 weeks / 6 months / all time
- Saves a CSV with columns: `Rank`, `Artist(s)`, `Song`

---

### `output_moods.py`
Analyzes your top artists and displays a mood/genre profile in the terminal using Last.fm tags.

```
python output_moods.py
```
- Choose time range: last 4 weeks / 6 months / all time
- Prints a ranked breakdown of your listening moods (e.g. Indie, Rock, Dance, Pop)

---

### `playlist_download.py`
Downloads tracks from a CSV file as MP3s using YouTube.

```
python playlist_download.py
```
- Lists all CSV files in the folder to choose from
- Downloads MP3s into a subfolder named after the CSV
- Skips already downloaded tracks
- Saves a `failed.txt` if any tracks couldn't be found

#### Additional requirements
- **ffmpeg**: Place `ffmpeg.exe` and `ffprobe.exe` in the project folder (download from https://www.gyan.dev/ffmpeg/builds/)
- **Node.js** (optional but recommended): Install from https://nodejs.org to improve YouTube extraction

---

## Notes
- These scripts disable SSL certificate verification to work on corporate networks. Use on trusted networks only.
- Downloading copyrighted music may be against YouTube's Terms of Service and local laws. Use responsibly.
- `config.py` and `.cache` are gitignored and will never be committed.
