from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TELEGRAM_TOKEN: SecretStr = Field(...)
    ETHSCAN_API_KEY: SecretStr | None = Field(None)
    CMC_API_KEY: SecretStr = Field("")
    API_URL: str | None = Field(None)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
