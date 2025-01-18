# app.py
import os
import streamlit as st
from spotify_search import search_playlists, get_user_id_from_display_name
from spotify_auth import SpotifyAuth

def check_credentials():
    """Check if Spotify credentials are properly set."""
    missing = []
    if not os.getenv('SPOTIFY_CLIENT_ID'):
        missing.append('SPOTIFY_CLIENT_ID')
    if not os.getenv('SPOTIFY_CLIENT_SECRET'):
        missing.append('SPOTIFY_CLIENT_SECRET')
    
    return missing

def main():
    st.set_page_config(page_title="Spotify Playlist Finder", page_icon="🎵")
    
    # Add custom CSS for better styling
    st.markdown("""
        <style>
        .stApp {
            max-width: 800px;
            margin: 0 auto;
        }
        .success-message {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #d1fae5;
            color: #065f46;
        }
        .error-message {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #fee2e2;
            color: #991b1b;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🎵 Spotify Playlist Finder")
    st.markdown("---")
    
    # Check for environment variables
    missing_credentials = check_credentials()
    if missing_credentials:
        st.error(f"Missing environment variables: {', '.join(missing_credentials)}")
        st.info("Please set these variables in your environment or .env file")
        return
    
    # Initialize auth (will validate credentials)
    try:
        SpotifyAuth()
    except Exception as e:
        st.error(f"Authentication setup failed: {str(e)}")
        return
    
    # Input fields
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            playlist_name = st.text_input("Playlist Name", placeholder="Enter playlist name...")
        with col2:
            owner_name = st.text_input("Owner Display Name", placeholder="Enter owner's display name...")
        
        submitted = st.form_submit_button("Search Playlist")
    
    if submitted:
        if not all([playlist_name, owner_name]):
            st.error("Please fill in all fields.")
            return
        
        with st.spinner("Searching for user..."):
            # First, get the user ID from the display name
            owner_id, user_error = get_user_id_from_display_name(owner_name)
            
            if user_error:
                st.error(user_error)
                return
            
            st.info(f"Found user! Now searching for their playlist...")
            
            # Search for the playlist
            playlist, playlist_error = search_playlists(playlist_name, owner_id)
            
            if playlist_error:
                st.error(playlist_error)
                return
            
            # Display playlist information in a nice format
            st.markdown("### Found Playlist! 🎉")
            col1, col2 = st.columns(2)
            
            with col1:
                if playlist.get('images'):
                    st.image(playlist['images'][0]['url'], width=200)
            
            with col2:
                st.markdown(f"**Name:** {playlist['name']}")
                st.markdown(f"**Owner:** {playlist['owner']['display_name']}")
                st.markdown(f"**Tracks:** {playlist['tracks']['total']}")
                if playlist.get('description'):
                    st.markdown(f"**Description:** {playlist['description']}")
            
            # Add a button to open in Spotify
            st.markdown(f"[Open in Spotify]({playlist['external_urls']['spotify']})")

if __name__ == "__main__":
    main()