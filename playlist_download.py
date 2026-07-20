import csv
import os
import subprocess
import sys

# List available CSVs in the current folder
csv_files = [f for f in os.listdir(".") if f.endswith(".csv")]
if not csv_files:
    print("No CSV files found in the current folder.")
    sys.exit()

print("Available CSV files:")
for i, f in enumerate(csv_files, start=1):
    print(f"  {i}. {f}")

choice = input("\nEnter number or filename: ").strip()

if choice.isdigit() and 1 <= int(choice) <= len(csv_files):
    csv_file = csv_files[int(choice) - 1]
else:
    csv_file = choice if choice.endswith(".csv") else choice + ".csv"

if not os.path.exists(csv_file):
    print(f"File '{csv_file}' not found.")
    sys.exit()

# Create output folder named after the CSV
folder_name = os.path.splitext(csv_file)[0]
os.makedirs(folder_name, exist_ok=True)

# Read tracks from CSV
with open(csv_file, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = [row for row in reader]

# Detect column names (support both playlist and favourites CSV formats)
sample = rows[0] if rows else {}
artist_col = next((k for k in sample if "artist" in k.lower()), None)
song_col = next((k for k in sample if "song" in k.lower()), None)

if not artist_col or not song_col:
    print(f"Could not detect Artist/Song columns. Found: {list(sample.keys())}")
    sys.exit()

total = len(rows)
skipped = 0
failed = []

print(f"\nDownloading {total} tracks to '{folder_name}/'...\n")

for i, row in enumerate(rows, start=1):
    artist = row[artist_col].strip()
    song = row[song_col].strip()

    if not artist or not song:
        continue

    query = f"{artist} - {song}"
    print(f"[{i}/{total}] {query}")

    result = subprocess.run(
        [
            sys.executable, "-m", "yt_dlp",
            "--no-check-certificate",
            "--ffmpeg-location", os.path.dirname(os.path.abspath(__file__)),
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--output", os.path.join(folder_name, "%(title)s.%(ext)s"),
            "--no-playlist",
            "--match-filter", "duration < 600",
            "--no-overwrites",
            "--quiet",
            "--progress",
            f"ytsearch1:{query}"
        ],
        capture_output=False
    )

    if result.returncode != 0:
        print(f"  -> Failed: {query}")
        failed.append(query)

print(f"\nDone. {total - len(failed) - skipped} downloaded, {len(failed)} failed.")

if failed:
    log_path = os.path.join(folder_name, "failed.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(failed))
    print(f"Failed tracks saved to '{log_path}'")
