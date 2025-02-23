import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from recognize import speak_text
import time

# Load environment variables
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URL")
device_id = os.getenv("DEVICE_ID")

# Validate environment variables
if not all([client_id, client_secret, redirect_uri, device_id]):
    print("Error: One or more environment variables are missing.")
    raise ValueError("Environment variables for Spotify API configuration are not set properly.")

# Initialize Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope='user-read-playback-state user-modify-playback-state playlist-read-private'
))

def play_song(track_name, retries = 3):
    """
    Play a song by name on the specified Spotify device.

    Args:
        track_name (str): The name of the track to play.

    """
    try:
        # Search for the track
        results = sp.search(q=track_name, type='track', limit=1)
        tracks = results['tracks']['items']

        if not tracks:
            print("No tracks found for the search term.")
            return

        # Play track
        track = tracks[0]
        track_uri = track['uri']

        # Ensure device_id is valid
        devices = sp.devices()
        device_ids = [device['id'] for device in devices['devices']]
        if device_id not in device_ids:
            print(f"Device ID {device_id} is not available.")
            return

        # Start playback on the chosen device
        sp.start_playback(device_id=device_id, uris=[track_uri])
        print(f"Playing track: {track_uri}")

    except Exception as e:
        print(f"An error occurred while playing the song: {e}")
        #recall the function if error
        if retries > 0:
            print(f"Retrying... ({retries} retries left)")
            play_song(track_name, retries - 1)

def play_playlist(playlist_name, retries = 3):
    """
    Play a playlist by name on the specified Spotify device.

    Args:
        playlist_name (str): The name of the playlist to play.

    """
    try:
        # Search for the playlist
        results = sp.search(q=f'playlist:{playlist_name}', type='playlist', limit=1)
        playlists = results['playlists']['items']

        if not playlists:
            print("No playlists found for the search term.")
            return

        # Get the first result
        playlist = playlists[0]
        playlist_uri = playlist['uri']

        # Ensure device_id is valid
        devices = sp.devices()
        device_ids = [device['id'] for device in devices['devices']]
        if device_id not in device_ids:
            print(f"Device ID {device_id} is not available.")
            return

        # Start playback on the chosen device
        sp.start_playback(device_id=device_id, context_uri=playlist_uri)
        print(f"Playing playlist: {playlist_uri}")

    except Exception as e:
        print(f"An error occurred while playing the playlist: {e}")
        #recall the function if error
        if retries > 0:
            print(f"Retrying... ({retries} retries left)")
            play_playlist(playlist_name, retries - 1)

def play_music(music):
    """Play specified music on Spotify."""
    try:
        os.system('spotify')
        
        music = music.lower()
        if " on spotify" in music:
            music, _ = music.split("on spotify", 1)
            music = music.strip()
        if "play " in music:
            _, music = music.split("play", 1)
            music = music.strip()
        response = "Playing " + music + " on Spotify"
        speak_text(response)
        time.sleep(1.5)
        if "playlist" in music:
            music = music.replace("playlist", "").strip()
            play_playlist(music)
        else:
            play_song(music)
        return(response)
    except Exception as e:
        print(f"Error playing music: {e}")
        return

if(__name__ == "__main__"):
    play_music("Friday play Mr. Brightside")