# spotify_auth.py
import os
import time
import requests
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class SpotifyToken:
    access_token: str
    expires_at: datetime

class SpotifyAuth:
    _instance = None
    _token: SpotifyToken = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpotifyAuth, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in environment variables"
            )

    def _get_basic_auth_header(self) -> str:
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = str(b64encode(auth_bytes), 'utf-8')
        return f"Basic {auth_base64}"

    def _request_new_token(self) -> SpotifyToken:
        """Request a new access token from Spotify."""
        headers = {
            'Authorization': self._get_basic_auth_header(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers=headers,
            data=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get access token: {response.text}")
        
        token_data = response.json()
        expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'] - 60)  # Buffer of 60 seconds
        
        return SpotifyToken(
            access_token=token_data['access_token'],
            expires_at=expires_at
        )

    def get_token(self) -> str:
        """Get a valid access token, requesting a new one if necessary."""
        if self._token is None or datetime.now() >= self._token.expires_at:
            self._token = self._request_new_token()
        
        return self._token.access_token