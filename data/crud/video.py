from datetime import datetime
from typing import List

from pydantic import BaseModel
from sqlalchemy import select, update

from .. import crud
from ..database import get_session
from log import get_logger
from ..mappers import Video

logger = get_logger(__name__)


class UpdateVideo(BaseModel):
    video_id: str
    title: str
    description: str
    game: str
    duration_seconds: int
    publish_date: datetime


def get_all_video_ids() -> List[str]:
    with get_session() as session:
        return session.execute(select(Video.unique_youtube_id)).scalars().all()


def get_video_by_id(video_id: str) -> Video | None:
    with get_session() as session:
        return session.execute(
            select(Video).filter_by(unique_youtube_id=video_id)
        ).scalar_one_or_none()


def create_video(unique_youtube_id: str):
    db_item = Video(unique_youtube_id=unique_youtube_id)
    logger.debug(f"Create row in DB: {db_item}")

    with get_session() as session:
        session.add(db_item)
        session.commit()


def update_video_data(updates: List[UpdateVideo]):
    with get_session() as session:
        for video_data in updates:
            db_item: Video = session.execute(
                select(Video).filter_by(unique_youtube_id=video_data.video_id)
            ).scalar_one()

            db_item.title = video_data.title
            db_item.description = video_data.description
            db_item.game = video_data.game
            db_item.duration_seconds = video_data.duration_seconds
            db_item.publish_date = video_data.publish_date
            logger.debug(f"Update row: {db_item}")

        session.commit()


def update_video_games():
    conversion_rules = crud.conversion_rule.read_all_conversion_rules()

    with get_session() as session:
        for conversion_rule in conversion_rules:
            matches = session.execute(
                select(Video).where(Video.game == conversion_rule.parsed_title)
            ).all()
            if matches and len(matches) != 0:
                logger.debug(
                    f"Updating {len(matches)} rows from "
                    f"`{conversion_rule.parsed_title}`"
                    f" to `{conversion_rule.final_title}`"
                )
                session.execute(
                    update(Video)
                    .where(Video.game == conversion_rule.parsed_title)
                    .values(game=conversion_rule.final_title)
                )
            else:
                logger.warn(
                    f"Couldn't change any videos with name "
                    f"{conversion_rule.parsed_title}"
                )

        session.commit()
