from sqlalchemy import select

from ..database import get_session
from log import get_logger
from ..mappers import CollectionEvent

logger = get_logger(__name__)


def create_collection_event() -> CollectionEvent:
    db_item = CollectionEvent()
    logger.debug(f"Request to create row in DB: {db_item}")

    with get_session() as session:
        session.add(db_item)
        session.commit()
        session.refresh(db_item)

    logger.debug(f"Created db item: {db_item}")
    return db_item


def update_collection_event_as_complete(collection_event_id: int):
    with get_session() as session:
        db_item: CollectionEvent = session.execute(
            select(CollectionEvent).filter_by(id=collection_event_id)
        ).scalar_one()

        db_item.complete = True
        logger.debug(f"Updated as complete: {db_item}")

        session.commit()


def get_most_recent_collection_event() -> CollectionEvent:
    query = (
        select(CollectionEvent)
        .where(CollectionEvent.complete == True)
        .order_by(CollectionEvent.pull_datetime.desc())
    )

    with get_session() as session:
        return session.execute(query).scalars().first()
