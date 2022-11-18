import json

import pandas as pd

from data.crud.raw_data import get_most_recent_raw_dataframe


def read_raw_data() -> pd.DataFrame():
    df = get_most_recent_raw_dataframe()

    col_map = {
        "kind": "kind",
        "etag": "etag",
        "snippet": "snippet",
        "content_details": "contentDetails",
        "statistics": "statistics",
    }
    for db_col, df_col in col_map.items():
        df[df_col] = df[db_col].apply(lambda r: json.loads(r))

    return df
