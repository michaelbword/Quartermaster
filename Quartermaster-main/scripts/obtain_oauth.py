import os

import requests
from dotenv import load_dotenv

# Load environment variables from the file
load_dotenv('../config/environment.env')  # Adjust the filename if needed
def get_oauth_token(client_id, client_secret):
    """
    Get OAuth token from Twitch using client ID and client secret.
    """
    grant_type = "client_credentials"
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": grant_type
    }

    # Use the data parameter instead of params for a POST request
    response = requests.post(url, data=params)

    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        return access_token
    else:
        raise ValueError(f"Failed to obtain OAuth token: {response.json()}")


# Example usage
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
token = get_oauth_token(client_id, client_secret)
print("Access Token:", token)