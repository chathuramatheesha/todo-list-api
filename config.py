from pydantic_settings import BaseSettings, SettingsConfigDict


class BasicConfig(BaseSettings):
    DATABASE_URL: str | None = None
    DATABASE_ECHO: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = BasicConfig()
