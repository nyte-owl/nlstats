from datetime import date, timedelta
import os
import pandas as pd

from log import get_logger

logger = get_logger(__name__)


def _get_filepath(name: str) -> str:
    check_day = date.today()
    for _ in range(7):
        path = os.path.join(
            os.path.dirname(__file__),
            f"{name}_{check_day.strftime('%Y_%m_%d')}.parquet",
        )
        logger.debug(f"Check {path=}")
        if os.path.exists(path):
            break
        else:
            check_day = check_day - timedelta(days=1)
    else:
        raise RuntimeError("No recent file :(")

    return path


def read_latest_raw_youtube() -> pd.DataFrame:
    path = _get_filepath("raw_youtube")
    return pd.read_parquet(path, engine="fastparquet")


def read_latest_processed_youtube() -> pd.DataFrame:
    path = _get_filepath("youtube")
    return pd.read_parquet(path, engine="fastparquet")
