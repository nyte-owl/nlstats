from datetime import timedelta
from typing import List

import pandas as pd
import numpy as np

from data import crud


def convert_seconds(seconds):
    return str(timedelta(seconds=seconds))


df_videos = crud.processed_stat.get_most_recent_processed_stat_dataframe()
df_videos["Duration"] = df_videos["Duration (Seconds)"].apply(convert_seconds)
print(df_videos.columns)
all_games = df_videos.groupby("Game")["Title"].count().sort_values(ascending=False)
most_uploaded = df_videos["Game"].value_counts().index.tolist()[:4]

df_views_over_time = (
    df_videos.set_index("Publish Date").resample("W").sum()[["Views"]].reset_index()
)


df_per_game_stats = (
    df_videos[["Likes", "Views", "Game"]].groupby("Game").agg(["sum", "count"])
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
print(df_per_game_stats)

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
    df=df_videos,
    rank_by_col="Views",
    columns_shown=["Title", "Publish Date", "Views"],
    str_conv_col="Views",
)

df_longest_videos = obtain_ranked_df(
    df=df_videos,
    rank_by_col="Duration (Seconds)",
    columns_shown=["Title", "Publish Date", "Views", "Duration"],
    str_conv_col="Views",
)

df_video_highest_like_rate = obtain_ranked_df(
    df=df_videos,
    rank_by_col="Likes per 1000 Views",
    columns_shown=["Title", "Publish Date", "Likes per 1000 Views", "Views"],
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
    df_videos.groupby([monthly])["Game"]
    .value_counts()
    .rename("Game Count")
    .to_frame()
    .groupby(level=0)
    .head(1)
    .reset_index()
    .set_index("Publish Date")
)
total_videos_monthly = (
    df_videos.groupby([monthly])["Game"].count().rename("Total Videos").to_frame()
)
df_top_monthly = df_top_monthly.join(total_videos_monthly).reset_index()

df_top_monthly["Game"] = df_top_monthly["Game"].apply(
    lambda x: x if not isinstance(x, np.ndarray) else ", ".join(x)
)
df_top_monthly["Publish Date"] = df_top_monthly["Publish Date"].apply(
    lambda x: x.strftime("%Y %B")
)

df_top_monthly = df_top_monthly.rename({"Publish Date": "Month"}, axis=1)
