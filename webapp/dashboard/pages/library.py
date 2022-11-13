from typing import List
from enum import Enum

import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, callback, ctx, dcc, html, no_update
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
    likes_text = f"{video['Likes per 1000 Views']:.2f} Likes per 1000 Views"
    comments_text = f"{video['Comments per 1000 Views']:.2f} Comments per 1000 Views"

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
        dmc.Text(likes_text, weight=500),
        dmc.Text(comments_text, weight=500),
    ]

    paper = dmc.Paper(
        card_content,
        withBorder=True,
        px="md",
        py="xs",
        style={
            "backgroundColor": dmc.theme.DEFAULT_COLORS["dark"][6],
            "border-color": dmc.theme.DEFAULT_COLORS["dark"][3],
            "margin-left": "auto",
            "margin-right": "auto",
        },
        shadow="md",
    )

    return paper


class Frequency(Enum):
    by_day = "D"
    by_week = "W"
    by_month = "M"


def create_cards_from_df(
    df: pd.DataFrame,
    sort_selection: str,
    sort_ascending: bool,
    page: int | None,
    frequency: Frequency = Frequency.by_day,
):
    sorts = {
        "Date": "Publish Date",
        "View Count": "Views",
        "Like Rate": "Likes per 1000 Views",
        "Comment Rate": "Comments per 1000 Views",
    }

    if page is None:
        page = 0

    VIDEOS_PER_PAGE = 20

    if frequency == Frequency.by_week:
        pre_text = "Week ending "
        str_format = "%Y-%m-%d"
    elif frequency == Frequency.by_month:
        pre_text = ""
        str_format = "%B %Y"
    else:
        pre_text = ""
        str_format = "%Y-%m-%d"

    output = []
    if sort_selection == "Date":

        def get_frames(df: pd.DataFrame):
            freq = frequency.value
            day_grouper = pd.Grouper(key="Publish Date", freq=freq)
            if sort_ascending:
                return list(df.groupby(day_grouper, sort=False))
            else:
                return reversed(list(df.groupby(day_grouper, sort=False)))

        current_page_count = 0
        current_skip_count = 0
        for day, frame in get_frames(df):
            if frame.empty:
                continue

            if current_skip_count < (page * VIDEOS_PER_PAGE):
                current_skip_count += len(frame)
                current_page_count += len(frame)
                continue

            frame = frame.sort_values(
                by=sorts[sort_selection], ascending=sort_ascending
            )
            publish_date: pd.Timestamp = day
            publish_date = publish_date.strftime(str_format)
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
                    breakpoints=[
                        {"maxWidth": "xl", "cols": 3},
                        {"maxWidth": "lg", "cols": 2},
                        {"maxWidth": "sm", "cols": 1},
                    ],
                    style={"margin-bottom": "20px"},
                )
            )

            current_page_count += len(frame)
            if current_page_count >= (VIDEOS_PER_PAGE * (page + 1)):
                break

        on_last_page = current_page_count >= len(df)

    else:
        skip = page * VIDEOS_PER_PAGE
        df = df.sort_values(by=sorts[sort_selection], ascending=sort_ascending).iloc[
            skip : skip + 20
        ]
        output.append(
            dmc.SimpleGrid(
                children=[create_video_card(row) for _, row in df.iterrows()],
                cols=4,
                spacing="md",
                breakpoints=[
                    {"maxWidth": "xl", "cols": 3},
                    {"maxWidth": "lg", "cols": 2},
                    {"maxWidth": "sm", "cols": 1},
                ],
                style={"margin-bottom": "20px"},
            )
        )

        on_last_page = skip + 20 >= len(df)

    return output, on_last_page


modal = dmc.Modal(
    title="Select Filter",
    id="modal",
    children=[
        dmc.Text(
            "You can drag and select points on the graph to filter the results on this"
            " page."
        ),
        d_views_scatter := dcc.Graph(id="views-scatter"),
        d_clear_selection := dmc.Button("Clear Selection"),
    ],
    size="70%",
    centered=True,
)

layout = dmc.Stack(
    [
        modal,
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
                ),
            ],
        ),
        dmc.Group(
            children=[
                dmc.Group(
                    [
                        d_result_count := dmc.Text(),
                        d_open_modal := dmc.Button("Select Filter"),
                    ],
                    position="left",
                ),
                dmc.Group(
                    [
                        dmc.Text("Sort:"),
                        d_sort_selection := dmc.Select(
                            data=["Date", "View Count", "Like Rate", "Comment Rate"],
                            value="Date",
                        ),
                        d_sort_direction := dmc.ActionIcon(
                            DashIconify(icon="akar-icons:arrow-down-thick"),
                            color="blue",
                            variant="hover",
                        ),
                    ],
                    position="right",
                    spacing="xs",
                ),
            ],
            position="apart",
            align="flex-start",
        ),
        dmc.LoadingOverlay(
            d_content := html.Div(),
            loaderProps={"variant": "dots", "color": "red", "size": "xl"},
            style={"align-items": "start"},
        ),
        dmc.Center(
            d_load_button := dmc.Button(
                "Load more...", id="load-button", variant="outline"
            )
        ),
    ]
)


def get_youtube_ids_from_graph_selection(selected_data):
    return [point["customdata"][0] for point in selected_data["points"]]


def generate_views_scatter_figure(df: pd.DataFrame):
    fig = px.scatter(
        df,
        x="Publish Date",
        y="Views",
        template="plotly_dark",
        log_y=True,
        size="Likes per 1000 Views",
        height=500,
        hover_data=["Title", "Game"],
        custom_data=["id"],
    )
    fig.update_layout(
        transition_duration=1000,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        dragmode="select",
    )
    return fig


def selection_is_empty(selected_data):
    return selected_data is None or not selected_data["points"]


@callback(
    Output(d_content, "children"),
    Output(d_load_button, "n_clicks"),
    Output(d_result_count, "children"),
    Output(d_load_button, "disabled"),
    Input(d_load_button, "n_clicks"),
    Input(d_game_selector, "value"),
    Input(d_sort_direction, "n_clicks"),
    Input(d_sort_selection, "value"),
    Input(d_views_scatter, "selectedData"),
    State(d_content, "children"),
)
def load_more_videos(
    n_clicks_load_more: int,
    games: List[str],
    n_clicks_sort_direction: int,
    sort_selection: str,
    selected_data,
    old_output,
):
    if n_clicks_sort_direction is None:
        n_clicks_sort_direction = 0

    selection_empty = selection_is_empty(selected_data)
    logger.info(
        f">>>>> Load More Videos -- {n_clicks_load_more=}, {games=}, {selection_empty=}"
    )
    if games:
        df_selected = df_videos[df_videos["Game"].isin(games)]
        freq = Frequency.by_week
    else:
        df_selected = df_videos
        freq = Frequency.by_day

    if not selection_empty:
        selected_ids = get_youtube_ids_from_graph_selection(selected_data)
        df_selected = df_selected[df_selected["id"].isin(selected_ids)]
        freq = Frequency.by_month

    num_videos = len(df_selected)
    if ctx.triggered_id == "load-button":
        new_cards, paged_thru_all_videos = create_cards_from_df(
            df=df_selected,
            sort_selection=sort_selection,
            sort_ascending=n_clicks_sort_direction % 2 == 1,
            page=n_clicks_load_more,
            frequency=freq,
        )

        return (
            old_output + new_cards,
            no_update,
            f"{num_videos} Videos",
            paged_thru_all_videos,
        )
    else:
        new_cards, paged_thru_all_videos = create_cards_from_df(
            df=df_selected,
            sort_selection=sort_selection,
            sort_ascending=n_clicks_sort_direction % 2 == 1,
            page=0,
            frequency=freq,
        )
        return (
            new_cards,
            0,
            f"{num_videos} Videos",
            paged_thru_all_videos,
        )


@callback(
    Output(d_views_scatter, "figure"),
    Output(d_views_scatter, "selectedData"),
    Input(d_game_selector, "value"),
    Input(d_clear_selection, "n_clicks"),
)
def update_views_scatter(games: List[str], clear_n_clicks):
    logger.info(f">>>>> Update views scatter -- {games=}")
    if games:
        df_selected = df_videos[df_videos["Game"].isin(games)]
    else:
        df_selected = df_videos

    figure = generate_views_scatter_figure(df_selected)

    return figure, None


@callback(
    Output(modal, "opened"),
    Input(d_open_modal, "n_clicks"),
    State(modal, "opened"),
    prevent_initial_call=True,
)
def toggle_modal(n_clicks, opened):
    return not opened


@callback(
    Output(d_clear_selection, "disabled"),
    Output(d_open_modal, "variant"),
    Input(d_views_scatter, "selectedData"),
)
def enable_clear_selection_button(selected_data):
    logger.info(">>>> clear button")

    if selection_is_empty(selected_data):
        variant = "outline"
    else:
        variant = "filled"

    return selection_is_empty(selected_data), variant


@callback(Output(d_sort_direction, "children"), Input(d_sort_direction, "n_clicks"))
def toggle_sort_arrow(n_clicks):
    if n_clicks is None:
        n_clicks = 0

    if n_clicks % 2 == 0:
        return DashIconify(icon="akar-icons:arrow-down-thick")
    else:
        return DashIconify(icon="akar-icons:arrow-up-thick")
