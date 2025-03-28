from pydantic_settings import BaseSettings, SettingsConfigDict


class BasicConfig(BaseSettings):
    SECRET_KEY: str | None = None
    ALGORITHM: str | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str | None = None
    DATABASE_ECHO: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = BasicConfig()
