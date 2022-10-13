import dash_mantine_components as dmc
import pandas as pd
from dash import html
from log import get_logger


logger = get_logger(__name__)


def href_from_id(yt_id: str) -> str:
    return f"https://www.youtube.com/watch?v={yt_id}"


def link_from_id(link_text: str, yt_id: str) -> str:
    return dmc.Anchor(
        link_text,
        href=href_from_id(yt_id),
        target="_blank",
        weight="bold",
    )


def create_dmc_table(df: pd.DataFrame, spacing: str = "xs"):
    do_yt_links = "id" in df.columns and "Title" in df.columns

    def convert_row(row):
        cells = []
        for col in df.columns.tolist():
            if col == "id":
                continue
            elif col == "Title" and do_yt_links:
                cells.append(html.Td(link_from_id(link_text=row[col], yt_id=row["id"])))
            else:
                cells.append(html.Td(str(row[col])))

        return cells

    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th(col_name)
                    for col_name in df.columns.tolist()
                    if col_name != "id"
                ]
            )
        )
    ]

    rows = [html.Tr(convert_row(row)) for _, row in df.iterrows()]

    table_body = [html.Tbody(rows)]

    return dmc.Table(
        table_header + table_body,
        highlightOnHover=True,
        striped=True,
        verticalSpacing=spacing,
    )
