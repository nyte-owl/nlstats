from fire import Fire
from .pipelines import (
    process_raw_local_youtube_data,
    process_raw_local_to_db,
    pull_videos_to_local,
    pull_videos_to_db,
)
from data import crud

if __name__ == "__main__":
    Fire(
        {
            "pull": pull_videos_to_db.execute,
            "repull": process_raw_local_to_db.execute,
            "pull_local": pull_videos_to_local.execute,
            "process": process_raw_local_youtube_data.execute,
            "convert": crud.video.update_video_games,
        }
    )
