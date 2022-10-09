from ..loaders import write_local_file, write_to_db
from ..local_data.read_local_file import read_latest_raw_youtube
from ..processing.key_youtube_columns import clean_video_data, convert_games
from data import crud


def execute(collection_event_id: int):
    (
        read_latest_raw_youtube()
        .pipe(
            write_to_db.write_latest_raw_youtube,
            collection_event_id=collection_event_id,
        )
        .pipe(clean_video_data)
        .pipe(convert_games)
        .pipe(write_local_file.write_latest_processed_youtube)
        .pipe(
            write_to_db.write_latest_processed_youtube,
            collection_event_id=collection_event_id,
        )
    )

    crud.collection_event.update_collection_event_as_complete(
        collection_event_id=collection_event_id
    )
