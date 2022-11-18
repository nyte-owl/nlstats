from datetime import timedelta
import math
from typing import List

import pandas as pd
import numpy as np

from data import crud
from log import get_logger
from config import settings

logger = get_logger(__name__)


def convert_seconds(seconds):
    return str(timedelta(seconds=seconds))


earliest_pull_date = crud.collection_event.get_earliest_event()

# -- All Video Stats --
logger.info("Creating 'All Video' stats")
df_all_video_stats = crud.processed_stat.get_all_stats()
df_all_video_stats["Likes per 1000 Views"] = df_all_video_stats["Likes"] / (
    df_all_video_stats["Views"] / 1000
)
df_all_video_stats["Comments per 1000 Views"] = df_all_video_stats["Comments"] / (
    df_all_video_stats["Views"] / 1000
)
df_all_video_stats["Publish Date"] = df_all_video_stats["Publish Date"].dt.tz_localize(
    "US/Eastern", nonexistent="shift_forward"
)
df_all_video_stats = df_all_video_stats[
    df_all_video_stats["Publish Date"] >= settings.start_date
]
df_all_video_stats["Time Elapsed"] = (
    df_all_video_stats["Pull Date"] - df_all_video_stats["Publish Date"]
)
df_all_video_stats["Days Elapsed"] = (
    df_all_video_stats["Time Elapsed"]
    .apply(lambda et: et.total_seconds() / 86400)
    .round(decimals=1)
)
df_all_video_stats = df_all_video_stats.sort_values(by="Pull Date")
df_all_video_stats = df_all_video_stats[
    df_all_video_stats["Publish Date"] >= earliest_pull_date
]
num_bins = math.ceil(df_all_video_stats["Days Elapsed"].max())
df_all_video_stats["Bin"] = pd.cut(df_all_video_stats["Days Elapsed"], bins=num_bins)


# -- Latest Video Stats --
logger.info("Creating 'Latest Video' stats")
df_latest_video_stats = crud.processed_stat.get_most_recent_processed_stat_dataframe()
df_latest_video_stats["Likes per 1000 Views"] = (
    df_latest_video_stats["Likes"] / (df_latest_video_stats["Views"] / 1000)
).round(3)
df_latest_video_stats["Comments per 1000 Views"] = (
    df_latest_video_stats["Comments"] / (df_latest_video_stats["Views"] / 1000)
).round(3)

df_latest_video_stats["Publish Date"] = df_latest_video_stats[
    "Publish Date"
].dt.tz_localize("US/Eastern", nonexistent="shift_forward")
df_latest_video_stats = df_latest_video_stats[
    df_latest_video_stats["Publish Date"] >= settings.start_date
]

df_latest_video_stats["Duration"] = df_latest_video_stats["Duration (Seconds)"].apply(
    convert_seconds
)
all_games = (
    df_latest_video_stats.groupby("Game")["Title"].count().sort_values(ascending=False)
)
most_uploaded = df_latest_video_stats["Game"].value_counts().index.tolist()[:4]

df_per_game_stats = (
    df_latest_video_stats[["Likes", "Views", "Game"]]
    .groupby("Game")
    .agg(["sum", "count"])
)
df_per_game_stats.columns = df_per_game_stats.columns.map("_".join)

df_per_game_stats = (
    df_per_game_stats.drop(["Likes_count"], axis=1)
    .reset_index()
    .rename(
        {"Likes_sum": "Likes", "Views_sum": "Views", "Views_count": "Video Count"},
        axis=1,
    )
)
df_per_game_stats["Likes per 1000 Views"] = df_per_game_stats["Likes"] / (
    df_per_game_stats["Views"] / 1000
)

df_per_game_stats["Average Views Per Video"] = (
    df_per_game_stats["Views"] / df_per_game_stats["Video Count"]
).astype(int)

df_per_game_stats["Average Like Rate Per Video"] = (
    df_per_game_stats["Likes per 1000 Views"] / df_per_game_stats["Video Count"]
)


def obtain_ranked_df(
    df: pd.DataFrame,
    rank_by_col: str,
    columns_shown: List[str],
    filter_function=None,
    str_conv_col: str | None = None,
    float_conversion: bool = False,
):
    df = df.copy()
    if filter_function:
        df = filter_function(df)

    ranking_col_name = "Ranking"

    df[ranking_col_name] = (
        df[rank_by_col].rank(ascending=False, method="min").astype(int)
    )
    df = df.sort_values(by="Ranking", ascending=True)[
        [ranking_col_name] + columns_shown
    ]

    if str_conv_col:
        if float_conversion:
            df[str_conv_col] = df[str_conv_col].map("{:.02f}".format)
        else:
            df[str_conv_col] = df[str_conv_col].map("{:,d}".format)

    return df


df_biggest_view_getters = obtain_ranked_df(
    df=df_per_game_stats,
    rank_by_col="Average Views Per Video",
    columns_shown=["Game", "Average Views Per Video", "Video Count"],
    filter_function=lambda df: df[df["Video Count"] > 4],
    str_conv_col="Average Views Per Video",
)

df_most_viewed_games = obtain_ranked_df(
    df=df_per_game_stats,
    rank_by_col="Views",
    columns_shown=["Game", "Views", "Video Count"],
    str_conv_col="Views",
)

df_most_published_games = obtain_ranked_df(
    df=df_per_game_stats,
    rank_by_col="Video Count",
    columns_shown=["Game", "Video Count"],
)

df_most_viewed_videos = obtain_ranked_df(
    df=df_latest_video_stats,
    rank_by_col="Views",
    columns_shown=["id", "Title", "Publish Date", "Views"],
    str_conv_col="Views",
)

df_longest_videos = obtain_ranked_df(
    df=df_latest_video_stats,
    rank_by_col="Duration (Seconds)",
    columns_shown=["id", "Title", "Publish Date", "Views", "Duration"],
    str_conv_col="Views",
)

df_video_highest_like_rate = obtain_ranked_df(
    df=df_latest_video_stats,
    rank_by_col="Likes per 1000 Views",
    columns_shown=["id", "Title", "Publish Date", "Likes per 1000 Views", "Views"],
)

df_game_highest_like_rate = obtain_ranked_df(
    df=df_per_game_stats,
    rank_by_col="Likes per 1000 Views",
    columns_shown=["Game", "Likes per 1000 Views", "Video Count"],
    filter_function=lambda df: df[df["Video Count"] > 4],
    str_conv_col="Likes per 1000 Views",
    float_conversion=True,
)

df_biggest_like_getters = obtain_ranked_df(
    df=df_per_game_stats,
    rank_by_col="Average Like Rate Per Video",
    columns_shown=["Game", "Average Like Rate Per Video", "Video Count"],
    filter_function=lambda df: df[df["Video Count"] > 4],
    str_conv_col="Average Like Rate Per Video",
    float_conversion=True,
)

monthly = pd.Grouper(key="Publish Date", freq="M")
df_top_monthly = (
    df_latest_video_stats.groupby([monthly])["Game"]
    .value_counts()
    .rename("Game Count")
    .to_frame()
    .groupby(level=0)
    .head(1)
    .reset_index()
    .set_index("Publish Date")
    .sort_index(ascending=False)
)
total_videos_monthly = (
    df_latest_video_stats.groupby([monthly])["Game"]
    .count()
    .rename("Total Videos")
    .to_frame()
)
df_top_monthly = df_top_monthly.join(total_videos_monthly).reset_index()

df_top_monthly["Game"] = df_top_monthly["Game"].apply(
    lambda x: x if not isinstance(x, np.ndarray) else ", ".join(x)
)
df_top_monthly["Publish Date"] = df_top_monthly["Publish Date"].apply(
    lambda x: x.strftime("%Y %B")
)

df_top_monthly = df_top_monthly.rename({"Publish Date": "Month"}, axis=1)

logger.info("Done")
