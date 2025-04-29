import os
import pandas as pd

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables from .env file
load_dotenv()

# Initialize Spotipy with client credentials
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id= os.getenv("CLIENT_ID"),
        client_secret= os.getenv("CLIENT_SECRET")
        )
    )

def get_genres(artist, enable_search=False):
    '''
    Get the genres of an artist, default is to use the artist ID.
    If enable_search is True, it will search for the artist by name.

    Parameters:
        artist (str): The ID or search query of the artist (e.g., artist name).
        enable_search (bool): Default is False.

    Returns:
        list: A list of genres associated with the artist.
    '''
    if enable_search:
        # Search for the artist by name
        results = sp.search(q='artist:' + artist, type='artist', limit=1)
        # Get the artist details
        artist = results['artists']['items'][0]
        # Extract the artist genres
        return artist['genres']
    
    else:
        # Get the artist information
        artist_info = sp.artist(artist)
        # Extract the genres
        return artist_info['genres']

def get_playlist_tracks(playlist_id):
    '''
    Get all tracks from a Spotify playlist and their associated genres.

    Parameters:
    playlist_id (str): The Spotify ID of the playlist.

    Returns:
    pd.DataFrame: A DataFrame containing track names, artist names, artist IDs, and genres.
    '''

    # Initialize variables for pagination
    offset = 0
    track_list = []

    while True:
        # Get a batch of tracks from the playlist
        response = sp.playlist_tracks(playlist_id, offset=offset, limit=100)
        tracks = response['items']

        if not tracks:
            break
        
        No_Genre_Name = 'None'
        # Extract track details and append to the list
        for item in tracks:
            track = item['track']
            track_name = track['name']
            artist_names = ', '.join([artist['name'] for artist in track['artists']])
            artist_ids = [artist['id'] for artist in track['artists']]
            unique_genres = set(sum([get_genres(artist_id) for artist_id in artist_ids], []))
            genres = ', '.join(unique_genres) if unique_genres else No_Genre_Name # if the song has "no genre", then None
            track_list.append([track_name, artist_names, ', '.join(artist_ids), genres])

        # Update the offset for the next batch
        offset += len(tracks)

    # Create a DataFrame from the track list
    df = pd.DataFrame(track_list, columns=['Track Name', 'Artist Name', 'Artist ID', 'Genre'])

    return df