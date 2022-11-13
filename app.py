import pytz
from dash import Dash, Input, Output, callback, dcc, html
from flask import request, redirect
import dash_mantine_components as dmc

from data import crud
from webapp.dashboard import pages, content
import config

import log

logger = log.get_logger(__name__)

google_fonts_stylesheet = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@100;200;300;400;500;900&display=swap"
)

title = "NL Stats"
description = "See the latest stats and trends for the NorthernLion YouTube channel."

app = Dash(
    __name__,
    title="NL Stats",
    external_stylesheets=[google_fonts_stylesheet],
    meta_tags=[
        {"name": "title", "content": title},
        {"name": "description", "content": description},
    ],
)
app.config.suppress_callback_exceptions = True

gtag_js_url = (
    f"https://www.googletagmanager.com/gtag/js?id={config.settings.gtag_analytics_code}"
)
preview_image = config.settings.custom_url.rstrip("/") + app.get_asset_url(
    "preview_image.png"
)
app.index_string = f"""<!DOCTYPE html>
<html>
    <head>
        <!-- Google tag (gtag.js) -->
        <script async src="{gtag_js_url}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}}
            gtag('js', new Date());

            gtag('config', '{config.settings.gtag_analytics_code}');
        </script>

        {{%metas%}}
        <meta property="og:type" content="website">
        <meta property="og:url" content="{config.settings.custom_url}">
        <meta property="og:title" content="{title}">
        <meta property="og:description" content="{description}">
        <meta property="og:image" content="{preview_image}">

        <meta property="twitter:card" content="summary_large_image">
        <meta property="twitter:url" content="{config.settings.custom_url}">
        <meta property="twitter:title" content="{title}">
        <meta property="twitter:description" content="{description}">
        <meta property="twitter:image" content="{preview_image}">

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
    f"All data is current as of {dt_est:{date_format}}",
    f"Data includes only videos posted since {config.settings.start_date}.",
    "Content is pulled daily at 8:05PM PST, 5:05PM EST.",
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
    theme={
        "colorScheme": "dark",
        "fontFamily": "'Inter', sans-serif",
    },
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
    elif pathname == "/library":
        return pages.library.layout
    else:
        return html.P(f"404 - Not Found: {pathname}")


if __name__ == "__main__":
    app.run_server(debug=True)
