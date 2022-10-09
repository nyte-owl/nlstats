from ..loaders.write_local_file import write_latest_processed_youtube
from ..local_data.read_local_file import read_latest_raw_youtube
from ..processing.key_youtube_columns import clean_video_data, convert_games


def execute():
    (
        read_latest_raw_youtube()
        .pipe(clean_video_data)
        .pipe(convert_games)
        .pipe(write_latest_processed_youtube)
    )
