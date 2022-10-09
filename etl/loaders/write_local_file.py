import os
from datetime import date

import log
import pandas as pd

logger = log.get_logger(__name__)


def _get_filepath(name: str) -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "local_data",
        f"{name}_{date.today().strftime('%Y_%m_%d')}.parquet",
    )


def write_latest_raw_youtube(df: pd.DataFrame) -> pd.DataFrame:
    logger.debug(f"write_latest_raw_youtube {df.shape=}")
    path = _get_filepath("raw_youtube")
    df.to_parquet(path, engine="fastparquet")
    return df


def write_latest_processed_youtube(df: pd.DataFrame) -> pd.DataFrame:
    logger.debug(f"write_latest_processed_youtube {df.shape=}")
    path = _get_filepath("youtube")
    df.to_parquet(path, engine="fastparquet")
    return df
