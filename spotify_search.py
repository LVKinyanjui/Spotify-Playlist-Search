# spotify_search.py
import requests
from spotify_auth import SpotifyAuth

def get_user_id_from_display_name(display_name, max_pages=20):
    """
    Search for a user by display name and return their user ID.
    Note: Since Spotify API doesn't support direct user search, we need to get creative
    with searching for content associated with the user.
    
    Args:
        display_name (str): The display name to search for
        max_pages (int): Maximum number of pages to search through (default: 20)
    
    Returns:
        tuple: (user_id, error_message)
    """
    auth = SpotifyAuth()
    base_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {auth.get_token()}",
        "Content-Type": "application/json"
    }
    
    # Search for playlists since we can't search users directly
    params = {
        "q": f"user:{display_name}",  # Try to find content by this user
        "type": "playlist",  # We can only search for content types
        "limit": 50,
        "offset": 0
    }
    
    pages_searched = 0
    
    while pages_searched < max_pages:
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            playlists = data.get('playlists', {}).get('items', [])
            
            # Look through playlist owners for a match
            for playlist in playlists:
                if playlist is not None:
                    owner = playlist.get('owner', {})
                    if owner.get('display_name', '').lower() == display_name.lower():
                        return owner['id'], None
            
            # Check if there are more results
            if not data['playlists'].get('next'):
                return None, "Could not find user with that display name"
                
            # Update offset for next page
            params['offset'] += 50
            pages_searched += 1
            
        except requests.exceptions.HTTPError as e:
            return None, f"API request failed: {str(e)}"
        except requests.exceptions.RequestException as e:
            return None, f"API request failed: {str(e)}"
            
    return None, f"Searched through {max_pages} pages without finding an exact match"

def search_playlists(query, owner_id):
    """
    Search for playlists on Spotify and find one by a specific owner.
    
    Args:
        query (str): Search query for playlists
        owner_id (str): Spotify user ID of the playlist owner to find
        
    Returns:
        tuple: (playlist_object, error_message)
    """
    auth = SpotifyAuth()
    base_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {auth.get_token()}",
        "Content-Type": "application/json"
    }
    
    params = {
        "q": query,
        "type": "playlist",
        "limit": 50,
        "offset": 0
    }
    
    while True:
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
                
            data = response.json()
            playlists = data['playlists']['items']
            
            # Search for playlist by the specified owner
            for playlist in playlists:
                if playlist['owner']['id'] == owner_id:
                    return playlist, None
            
            # Check if there are more results
            if not data['playlists']['next']:
                return None, "No matching playlist found"
                
            # Update offset for next page
            params['offset'] += 50
            
        except requests.exceptions.HTTPError as e:
            return None, f"API request failed: {str(e)}"
        except requests.exceptions.RequestException as e:
            return None, f"API request failed: {str(e)}"