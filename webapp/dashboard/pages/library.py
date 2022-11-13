from typing import List

import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, State, callback, ctx, html, no_update
from dash_iconify import DashIconify

import log
from .. import data, util

logger = log.get_logger(__name__)

df_videos = data.df_latest_video_stats.sort_values(by="Publish Date", ascending=False)
df_videos["Publish Date"] = (
    df_videos["Publish Date"].dt.tz_localize("utc").dt.tz_convert("US/Pacific")
)


def create_video_card(video: pd.Series):
    image = dmc.Image(
        src=f"https://i.ytimg.com/vi/{video['id']}/mqdefault.jpg",
        width=280,
    )
    views_text = f"{video['Views']:,} Views"

    card_content = [
        dmc.Anchor(
            [
                image,
                dmc.Title(video["Title"], order=5),
            ],
            href=util.href_from_id(video["id"]),
            target="_blank",
        ),
        dmc.Text(views_text, weight=500),
    ]

    paper = dmc.Paper(
        card_content,
        withBorder=False,
        px="md",
        py="xs",
        style={"backgroundColor": dmc.theme.DEFAULT_COLORS["dark"][5]},
    )

    return paper


def create_cards_from_df(df: pd.DataFrame, page: int | None, by_week: bool = False):
    if page is None:
        page = 0

    VIDEOS_PER_PAGE = 20

    if by_week:
        pre_text = "Week ending "
        freq = "W"
    else:
        pre_text = ""
        freq = "D"

    day_grouper = pd.Grouper(key="Publish Date", freq=freq)
    output = []
    current_page_count = 0
    current_skip_count = 0
    for day, frame in reversed(list(df.groupby(day_grouper, sort=False))):
        publish_date: pd.Timestamp = day
        publish_date = publish_date.strftime("%Y-%m-%d")

        logger.debug(
            f"{publish_date=}, {current_skip_count=}, {current_page_count=}, "
            f"{len(frame)=}"
        )
        if frame.empty:
            continue

        if current_skip_count < (page * VIDEOS_PER_PAGE):
            current_skip_count += len(frame)
            current_page_count += len(frame)
            continue

        frame = frame.sort_values(by="Publish Date", ascending=False)
        publish_text = pre_text + publish_date
        output.append(
            dmc.Divider(
                label=[
                    DashIconify(icon="ant-design:calendar-twotone"),
                    dmc.Space(w="xs"),
                    f"{publish_text}",
                ],
                color="red",
                variant="dashed",
                labelPosition="center",
                style={"margin-bottom": "5px"},
            )
        )

        output.append(
            dmc.SimpleGrid(
                children=[create_video_card(row) for _, row in frame.iterrows()],
                cols=4,
                spacing="md",
                breakpoints=[{"maxWidth": "lg", "cols": 1}],
                style={"margin-bottom": "20px"},
            )
        )

        current_page_count += len(frame)
        if current_page_count >= (VIDEOS_PER_PAGE * (page + 1)):
            break

    logger.debug(f"-- {current_skip_count=}, {current_page_count=} --")
    return output


layout = dmc.Stack(
    [
        dmc.Center(dmc.Title("NorthernLion Library", order=1)),
        dmc.Center(
            [
                d_game_selector := dmc.MultiSelect(
                    icon=[DashIconify(icon="cil:magnifying-glass")],
                    data=data.all_games.index.to_list(),
                    searchable=True,
                    nothingFound="No games found",
                    size="xl",
                    id="game-select",
                    style={"width": 500},
                    placeholder="Search games...",
                )
            ]
        ),
        d_content := html.Div(),
        dmc.Center(
            d_load_button := dmc.Button(
                "Load more...", id="load-button", variant="outline"
            )
        ),
    ]
)


@callback(
    Output(d_content, "children"),
    Output(d_load_button, "n_clicks"),
    Input(d_load_button, "n_clicks"),
    Input(d_game_selector, "value"),
    State(d_content, "children"),
)
def load_more_videos(n_clicks: int, games: List[str], old_output):
    if games:
        df_selected = df_videos[df_videos["Game"].isin(games)]
    else:
        df_selected = df_videos

    if ctx.triggered_id == "load-button":
        new_cards = create_cards_from_df(
            df_selected,
            page=n_clicks,
            by_week=bool(games),
        )

        return (
            old_output + new_cards,
            no_update,
        )
    elif ctx.triggered_id == "game-select":
        new_cards = create_cards_from_df(
            df_selected,
            page=0,
            by_week=bool(games),
        )
        return (
            new_cards,
            0,
        )
    else:
        new_cards = create_cards_from_df(
            df_selected,
            page=0,
            by_week=bool(games),
        )
        return (
            new_cards,
            0,
        )
