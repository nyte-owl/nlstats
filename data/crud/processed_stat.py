from typing import List

import pandas as pd
from pydantic import BaseModel
from sqlalchemy import select

from .. import crud
from ..database import get_session
from log import get_logger
from ..mappers import ProcessedStat, Video

logger = get_logger(__name__)


class CreateProcessedStat(BaseModel):
    video_id: str
    collection_event_id: int
    views: int
    likes: int
    comments: int
    ratio_likes_views: float
    ratio_comments_views: float


def create_processed_stats(new_items: List[CreateProcessedStat]):
    with get_session() as session:
        for data in new_items:
            db_item = ProcessedStat(**data.dict())
            logger.debug(f"Create row in DB: {db_item}")

            session.add(db_item)

        session.commit()


def get_most_recent_processed_stat_dataframe() -> pd.DataFrame:
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
        "Likes per 1000 Views": ProcessedStat.ratio_likes_views,
        "Comments per 1000 Views": ProcessedStat.ratio_comments_views,
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
