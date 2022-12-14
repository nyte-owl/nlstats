from typing import List

import pandas as pd
from pydantic import BaseModel
from sqlalchemy import select

from log import get_logger
from .. import crud
from ..database import get_session
from ..mappers import CollectionEvent, ProcessedStat, Video


logger = get_logger(__name__)


class CreateProcessedStat(BaseModel):
    video_id: str
    collection_event_id: int
    views: int
    likes: int
    comments: int


def create_processed_stats(new_items: List[CreateProcessedStat]):
    with get_session() as session:
        for data in new_items:
            db_item = ProcessedStat(**data.dict())

            session.add(db_item)

        session.commit()


def get_most_recent_processed_stat_dataframe() -> pd.DataFrame:
    """
    Columns:
    - "id"
    - "Publish Date"
    - "Title"
    - "Description"
    - "Duration (Seconds)"
    - "Game"
    - "Likes"
    - "Views"
    - "Comments"
    """
    most_recent_collection_event = (
        crud.collection_event.get_most_recent_collection_event()
    )

    columns = {
        "id": Video.unique_youtube_id,
        "Publish Date": Video.publish_date,
        "Title": Video.title,
        "Description": Video.description,
        "Duration (Seconds)": Video.duration_seconds,
        "Game": Video.game,
        "Likes": ProcessedStat.likes,
        "Views": ProcessedStat.views,
        "Comments": ProcessedStat.comments,
    }
    query = (
        select(list(columns.values()))
        .where(ProcessedStat.collection_event_id == most_recent_collection_event.id)
        .join(ProcessedStat.video_info)
    )

    with get_session() as session:
        data = session.execute(query).all()

    return pd.DataFrame(
        data,
        columns=list(columns.keys()),
    )


def get_all_stats() -> pd.DataFrame:
    columns = {
        "id": Video.unique_youtube_id,
        "Publish Date": Video.publish_date,
        "Title": Video.title,
        "Description": Video.description,
        "Duration (Seconds)": Video.duration_seconds,
        "Game": Video.game,
        "Likes": ProcessedStat.likes,
        "Views": ProcessedStat.views,
        "Comments": ProcessedStat.comments,
        "Pull Date": CollectionEvent.pull_datetime,
        "Collection Event": CollectionEvent.id,
    }
    query = (
        select(list(columns.values()))
        .join(ProcessedStat.video_info)
        .join(ProcessedStat.collection_event)
    )

    with get_session() as session:
        data = session.execute(query).all()

    return pd.DataFrame(
        data,
        columns=list(columns.keys()),
    )
