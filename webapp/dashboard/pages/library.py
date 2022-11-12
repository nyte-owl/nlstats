import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, State, callback, no_update

import log
from .. import data, util

logger = log.get_logger(__name__)

df_videos = data.df_latest_video_stats.sort_values(by="Publish Date", ascending=False)


def create_video_card(video: pd.Series):
    image = dmc.Image(
        src=f"https://i.ytimg.com/vi/{video['id']}/mqdefault.jpg",
        width=280,
    )
    views_text = f"{video['Views']:,} Views"
    publish_date: pd.Timestamp = video["Publish Date"]
    publish_date = (
        publish_date.tz_localize("utc").astimezone("US/Eastern").strftime("%Y-%m-%d")
    )
    publish_text = f"Posted {publish_date}"

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
        dmc.Text(publish_text),
    ]

    paper = dmc.Paper(
        card_content,
        withBorder=False,
        px="md",
        py="xs",
        style={"backgroundColor": dmc.theme.DEFAULT_COLORS["dark"][5]},
    )

    return paper


layout = dmc.Stack(
    [
        dmc.Center(dmc.Title("NorthernLion Library", order=1)),
        d_grid := dmc.SimpleGrid(
            cols=4,
            spacing="md",
            breakpoints=[{"maxWidth": "lg", "cols": 1}],
            children=[
                create_video_card(row) for _, row in df_videos.head(n=20).iterrows()
            ],
        ),
        dmc.Center(d_load_button := dmc.Button("Load more...", variant="outline")),
    ]
)


@callback(
    Output(d_grid, "children"),
    Input(d_load_button, "n_clicks"),
    State(d_grid, "children"),
)
def load_more_videos(n_clicks: int, old_output):
    if not n_clicks:
        return no_update

    page_start = n_clicks * 20
    page_end = page_start + 20
    return old_output + [
        create_video_card(row)
        for _, row in df_videos.iloc[page_start:page_end].iterrows()
    ]
