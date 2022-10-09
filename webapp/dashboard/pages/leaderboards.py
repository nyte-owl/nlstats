from enum import Enum

from dash import html, callback, Output, Input
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd

from .. import data
from log import get_logger

logger = get_logger(__name__)


class LeaderboardTab(str, Enum):
    views = "Views"
    likes = "Likes"
    activity = "Activity"
    length = "Length"


def create_dmc_table(df: pd.DataFrame):
    table_header = [
        html.Thead(html.Tr([html.Th(col_name) for col_name in df.columns.tolist()]))
    ]

    rows = [
        html.Tr([html.Td(str(row[col])) for col in df.columns.tolist()])
        for _, row in df.iterrows()
    ]

    table_body = [html.Tbody(rows)]

    return dmc.Table(
        table_header + table_body,
        highlightOnHover=True,
        striped=True,
    )


def make_single_leaderboard(dataframe: pd.DataFrame):
    dmc_table = create_dmc_table(dataframe)
    return html.Div(children=[dmc_table])


all_boards = {
    "game_views_overall": {
        "df": data.df_most_viewed_games.head(n=50),
        "label": "Most Viewed Game - Overall",
        "tab": LeaderboardTab.views,
    },
    "game_views_average": {
        "df": data.df_biggest_view_getters.head(n=50),
        "label": "Most Viewed Game - On Average",
        "tab": LeaderboardTab.views,
    },
    "video_views_overall": {
        "df": data.df_most_viewed_videos.head(n=50),
        "label": "Most Viewed Video - Overall",
        "tab": LeaderboardTab.views,
    },
    "game_likes_overall": {
        "df": data.df_game_highest_like_rate.head(n=50),
        "label": "Highest Game Like Rate (Likes per 1000 Views) - Overall",
        "tab": LeaderboardTab.likes,
    },
    "game_likes_average": {
        "df": data.df_biggest_like_getters.head(n=50),
        "label": "Highest Game Like Rate (Likes per 1000 Views) - On Average",
        "tab": LeaderboardTab.likes,
    },
    "video_likes_overall": {
        "df": data.df_video_highest_like_rate.head(n=50),
        "label": "Most Liked Video (per 1000 Views) - Overall",
        "tab": LeaderboardTab.likes,
    },
    "most_published_overall": {
        "df": data.df_most_published_games.head(n=50),
        "label": "Most Published Game - Overall",
        "tab": LeaderboardTab.activity,
    },
    "most_published_monthly": {
        "df": data.df_top_monthly.tail(n=24),
        "label": "Most Published Game - Monthly",
        "tab": LeaderboardTab.activity,
    },
    "longest_videos_overall": {
        "df": data.df_longest_videos.head(n=50),
        "label": "Longest Video - Overall",
        "tab": LeaderboardTab.length,
    },
}

tab_definitions = {
    LeaderboardTab.views: "akar-icons:eye",
    LeaderboardTab.likes: "fa:thumbs-o-up",
    LeaderboardTab.activity: "material-symbols:youtube-activity",
    LeaderboardTab.length: "bxs:time-five",
}

tab_selections = [
    [
        {"value": key, "label": info["label"]}
        for key, info in all_boards.items()
        if info["tab"] == tab
    ]
    for tab in tab_definitions.keys()
]

tab_content = dmc.Container(
    children=[
        dmc.Center(
            d_select := dmc.Select(
                size="xl",
                variant="default",
                icon=[DashIconify(icon="line-md:menu-unfold-right")],
                style={"width": "60%", "margin-bottom": "20px"},
                radius="md",
            ),
        ),
        dmc.LoadingOverlay(children=[d_content := dmc.Container(children=[])]),
    ]
)

page_content = dmc.Paper(
    children=[
        d_tabs := dmc.Tabs(
            active=0,
            children=[
                dmc.Tab(label=[DashIconify(icon=icon), f" {name.value}"])
                for name, icon in tab_definitions.items()
            ],
            color="red",
        ),
        tab_content,
    ],
    withBorder=True,
    style={"padding": "25px"},
)

layout = html.Div(
    children=[html.Br(), page_content],
)


@callback(Output(d_select, "data"), Output(d_select, "value"), Input(d_tabs, "active"))
def switch_tab(active_tab: int):
    logger.debug(f"enter: {active_tab}")
    return tab_selections[active_tab], tab_selections[active_tab][0]["value"]


@callback(Output(d_content, "children"), Input(d_select, "value"))
def switch_views_board(selected_board):
    return make_single_leaderboard(all_boards[selected_board]["df"])
