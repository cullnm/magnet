from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global application settings.
    """

    BITTENSOR_NETWORK: str = "finney"
    BITTENSOR_ARCHIEVE_ENDPOINT: Optional[str] = None
    DATABASE_URL: str = (
        "postgresql+psycopg2://magnet_user:magnet_pass@localhost:5432/magnet_mining"
    )

    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()