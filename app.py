import pytz
from dash import Dash, Input, Output, callback, dcc, html, State
from flask import request, redirect
import dash_mantine_components as dmc

from data import crud
from webapp.dashboard import pages
from webapp.dashboard.style import colors
import config

google_fonts_stylesheet = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@100;200;300;400;500;900&display=swap"
)
app = Dash(
    __name__,
    title="NL Stats",
    external_stylesheets=[google_fonts_stylesheet],
)
app.config.suppress_callback_exceptions = True

server = app.server


@server.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)


tab_style = {
    "backgroundColor": colors["background"],
    "color": colors["text"],
    "text-transform": "uppercase",
    "border-radius": "4px",
    "border": "2px dashed white",
    "margin": "4px",
}

tab_selected_style = tab_style.copy()
tab_selected_style.update(
    {"backgroundColor": colors["selected_color"], "border": "2px solid white"}
)

logo_size_pixels = 40

nav_buttons = dmc.Center(
    dmc.Group(
        position="right",
        align="center",
        spacing="xl",
        children=[
            dcc.Link(
                dmc.Text("Home", color="gray"),
                href="/",
                style={"textDecoration": "none"},
            ),
            dcc.Link(
                dmc.Text("Leaderboards", color="gray"),
                href="/leaderboards",
                style={"textDecoration": "none"},
            ),
            dcc.Link(
                dmc.Text("Monthly Reports", color="gray"),
                href="/monthly",
                style={"textDecoration": "none"},
            ),
        ],
    ),
    style={"height": f"{logo_size_pixels}px"},
)

logo_title = dmc.Center(
    dcc.Link(
        dmc.Group(
            [
                html.Img(
                    src=app.get_asset_url("egg.png"), height=f"{logo_size_pixels}"
                ),
                dmc.Text("NL Stats", size="xl", color="gray"),
            ],
            align="center",
            spacing="xs",
        ),
        href="/",
        style={"textDecoration": "none"},
    ),
)

navbar = dmc.Header(
    height=70,
    fixed=True,
    p="md",
    px="xl",
    children=[
        dmc.Container(
            fluid=True,
            children=dmc.Group(
                position="apart",
                align="flex-start",
                children=[logo_title, nav_buttons],
            ),
            px="xl",
        )
    ],
    style={"backgroundColor": dmc.theme.DEFAULT_COLORS["dark"][6]},
)

date_format = "%Y-%m-%d %H:%M:%S %Z%z"
date_pulled = crud.collection_event.get_most_recent_collection_event().pull_datetime

tz = pytz.timezone("America/New_York")
dt_est = date_pulled.astimezone(tz)

footer_notes = [
    "Content is updated daily at 2:05AM ET.",
    f"Data includes only videos posted since {config.settings.start_date}.",
    f"All data is current as of {dt_est:{date_format}}",
]

footer = []
for note in footer_notes:
    footer.append(html.Em(note))
    footer.append(html.Br())
footer.append(
    html.Img(
        src=app.get_asset_url("egg.png"),
        height="60px",
    )
)

app_content = html.Div(
    [
        d_url := dcc.Location(id="url"),
        navbar,
        dmc.Grid(
            div_page_content := dmc.Col(offset=1, span=8),
            columns=10,
            style={"padding-top": "90px"},
        ),
        html.Div(
            footer,
            style={"textAlign": "center", "padding": "25px"},
        ),
    ],
)
app.layout = dmc.MantineProvider(
    theme={"colorScheme": "dark"},
    children=[app_content],
    withGlobalStyles=True,
    withNormalizeCSS=True,
)


@callback(Output(div_page_content, "children"), Input(d_url, "pathname"))
def display_page(pathname):
    if pathname == "/":
        return pages.index.layout
    elif pathname == "/health":
        return html.P("OK")
    elif pathname == "/monthly":
        return pages.monthly.layout
    elif pathname == "/leaderboards":
        return pages.leaderboards.layout
    else:
        return html.P(f"404 - Not Found: {pathname}")


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)
