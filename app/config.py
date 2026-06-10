from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MODEL_PATH: str
    THRESHOLD: float
    MODEL_VERSION: str
    LOG_LEVEL: str = "INFO"
    REDIS_HOST : str
    REDIS_PORT: int = 6379
    API_USERNAME: str
    API_PASSWORD: str
    model_config = SettingsConfigDict(
        env_file="app/.env"
    )

settings = Settings() # type: ignore