import random
from datetime import date, timedelta

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, ctx, dcc, html, no_update
from dash_iconify import DashIconify

from .. import data, util
import config
import log


logger = log.get_logger(__name__)


def create_card(title: str, body, centered: bool = True, icon: str | None = None):
    if centered:
        body = dmc.Center(body)
    if icon:
        icon = [DashIconify(icon=icon)]

    return dmc.Alert(title=title, children=body, icon=icon, color="green")


def create_graph_card(title: str, figure, extra_content=[]):
    card_content = (
        dmc.Stack(
            [
                dmc.Text(title, color="green", weight="bold", size="sm"),
                dmc.LoadingOverlay(children=[dcc.Graph(figure=figure)]),
            ]
            + extra_content,
            spacing="xs",
            align="stretch",
        ),
    )

    content = dmc.Paper(
        card_content,
        withBorder=True,
        px="md",
        py="xs",
        style={"backgroundColor": dmc.theme.DEFAULT_COLORS["dark"][5]},
    )

    return content


def create_stat_card(
    title: str, stat_num: str, centered: bool = True, icon: str | None = None
):
    gradient = random.randint(0, 360)
    return create_card(
        title=title,
        body=dmc.Text(
            stat_num,
            variant="gradient",
            gradient={"from": "blue", "to": "grape", "deg": gradient},
            style={"fontSize": 50},
        ),
        centered=centered,
        icon=icon,
    )


class GridBuilder:
    def __init__(self):
        self.children = []

    def add_col(self, body, width: int = 4):
        self.children.append(dmc.Col(children=body, span=width))

    def get_grid(self) -> dmc.Grid:
        return dmc.Grid(children=self.children, gutter="xl", grow=True)


def get_content(date_picked: date):
    df = data.df_videos[
        (data.df_videos["Publish Date"].dt.month == date_picked.month)
        & (data.df_videos["Publish Date"].dt.year == date_picked.year)
    ]

    by_game_accordion = []
    for game, game_df in df.groupby("Game"):
        accordion = dmc.AccordionItem(
            label=game,
            children=[
                util.create_dmc_table(
                    game_df[
                        ["id", "Title", "Publish Date", "Views", "Likes", "Comments"]
                    ]
                )
            ],
        )
        by_game_accordion.append(accordion)

    post_history = dmc.Accordion(
        icon=[
            DashIconify(
                icon="tabler:arrow-big-down-line",
                color=dmc.theme.DEFAULT_COLORS["green"][6],
            )
        ],
        children=by_game_accordion,
        multiple=True,
        iconPosition="right",
    )

    most_viewed_video = df.sort_values(by="Views", ascending=False).iloc[0]
    most_liked_video = df.sort_values(by="Likes per 1000 Views", ascending=False).iloc[
        0
    ]
    most_discussed_video = df.sort_values(
        by="Comments per 1000 Views", ascending=False
    ).iloc[0]

    # PIE
    df_game_count = (
        df.groupby("Game")["Title"]
        .count()
        .to_frame()
        .reset_index()
        .rename({"Title": "Count"}, axis=1)
    )
    top_games = (
        df_game_count.sort_values(by="Count", ascending=False).iloc[:4]["Game"].tolist()
    )
    df_game_count.loc[df_game_count["Count"] == 1, "Game"] = "'Other' Games"

    pie_game_count = px.pie(df_game_count, values="Count", names="Game")
    pie_game_count.update_layout(
        legend_borderwidth=3,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # Posts
    date_grouper = pd.Grouper(key="Publish Date", freq="1D")
    df.loc[~df["Game"].isin(top_games), "Game"] = "'Other' Games"
    df_post_history = (
        df.groupby([date_grouper, "Game"])
        .count()["Title"]
        .to_frame()
        # .cumsum()
        .reset_index()
        .rename({"Publish Date": "Date", "Title": "Count"}, axis=1)
    )
    df_post_history = df_post_history.sort_values(by="Game")

    bar_post_history = px.bar(df_post_history, x="Date", y="Count", color="Game")
    bar_post_history.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    def top_video_layout(video: pd.Series, key_column: str):
        image = dmc.Image(
            src=f"https://i.ytimg.com/vi/{video['id']}/mqdefault.jpg",
            width=320,
        )
        return dmc.Container(
            [
                image,
                html.H4(video["Title"]),
                html.P(f"{video[key_column]} {key_column}"),
            ],
            px=0,
        )

    content_grid_builder = GridBuilder()
    content_grid_builder.add_col(
        create_card(
            title="Most Viewed Video",
            body=top_video_layout(most_viewed_video, "Views"),
            centered=False,
            icon="akar-icons:eye",
        )
    )
    content_grid_builder.add_col(
        create_card(
            title="Most Liked Video",
            body=top_video_layout(most_liked_video, "Likes per 1000 Views"),
            centered=False,
            icon="fa:thumbs-o-up",
        )
    )

    content_grid_builder.add_col(
        create_card(
            title="Most Discussed Video",
            body=top_video_layout(most_discussed_video, "Comments per 1000 Views"),
            centered=False,
            icon="bx:comment-detail",
        )
    )

    stat_column = GridBuilder()
    stat_column.add_col(
        create_stat_card(
            title="Videos Published",
            stat_num=str(len(df)),
            icon="material-symbols:youtube-activity",
        ),
        width=12,
    )
    stat_column.add_col(
        create_stat_card(
            title="Total Views",
            stat_num=f'{df["Views"].sum():,}',
            icon="akar-icons:eye",
        ),
        width=12,
    )
    stat_column.add_col(
        create_stat_card(
            title="Comments per 1000 Views",
            stat_num=f'{df["Comments per 1000 Views"].mean():.04}',
            icon="bx:comment-detail",
        ),
        width=12,
    )

    content_grid_builder.add_col(stat_column.get_grid())

    content_grid_builder.add_col(
        create_graph_card(
            title="Featured Games",
            figure=pie_game_count,
        ),
        width=8,
    )

    content_grid_builder.add_col(
        create_graph_card(
            title="Post History", figure=bar_post_history, extra_content=[post_history]
        ),
        width=12,
    )

    return [
        content_grid_builder.get_grid(),
    ]


min_date = date.fromisoformat(config.settings.start_date)
if min_date.day == 1:
    min_date = min_date + timedelta(days=1)


month_nav = dmc.Group(
    [
        d_previous_month := dmc.Button(
            children="",
            leftIcon=[DashIconify(icon="akar-icons:arrow-left-thick")],
            id="prev-month-btn",
        ),
        d_date_picker := dmc.DatePicker(
            value=date.today(),
            inputFormat="MMMM YYYY",
            initialLevel="month",
            style={"text-align": "center"},
            allowLevelChange=False,
            shadow="md",
            maxDate=date.today(),
            minDate=min_date,
            icon=[DashIconify(icon="clarity:date-line")],
        ),
        d_next_month := dmc.Button(
            children="",
            rightIcon=[DashIconify(icon="akar-icons:arrow-right-thick")],
            id="next-month-btn",
        ),
    ],
    position="center",
)

layout = html.Div(
    children=[
        dbc.Row(
            [html.H1("Monthly Report")],
            style={"text-align": "center"},
        ),
        dmc.Container(
            dmc.Paper(
                children=month_nav,
                p="sm",
                radius="md",
            ),
            size="sm",
        ),
        dbc.Row(
            [d_current_month := html.H2("")],
            style={"text-align": "center", "margin-top": "20px"},
        ),
        dbc.Row(
            dbc.Col(d_content := dmc.LoadingOverlay()),
        ),
    ],
)


@callback(
    Output(d_content, "children"),
    Output(d_current_month, "children"),
    Output(d_previous_month, "children"),
    Output(d_previous_month, "disabled"),
    Output(d_next_month, "children"),
    Output(d_next_month, "disabled"),
    Input(d_date_picker, "value"),
)
def update_content(date_value):
    logger.info(f"[monthly] Update monthly page with date {date_value}")
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
        next_month: date = (date_object + pd.DateOffset(months=1)).date()
        previous_month: date = (date_object - pd.DateOffset(months=1)).date()

        start_date = date.fromisoformat(config.settings.start_date)
        today = date.today()

        prev_month_invalid = (
            previous_month.year == start_date.year
            and previous_month.month < start_date.month
        ) or previous_month.year < start_date.year
        next_month_invalid = (
            next_month.year == today.year and next_month.month > today.month
        ) or next_month.year > today.year

        return (
            get_content(date_object),
            date_object.strftime("%B %Y"),
            previous_month.strftime("%B %Y"),
            prev_month_invalid,
            next_month.strftime("%B %Y"),
            next_month_invalid,
        )
    else:
        return "Pick a date", "", "", ""


@callback(
    Output(d_date_picker, "value"),
    Input(d_next_month, "n_clicks"),
    Input(d_previous_month, "n_clicks"),
    Input(d_date_picker, "value"),
)
def update_calendar_from_button(n_clicks_next, n_clicks_prev, date_value):
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
        if ctx.triggered_id == "next-month-btn":
            new_date: date = (date_object + pd.DateOffset(months=1)).date()
            logger.info(f"[monthly] Next month button - {new_date}")
        elif ctx.triggered_id == "prev-month-btn":
            new_date: date = (date_object - pd.DateOffset(months=1)).date()
            logger.info(f"[monthly] Previous month button - {new_date}")
        else:
            new_date = date_value

        return new_date
    else:
        return no_update
