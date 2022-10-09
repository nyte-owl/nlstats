import json

import pandas as pd
from data import crud
from log import get_logger

logger = get_logger(__name__)


def write_latest_raw_youtube(
    df: pd.DataFrame, collection_event_id: int
) -> pd.DataFrame:
    logger.info(f"write_latest_raw_youtube {df.shape=}")
    new_data = []
    all_video_ids = crud.video.get_all_video_ids()

    for idx, row in df.iterrows():
        logger.debug(f"Write latest raw YT: {idx}")
        unique_youtube_id = row["id"]
        if unique_youtube_id not in all_video_ids:
            crud.video.create_video(unique_youtube_id)

        new_data.append(
            crud.raw_data.CreateRawData(
                video_id=unique_youtube_id,
                collection_event_id=collection_event_id,
                kind=json.dumps(row["kind"]),
                etag=json.dumps(row["etag"]),
                snippet=json.dumps(row["snippet"]),
                content_details=json.dumps(row["contentDetails"]),
                statistics=json.dumps(row["statistics"]),
            )
        )

    crud.raw_data.create_raw_video_data(new_data)
    return df


def write_latest_processed_youtube(
    df: pd.DataFrame, collection_event_id: int
) -> pd.DataFrame:
    logger.info(f"write_latest_processed_youtube {df.shape=}")

    video_updates = []
    new_stats = []
    for idx, row in df.iterrows():
        logger.debug(f"Write latest processed YT: {idx}")
        video_updates.append(
            crud.video.UpdateVideo(
                video_id=row["id"],
                title=row["Title"],
                description=row["Description"],
                game=row["Game"],
                duration_seconds=row["Duration (Seconds)"],
                publish_date=row["Publish Date"],
            )
        )

        new_stats.append(
            crud.processed_stat.CreateProcessedStat(
                video_id=row["id"],
                collection_event_id=collection_event_id,
                views=row["Views"],
                likes=row["Likes"],
                comments=row["Comments"],
                ratio_likes_views=row["Likes per 1000 Views"],
                ratio_comments_views=row["Comments per 1000 Views"],
            )
        )

    crud.video.update_video_data(video_updates)
    crud.processed_stat.create_processed_stats(new_stats)
    return df
