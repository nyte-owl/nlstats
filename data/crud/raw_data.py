from typing import List

from pydantic import BaseModel

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
