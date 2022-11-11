from functools import lru_cache
from typing import List

from dash import dcc, html, Input, Output, callback, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import page_data
from ... import data

CHART_HEIGHT = 600

fig_views_over_time = px.scatter(
    page_data.df_views_over_time,
    x="Publish Date",
    y="Views",
    template="plotly_dark",
    log_y=True,
    trendline="rolling",
    trendline_options=dict(window=10),
    height=CHART_HEIGHT,
)

fig_views_over_time.update_layout(
    margin=dict(l=10, r=20, t=20, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)


def create_performance_chart(
    x_axis: str,
    y_axis: str,
    line_data: pd.DataFrame,
    color: str,
    middle_50_x,
    middle_50_y,
):
    figure = px.line(
        line_data,
        x=x_axis,
        y=y_axis,
        template="plotly_dark",
        color=color,
        log_y=True,
        markers=True,
        hover_data=["Title", "Publish Date", "Views"],
        height=CHART_HEIGHT,
    )
    figure.update_layout(
        transition_duration=1000,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        hovermode="x",
    )
    figure.add_trace(
        go.Scatter(
            x=middle_50_x,
            y=middle_50_y,
            fill="toself",
            fillcolor="rgba(243,215,200,0.3)",
            line_color="rgba(255,255,255,0)",
            name="Middle 50%",
            hoverinfo="none",
        )
    )

    return figure


fig_new_series_trend = create_performance_chart(
    x_axis="Video #",
    y_axis="Cumulative Views",
    line_data=page_data.df_small_game_series_video_stats,
    color="Game",
    middle_50_x=page_data.middle_50_x,
    middle_50_y=page_data.middle_50_y,
)

tab_definitions = {
    "New Video Trends": "bx:trending-up",
    "New Game Series Trends": "bx:trending-up",
    "Video View Count": "akar-icons:eye",
    "Total Channel Views": "akar-icons:eye",
}
page_content = dmc.Paper(
    children=[
        d_tabs := dmc.Tabs(
            active=0,
            children=[
                dmc.Tab(label=[DashIconify(icon=icon), f" {name}"])
                for name, icon in tab_definitions.items()
            ],
            color="red",
        ),
        d_content := html.Div(),
    ],
    withBorder=True,
    px="sm",
    py="sm",
)

new_video_chart_description = """
    This shows the performance of newly-posted (within the last week)
    videos.  It shows the view count of the video over time.  The shaded area
    represents the 'Middle 50%' of all game series performance. Values above the shaded
    area are in the Top 25% of cumulative views, while values below the shaded area are
    in the Bottom 25%.
"""
new_video_trends_tab = html.Div(
    children=[
        html.P(new_video_chart_description),
        dmc.Container(
            dmc.Paper(
                children=[
                    d_daily_game_selector := dmc.Select(
                        label=[
                            "Select game to display ",
                            DashIconify(icon="ant-design:dot-chart-outlined"),
                        ],
                        data=page_data.df_new_videos_stats["Game"].unique().tolist(),
                        value=np.random.choice(
                            page_data.df_new_videos_stats["Game"].unique()
                        ),
                        size="md",
                    ),
                ],
                p="sm",
                radius="md",
                withBorder=True,
            ),
            size="sm",
        ),
        dmc.LoadingOverlay(
            children=[
                d_daily_chart := dcc.Graph(),
            ],
        ),
    ]
)

new_game_series_chart_description = """
    This shows the performance of newly-posted (within the last 3 weeks)
    game series.  It shows the cumulative view counts of the series for each
    successive video.  The shaded area represents the 'Middle 50%' of all
    game series performance. Values above the shaded area are in the Top 25%
    of cumulative views, while values below the shaded area are in the Bottom
    25%.
"""
new_game_series_trends_tab = html.Div(
    children=[
        html.P(new_game_series_chart_description),
        dmc.LoadingOverlay(
            children=[
                dcc.Graph(figure=fig_new_series_trend),
            ],
        ),
    ]
)

video_views_tab = html.Div(
    children=[
        html.P(
            children=(
                "This shows how many views NL's videos have accrued to date.  "
                "The size of the points represent the number of likes each video "
                "received."
            ),
        ),
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
        dmc.LoadingOverlay(
            children=[
                d_main_scatter := dcc.Graph(),
            ],
        ),
    ]
)

channel_views_tab = html.Div(
    children=[
        html.P(
            "This presents the total views (today) of all videos posted "
            "in a given week.  NOTE: There is a bias towards older videos as newer "
            "videos have not had as much time to accumulate views. This is especially "
            "true for videos that are only a few days old."
        ),
        dmc.LoadingOverlay(
            children=[
                d_views_over_time := dcc.Graph(figure=fig_views_over_time),
            ],
        ),
    ]
)

tab_contents = [
    new_video_trends_tab,
    new_game_series_trends_tab,
    video_views_tab,
    channel_views_tab,
]

layout = html.Div(
    children=[
        html.Br(),
        page_content,
    ],
)


@lru_cache(maxsize=20)
def generate_daily_chart(game_selection: str):
    df = page_data.df_new_videos_stats[
        page_data.df_new_videos_stats["Game"] == game_selection
    ]
    return create_performance_chart(
        x_axis="Days Elapsed",
        y_axis="Views",
        line_data=df,
        color="Title",
        middle_50_x=page_data.daily_middle_50_x,
        middle_50_y=page_data.daily_middle_50_y,
    )


@lru_cache(maxsize=20)
def generate_figure(games_selection):
    if games_selection:
        filtered_videos = data.df_latest_video_stats[
            data.df_latest_video_stats["Game"].isin(games_selection)
        ]
    else:
        filtered_videos = data.df_latest_video_stats[
            data.df_latest_video_stats["Game"].isin(data.most_uploaded)
        ]

    fig = px.scatter(
        filtered_videos,
        x="Publish Date",
        y="Views",
        template="plotly_dark",
        log_y=True,
        size="Likes per 1000 Views",
        color="Game",
        # trendline="rolling",
        # trendline_options=dict(window=7),
        height=CHART_HEIGHT,
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


@callback(Output(d_daily_chart, "figure"), Input(d_daily_game_selector, "value"))
def update_daily_chart_game(games_selection: str):
    return generate_daily_chart(games_selection)


@callback(Output(d_content, "children"), Input(d_tabs, "active"))
def switch_views_board(active_tab: int):
    return tab_contents[active_tab]


@callback(Output(d_daily_game_selector, "value"), Input(d_tabs, "active"))
def select_random_game(active_tab: int):
    if active_tab == 0:
        return np.random.choice(page_data.df_new_videos_stats["Game"].unique())
    else:
        return no_update
