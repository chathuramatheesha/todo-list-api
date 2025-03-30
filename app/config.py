from pydantic_settings import BaseSettings, SettingsConfigDict


# Configuration class for environment variables and app settings
class BasicConfig(BaseSettings):
    SECRET_KEY: str | None = None  # Secret key for JWT encryption
    ALGORITHM: str | None = None  # Encryption algorithm used for JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Token expiration time in minutes
    DATABASE_URL: str | None = None  # URL for the database connection
    DATABASE_ECHO: bool = False  # Whether to log database queries for debugging
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore"
    )  # Read settings from .env file


# Create an instance of BasicConfig to access the settings
config = BasicConfig()
