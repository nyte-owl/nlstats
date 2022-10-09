from ..loaders.write_local_file import (
    write_latest_processed_youtube,
    write_latest_raw_youtube,
)
from ..datasources.youtube import pull_uploads_from_youtube
from ..processing.key_youtube_columns import clean_video_data, convert_games


def execute():
    (
        pull_uploads_from_youtube()
        .pipe(write_latest_raw_youtube)
        .pipe(clean_video_data)
        .pipe(convert_games)
        .pipe(write_latest_processed_youtube)
    )
