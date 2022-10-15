import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify

logo_size_pixels = 40


def make_header_link(text: str, href: str, icon: str) -> dcc.Link:
    text_portion = dmc.MediaQuery(
        dmc.Text(text, color="gray"), smallerThan="sm", styles={"display": "none"}
    )
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


def make_navbar_logo(logo_url: str) -> dmc.Group:
    return dmc.Group(
        [
            html.Img(src=logo_url, height=f"{logo_size_pixels}"),
            dmc.MediaQuery(
                dmc.Text("NL Stats", size="xl", color="gray"),
                smallerThan="xs",
                styles={"display": "none"},
            ),
        ],
        align="center",
        spacing="xs",
    )


def make_navbar(logo_url: str) -> dmc.Header:
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
            make_navbar_logo(logo_url),
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

    return navbar
