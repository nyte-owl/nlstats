from typing import List

from pydantic import BaseModel, BaseSettings


class GeneralSettings(BaseSettings):
    channel_id: str
    upload_playlist_id: str
    youtube_api_key: str

    db_username: str
    db_password: str
    db_host: str
    db_name: str

    start_date: str = "2019-06-01"

    heroku_app_name: str = "nlstats"
    heroku_oauth_token: str

    local_development: bool = False

    class Config:
        env_file = ".env"


settings = GeneralSettings()


class ConversionRuleSetGameByID(BaseModel):
    id: str
    final_game_title: str


class ConversionRuleSetGameByParsedGame(BaseModel):
    parsed_game_title: str
    final_game_title: str


class ConversionRules(BaseModel):
    by_id: List[ConversionRuleSetGameByID] = []
    by_parsed_game: List[ConversionRuleSetGameByParsedGame] = []
