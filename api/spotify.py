import os
import json
import random
import requests

from base64 import b64encode
from dotenv import load_dotenv, find_dotenv
from flask import Flask, Response, jsonify, render_template

load_dotenv(find_dotenv())

# Spotify scopes:
#   user-read-currently-playing
#   user-read-recently-played
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_ID")
SPOTIFY_SECRET_ID = os.getenv("SPOTIFY_SECRET")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH")

REFRESH_TOKEN_URL = "https://accounts.spotify.com/api/token"
NOW_PLAYING_URL = "https://api.spotify.com/v1/me/player/currently-playing"
RECENTLY_PLAYING_URL = (
    "https://api.spotify.com/v1/me/player/recently-played?limit=10"
)

# Twitter
# POST account/update_profile


app = Flask(__name__)


def getAuth():
    return b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET_ID}".encode()).decode(
        "ascii"
    )


def refreshToken():
    data = {
        "grant_type": "refresh_token",
        "refresh_token": SPOTIFY_REFRESH_TOKEN,
    }

    headers = {"Authorization": "Basic {}".format(getAuth())}
    response = requests.post(REFRESH_TOKEN_URL, data=data, headers=headers)

    try:
        return response.json()["access_token"]
    except KeyError:
        print(json.dumps(response.json()))
        print("\n---\n")
        raise KeyError(str(response.json()))


def recentlyPlayed():
    token = refreshToken()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(RECENTLY_PLAYING_URL, headers=headers)

    if response.status_code == 204:
        return {}
    return response.json()


def nowPlaying():
    token = refreshToken()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(NOW_PLAYING_URL, headers=headers)

    if response.status_code == 204:
        return {}
    return response.json()



@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    data = nowPlaying()
    np_title = data["item"]["name"]
    np_artist = data["item"]["artists"][0]["name"]
    now_playing = '#np 🎵 ' + np_title + ' - ' + np_artist
    return now_playing


if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)