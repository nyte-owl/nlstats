from functools import lru_cache
from typing import List

from dash import dcc, html, Input, Output, callback
from dash_bootstrap_templates import load_figure_template
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.express as px

from .. import data

load_figure_template("darkly")

fig_views_over_time = px.scatter(
    data.df_views_over_time,
    x="Publish Date",
    y="Views",
    log_y=True,
    trendline="rolling",
    trendline_options=dict(window=10),
    height=500,
)

fig_views_over_time.update_layout(
    margin=dict(l=10, r=20, t=20, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)

layout = html.Div(
    style={
        "textAlign": "center",
    },
    children=[
        dmc.Title("Video View Count", order=1),
        html.P(
            children=(
                "This graph shows how many views NL's videos have accrued to date.  "
                "The size of the points represent the number of likes each video "
                "received."
            ),
        ),
        dmc.LoadingOverlay(
            children=[
                d_main_scatter := dcc.Graph(),
            ],
        ),
        html.Br(),
        dmc.Container(
            dmc.Paper(
                children=[
                    d_trace_selector := dmc.MultiSelect(
                        label=[
                            "Select games to display ",
                            DashIconify(icon="ant-design:dot-chart-outlined"),
                        ],
                        description="You can select a maxiumum of 5 games",
                        data=data.all_games.index.to_list(),
                        value=data.most_uploaded,
                        searchable=True,
                        nothingFound="No games found",
                        maxSelectedValues=5,
                        size="md",
                    ),
                ],
                p="sm",
                radius="md",
                withBorder=True,
            ),
            size="sm",
        ),
        html.Br(),
        dmc.Divider(variant="dashed", size="md"),
        html.Br(),
        dmc.Title("Total Views Over Time (Weekly)", order=1),
        html.P(
            "This graph presents the total views (today) of all videos posted "
            "in a given week.  NOTE: There is a bias towards older videos as newer "
            "videos have not had as much time to accumulate views. This is especially "
            "true for videos that are only a few days old."
        ),
        dmc.LoadingOverlay(
            children=[
                d_views_over_time := dcc.Graph(figure=fig_views_over_time),
            ],
        ),
    ],
)


@lru_cache(maxsize=20)
def generate_figure(games_selection):
    if games_selection:
        filtered_videos = data.df_videos[data.df_videos["Game"].isin(games_selection)]
    else:
        filtered_videos = data.df_videos[
            data.df_videos["Game"].isin(data.most_uploaded)
        ]

    fig = px.scatter(
        filtered_videos,
        x="Publish Date",
        y="Views",
        log_y=True,
        size="Likes per 1000 Views",
        color="Game",
        # trendline="rolling",
        # trendline_options=dict(window=7),
        height=500,
        hover_data=["Title"],
        category_orders={"Game": games_selection},
    )
    fig.update_layout(
        transition_duration=1000,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    return fig


default_figure = generate_figure(tuple(data.most_uploaded))


@callback(Output(d_main_scatter, "figure"), Input(d_trace_selector, "value"))
def update_plotted_games(games_selection: List[str]):
    if games_selection == data.most_uploaded:
        return default_figure
    else:
        return generate_figure(tuple(games_selection))
