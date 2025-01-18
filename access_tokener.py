import requests
import os

client_id = os.environ["SPOTIFY_CLIENT_ID"]
client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]


def get_access_token(client_id: str, client_secret: str) -> str | None:
    
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    # Make the POST request
    response = requests.post(url, headers=headers, data=data)
    
    # Check the response status and print the output
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print("Access token:", access_token)
        return access_token
    else:
        print(f"Error: {response.status_code}", response.text)
        return None


if __name__ == '__main__':
    get_access_token(client_id, client_secret)