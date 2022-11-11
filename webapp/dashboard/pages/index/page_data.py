import pandas as pd
from pandas.tseries.offsets import DateOffset
from datetime import date, datetime

from ... import data

DAILY_PERFORMANCE_DAYS_MAX = 6
SERIES_MIN_VIDEO_COUNT = 2
SMALL_SERIES_MAX_VIDEO_COUNT = 30

daily_performance_stats = (
    data.df_all_video_stats.groupby("Bin")["Time Elapsed"].mean().to_frame()
)
daily_performance_stats["Days Elapsed"] = (
    daily_performance_stats["Time Elapsed"]
    .apply(lambda et: et.total_seconds() / 86400)
    .round(decimals=1)
)
daily_performance_stats = daily_performance_stats.join(
    data.df_all_video_stats.groupby("Bin")["Views"].describe()
).set_index("Days Elapsed")
daily_performance_stats = daily_performance_stats.loc[
    daily_performance_stats.index <= DAILY_PERFORMANCE_DAYS_MAX
]

daily_middle_50_x = (
    daily_performance_stats.index.tolist()
    + daily_performance_stats.index.tolist()[::-1]
)
daily_middle_50_y = (
    daily_performance_stats["75%"].tolist()
    + daily_performance_stats["25%"].tolist()[::-1]
)


df_new_videos_stats: pd.DataFrame = data.df_all_video_stats[
    (
        pd.Timestamp(datetime.today(), tz="UTC")
        - data.df_all_video_stats["Publish Date"]
        <= pd.Timedelta(DAILY_PERFORMANCE_DAYS_MAX, "days")
    )
    & (
        pd.Timestamp(datetime.today(), tz="UTC")
        - data.df_all_video_stats["Publish Date"]
        >= pd.Timedelta(2, "days")
    )
]

df_views_over_time = (
    data.df_latest_video_stats.set_index("Publish Date")[["Views"]]
    .resample("W")
    .sum()
    .reset_index()
)

df_latest_video_stats = data.df_latest_video_stats.copy().sort_values(by="Publish Date")

# Get list of game series that are "small"; not many videos
counts = df_latest_video_stats["Game"].value_counts().rename("Count").to_frame()
small_game_series = counts[
    (counts["Count"] >= SERIES_MIN_VIDEO_COUNT)
    & (counts["Count"] <= SMALL_SERIES_MAX_VIDEO_COUNT)
].index.tolist()


# Get list of game series that are RECENT
today = pd.Timestamp(date.today())
most_recent_pub_date_per_video = (
    df_latest_video_stats.groupby("Game")["Publish Date"].max().to_frame()
)
recent_video_series = most_recent_pub_date_per_video[
    most_recent_pub_date_per_video["Publish Date"] >= today - DateOffset(weeks=3)
].index.tolist()


game_series = counts[counts["Count"] >= 2].index.tolist()
df_latest_video_stats["Cumulative Views"] = (
    df_latest_video_stats[df_latest_video_stats["Game"].isin(game_series)]
    .groupby(["Game"])["Views"]
    .cumsum()
    .fillna(0)
    .astype(int)
)

# Create publish rank order for each game series
df_game_series_video_stats = df_latest_video_stats[
    df_latest_video_stats["Game"].isin(game_series)
]
df_game_series_video_stats = pd.concat(
    [
        df[
            [
                "Cumulative Views",
                "Views",
                "Likes",
                "Likes per 1000 Views",
                "Comments",
                "Comments per 1000 Views",
                "Publish Date",
                "Game",
                "Title",
            ]
        ]
        .reset_index(drop=True)
        .reset_index()
        for _, df in df_game_series_video_stats.groupby("Game", as_index=False)
    ]
)

df_game_series_video_stats["Video #"] = df_game_series_video_stats["index"] + 1

df_small_game_series_video_stats = df_game_series_video_stats[
    df_game_series_video_stats["Game"].isin(small_game_series)
    & df_game_series_video_stats["Game"].isin(recent_video_series)
]

series_cumulative_views_stats = (
    df_game_series_video_stats.groupby("Video #")["Cumulative Views"]
    .describe()
    .loc[:SMALL_SERIES_MAX_VIDEO_COUNT]
)

middle_50_x = (
    series_cumulative_views_stats.index.tolist()
    + series_cumulative_views_stats.index.tolist()[::-1]
)
middle_50_y = (
    series_cumulative_views_stats["75%"].tolist()
    + series_cumulative_views_stats["25%"].tolist()[::-1]
)
