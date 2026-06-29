from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    gemini_api_key: str = ""
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "vendoriq"
    chroma_persist_dir: str = "./chroma_db"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
