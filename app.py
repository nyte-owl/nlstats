import pytz
from dash import Dash, Input, Output, callback, dcc, html, State
from flask import request, redirect
import dash_mantine_components as dmc
from dash_iconify import DashIconify

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
    if config.settings.local_development:
        return

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


def make_header_link(text: str, href: str, icon: str) -> dcc.Link:
    text_portion = dmc.Text(text, color="gray")
    icon_portion = dmc.ThemeIcon(
        DashIconify(
            icon=icon,
            width=22,
        ),
        radius=30,
        size=36,
        variant="outline",
        color="blue",
    )
    return dcc.Link(
        dmc.Group([icon_portion, text_portion], spacing="xs"),
        href=href,
        style={"textDecoration": "none"},
    )


nav_buttons = dmc.Center(
    dmc.Group(
        position="right",
        align="center",
        spacing="xl",
        children=[
            make_header_link("Home", "/", "bi:house-door"),
            make_header_link(
                "Leaderboards", "/leaderboards", "ant-design:ordered-list-outlined"
            ),
            make_header_link(
                "Monthly Reports", "/monthly", "ant-design:calendar-outlined"
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
        div_page_content := dmc.Container(
            style={"margin-top": "90px"},
            px="xl",
            size="lg",
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
