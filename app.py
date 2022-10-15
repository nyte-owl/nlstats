import pytz
from dash import Dash, Input, Output, callback, dcc, html
from flask import request, redirect
import dash_mantine_components as dmc

from data import crud
from webapp.dashboard import pages, content
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
app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
    </head>
    <body style="background-color:{dmc.theme.DEFAULT_COLORS["dark"][7]}">
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""

server = app.server


@server.before_request
def before_request():
    if config.settings.local_development:
        return

    if not request.is_secure:
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)


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
        content.header.make_navbar(logo_url=app.get_asset_url("egg.png")),
        div_page_content := dmc.Container(
            style={"margin-top": "90px"},
            px="xs",
            size="xl",
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


if __name__ == "__main__":
    app.run_server(debug=True)
