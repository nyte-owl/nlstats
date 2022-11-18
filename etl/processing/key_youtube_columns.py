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
        if (
            "Northernlion Live Super Show" in title
            or "Northernlion Live Pseudo Show" in title
        ):
            return "NLSS"

        simple_regex_attempts = [
            r"([^-]+) - Season",
            # Hearthstone Arena Northernlion's Den! [Episode 28]
            r"(Hearthstone)",
            # e.g. Northernlion and Friends Play: Spelunky [Episode 3]
            r"^Northernlion [Aa]nd Friends Play: ([^|(\[-]+)",
            # e.g. Don't Play - All Outta Bubblegum
            r"^Don't Play.*?- ([^|(\[-]+)",
            # e.g. Let's Hate - The Great Waldo Search [NES]
            r"^Let's Hate.*?- ([^|(\[-]+)",
            # e.g. The Binding of Isaac: Rebirth - Let's Play - Episode 1 [Reborn]
            r"([^|(\[-]+) - Let's Play -",
            # e.g. Northernlion Tries: EXAPUNKS! [Twitch VOD]
            r"Northernlion Tries: ([^|(\[-]+)",
            # e.g. Let's Play: XCOM: Enemy Within! [Episode 19]
            r"^Let's Play: ([^|(\[-]+)",
            # e.g. Let's Play - Mega Man: Dr. Wily's Revenge (1)
            # e.g. Let's Play (Bonus) - Super Meat Boy - Unlockable Meat Boys
            r"^Let's Play.*?- ([^|(\[-]+)",
            # e.g. Let's Look At: War of the Roses! [PC]
            r"^Let's Look [Aa]t.*?: ([^|(\[-]+)",
            # e.g. Let's Look At - Revenge of the Titans
            r"^Let's Look [Aa]t.*?- ([^|(\[-]+)",
            # e.g. `Northernlion Plays: Pokemon Let's Go Pikachu [...`
            r"Northernlion Plays: ([^\[\(|]+)",
            # e.g. `The Binding of Isaac: AFTERBIRTH+ - Northernlion Plays - Episode...
            # (Motto)`
            r"([^-]+) - Northernlion Plays",
            # e.g. `Northernlion Plays - D4: Dark Dreams Don't Die [Episode 6]...
            r"Northernlion Plays - ([^\[\(|]+)",
            # e.g. `An Alternative XCOM | Gears Tactics (Northernlion Tries)`
            r"[^|]+ \|([^#(]+)",
            r"Play: ([^|(\[-]+)",
            r"(Afterbirth\+)",
            r"(Super Mega Baseball 2)",
            r"(Planet Coaster)",
            r"(Factorio)",
            r"(Overwatch)",
            r"(Rocket League)",
            r"(Europa Universalis IV)",
            r"(Europa Universalis 4)",
            r"(PUBG)",
            r"(NHL 18)",
            r"(Fortnite)",
            r"(The Escapists 2)",
            r"(Divinity: Original Sin 2)",
            r"(PlayerUnknown's Battlegrounds)",
            r"Team Unity (Minecraft)",
            r"Team Unity Tuesday: (Minecraft)",
            r"(Oxygen Not Included)",
            r"(Ultimate Chicken Horse)",
            r"(Escape from Tarkov)",
            r"(Streets of Rogue): ",
            r"(Geo[Gg]uessr)",
            r"(Super Mario Maker 2)",
            r"(Civilization VI)",
            r"(Civilization V)",
            r"(Civilization IV)",
            r"(Rainbow Six Siege)",
            r"(Subnautica)",
            r"(Tetris 99)",
            r"(Baba Is You)",
            r"(Satisfactory)",
            r"(Dicey Dungeons)",
            r"(Crusader Kings II)",
        ]

        for regex_pat in simple_regex_attempts:
            matches = re.findall(regex_pat, title)
            if matches:
                return matches[0].strip().strip("!")

        # e.g. `Consider My Timbers Shivered - Pirate Outlaws (Northernlion Tries)`
        if "Northernlion Tries" in title:
            matches = re.findall(r"[^-]+ -+([^#(]+)", title)
            if matches:
                return matches[-1].strip()

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
