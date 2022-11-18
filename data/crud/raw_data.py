from typing import List

import pandas as pd
from pydantic import BaseModel
from sqlalchemy import select

from .. import crud
from ..database import get_session
from log import get_logger
from ..mappers import RawData

logger = get_logger(__name__)


class CreateRawData(BaseModel):
    video_id: str
    collection_event_id: int
    kind: str
    etag: str
    snippet: str
    content_details: str
    statistics: str


def create_raw_video_data(new_items: List[CreateRawData]):
    with get_session() as session:
        for i, raw_data in enumerate(new_items):
            db_item = RawData(**raw_data.dict())
            if i % 100 == 0:
                logger.info(f"Adding raw data #{i} of {len(new_items)}")
            # logger.debug(f"Create row in DB: {db_item}")

            session.add(db_item)

        session.commit()


def get_raw_dataframe_from_collection_event(event_id: int) -> pd.DataFrame:
    columns = {
        "id": RawData.id,
        "video_id": RawData.video_id,
        "collection_event_id": RawData.collection_event_id,
        "kind": RawData.kind,
        "etag": RawData.etag,
        "snippet": RawData.snippet,
        "content_details": RawData.content_details,
        "statistics": RawData.statistics,
    }

    query = select(list(columns.values())).where(
        RawData.collection_event_id == event_id
    )

    with get_session() as session:
        data = session.execute(query).all()

    return pd.DataFrame(
        data,
        columns=list(columns.keys()),
    )


def get_most_recent_raw_dataframe() -> pd.DataFrame:
    """
    Columns:
    - "id"
    - "video_id"
    - "collection_event_id"
    - "kind"
    - "etag"
    - "snippet"
    - "content_details"
    - "statistics"
    """
    most_recent_collection_event = (
        crud.collection_event.get_most_recent_collection_event()
    )

    logger.info(
        f"Retrieving raw data from collection event {most_recent_collection_event.id}"
    )
    return get_raw_dataframe_from_collection_event(most_recent_collection_event.id)
