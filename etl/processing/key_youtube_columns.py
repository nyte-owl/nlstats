import re

import pandas as pd

from data import crud
from log import get_logger

logger = get_logger(__name__)


def clean_video_data(df_videos: pd.DataFrame):
    logger.debug(f"clean_video_data {df_videos.shape=}")
    # expand complex-object columns
    for column in ["statistics", "contentDetails", "snippet"]:
        df_videos = df_videos.join(
            pd.DataFrame(df_videos[column].to_dict()).T.add_prefix(f"{column}-")
        )
        df_videos = df_videos.drop(column, axis=1)

    df_videos = df_videos.drop(
        [
            "kind",
            "etag",
            "snippet-thumbnails",
            "snippet-channelTitle",
            "snippet-channelId",
            "snippet-liveBroadcastContent",
            "snippet-localized",
            "snippet-categoryId",
            "snippet-tags",
            "contentDetails-caption",
            "contentDetails-licensedContent",
            "contentDetails-projection",
            "contentDetails-dimension",
            "contentDetails-definition",
            "contentDetails-contentRating",
        ],
        axis=1,
    )

    def parse_title(title: str):
        matches = re.findall(r"[^|]+ \|([^#(]+)", title)
        if "Northernlion Live Super Show" in title:
            return None

        if matches:
            return matches[-1].strip()
        else:
            matches = re.findall(r"[^(]+\(([^#)]*?)\)", title)
            if matches:
                if "Episode" in matches[-1]:
                    if ":" in matches[-1] and "Episode" in matches[-1].split(":")[1]:
                        return matches[-1].split(":")[0].strip()
                    return title.split(" (")[0]
                return matches[-1].strip()

            return None

    df_videos["game"] = df_videos["snippet-title"].apply(parse_title)
    df_videos["snippet-publishedAt"] = pd.to_datetime(
        df_videos["snippet-publishedAt"], utc=True
    ).dt.tz_convert("US/Eastern")
    df_videos["statistics-viewCount"] = df_videos["statistics-viewCount"].astype(int)
    df_videos["statistics-likeCount"] = df_videos["statistics-likeCount"].astype(int)
    df_videos["statistics-commentCount"] = df_videos["statistics-commentCount"].astype(
        int
    )

    df_videos["likes-per-view"] = (
        (df_videos["statistics-likeCount"] / df_videos["statistics-viewCount"]) * 1000.0
    ).astype(int)
    df_videos["comments-per-view"] = (
        (df_videos["statistics-commentCount"] / df_videos["statistics-viewCount"])
        * 1000.0
    ).astype(int)

    df_videos["contentDetails-duration"] = df_videos["contentDetails-duration"].apply(
        lambda x: pd.Timedelta(x).seconds
    )

    df_videos.dropna(subset=["game"], inplace=True)

    df_videos.rename(
        {
            "snippet-title": "Title",
            "game": "Game",
            "snippet-publishedAt": "Publish Date",
            "statistics-viewCount": "Views",
            "statistics-likeCount": "Likes",
            "statistics-commentCount": "Comments",
            "snippet-description": "Description",
            "likes-per-view": "Likes per 1000 Views",
            "comments-per-view": "Comments per 1000 Views",
            "contentDetails-duration": "Duration (Seconds)",
        },
        axis=1,
        inplace=True,
    )

    return df_videos


def convert_games(df_videos: pd.DataFrame) -> pd.DataFrame:
    logger.debug(f"convert_games {df_videos=}")
    df_videos = df_videos[~df_videos["Title"].str.contains("#ad", case=False)]

    conversion_rules = crud.conversion_rule.read_all_conversion_rules()

    for conversion_rule in conversion_rules:
        mask = df_videos["Game"] == conversion_rule.parsed_title
        if mask.any():
            logger.info(
                f"Changing {mask.value_counts()[True]} videos "
                f"`{conversion_rule.parsed_title}` to "
                f"`{conversion_rule.final_title}`"
            )
            df_videos.loc[mask, "Game"] = conversion_rule.final_title
        else:
            logger.warning(
                f"Couldn't change any videos with name "
                f"{conversion_rule.parsed_title}"
            )

    return df_videos
