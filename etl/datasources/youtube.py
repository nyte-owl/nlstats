from datetime import datetime
import time

import pandas as pd
import requests

from config import settings
from log import get_logger


logger = get_logger(__name__)


def get_page_of_videos_from_upload_playlist(page_token: str = None):
    params = {
        "part": "id,snippet,contentDetails,status",
        "playlistId": settings.upload_playlist_id,
        "key": settings.youtube_api_key,
        "maxResults": 50,
    }
    if page_token:
        params.update({"pageToken": page_token})

    r = requests.get(
        url="https://youtube.googleapis.com/youtube/v3/playlistItems",
        params=params,
        headers={"Accept": "application/json"},
    )

    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code=} :: {r.text=}")

    playlist_data = r.json()

    if "nextPageToken" not in playlist_data:
        return None, None

    next_page_token = playlist_data["nextPageToken"]
    video_ids = [video["contentDetails"]["videoId"] for video in playlist_data["items"]]

    params = {
        "part": "snippet,contentDetails,statistics",
        "id": ",".join(video_ids),
        "key": settings.youtube_api_key,
    }

    r = requests.get(
        url="https://youtube.googleapis.com/youtube/v3/videos",
        params=params,
        headers={"Accept": "application/json"},
    )

    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code=} :: {r.text=}")

    data = r.json()

    logger.debug(f"Got {len(data['items'])} videos")

    return data["items"], next_page_token


def pull_uploads_from_youtube() -> pd.DataFrame:
    next_page = None

    all_videos = []
    while True:
        time.sleep(2)
        videos, next_page = get_page_of_videos_from_upload_playlist(next_page)
        if not videos:
            break

        all_videos.extend(videos)

        dt = datetime.strptime(
            videos[-1]["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
        )

        logger.debug(f"Oldest video from response from {dt}")

    return pd.DataFrame(all_videos)
