import requests
import os
from loguru import logger

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def authorization():
    try:
        url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
        x = requests.post(url)
        return x.json()["access_token"]
    except KeyError as e:
        logger.error(
            "Failed to get access token. Check your CLIENT_ID and CLIENT_SECRET."
        )
        raise e
