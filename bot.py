import json
import os
import random
import time
from mastodon import Mastodon

# Configuration
MASTODON_API_BASE = "https://icosahedron.website"  # Change this to your instance
ACCESS_TOKEN = "token.secret"
META_FILE = "meta.json"
IMAGE_FOLDER = "images"
MUSIC_FOLDER = "music"
POST_INTERVAL = 2 * 60 * 60  # 2 hours in seconds
MUSIC_POST_INTERVAL = 24 * 60 * 60  # 24 hours in seconds

# Authenticate with Mastodon
mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=MASTODON_API_BASE,
)

def load_metadata():
    """Loads image metadata from meta.json."""
    with open(META_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def choose_random_image(meta):
    """Selects a random image from the metadata list."""
    return random.choice(meta)

def choose_random_song():
    """Selects a random song from the music folder."""
    albums = [d for d in os.listdir(MUSIC_FOLDER) if os.path.isdir(os.path.join(MUSIC_FOLDER, d))]
    if not albums:
        return None
    album = random.choice(albums)
    album_path = os.path.join(MUSIC_FOLDER, album)
    tracks = [f for f in os.listdir(album_path) if f.endswith(".flac")]
    if not tracks:
        return None
    track = random.choice(tracks)
    track_path = os.path.join(album_path, track)
    cover_path = os.path.join(album_path, "cover.jpg")
    track_nb, track_name = track.split(" - ", 1)
    track_name = track_name.replace(".flac", "")
    description = f"{album}, track {track_nb} - {track_name}"
    return track_path, cover_path, description

def post_image():
    """Uploads and posts a random image with alt text."""
    meta = load_metadata()
    selected = choose_random_image(meta)
    image_path = os.path.join(IMAGE_FOLDER, selected["folder"], selected["filename"])
    alt_text = selected["full_description"]
    
    if not os.path.exists(image_path):
        print(f"Error: Image {image_path} not found!")
        return
    
    # Upload image
    media = mastodon.media_post(image_path, description=alt_text, synchronous=True)
    
    # Post toot
    mastodon.status_post(" ", media_ids=[media["id"]], visibility="unlisted")

def post_song():
    """Uploads and posts a random song with album cover."""
    song_data = choose_random_song()
    if not song_data:
        print("Error: No songs found!")
        return
    track_path, cover_path, description = song_data
    
    if not os.path.exists(track_path) or not os.path.exists(cover_path):
        print("Error: Track or cover not found!")
        return
    
    media = mastodon.media_post(track_path, description=description, thumbnail=cover_path, synchronous=True)
    
    # Post toot
    mastodon.status_post(f" ", media_ids=[media["id"]], visibility="unlisted")

if __name__ == "__main__":
    last_song_post_time = 0
    while True:
        post_image()
        current_time = time.time()
        if current_time - last_song_post_time >= MUSIC_POST_INTERVAL:
            post_song()
            last_song_post_time = current_time
        time.sleep(POST_INTERVAL)
