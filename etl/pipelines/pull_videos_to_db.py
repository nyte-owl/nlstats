from ..loaders import write_to_db
from ..datasources.youtube import pull_uploads_from_youtube
from ..processing.key_youtube_columns import clean_video_data, convert_games
from data import crud

from log import get_logger

logger = get_logger(__name__)


def execute():
    logger.info("--- PULL VIDEOS TO DB PIPELINE ---")
    collection_event = crud.collection_event.create_collection_event()

    logger.info(f"Started new collection event, ID={collection_event.id}")
    (
        pull_uploads_from_youtube()
        .pipe(
            write_to_db.write_latest_raw_youtube,
            collection_event_id=collection_event.id,
        )
        .pipe(clean_video_data)
        .pipe(convert_games)
        .pipe(
            write_to_db.write_latest_processed_youtube,
            collection_event_id=collection_event.id,
        )
    )

    logger.info("--- PIPELINE COMPLETE ---")
    crud.collection_event.update_collection_event_as_complete(
        collection_event_id=collection_event.id
    )
