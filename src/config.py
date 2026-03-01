from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TELEGRAM_TOKEN: SecretStr = Field(...)
    ETHSCAN_API_KEY: SecretStr | None = Field(None)
    CMC_API_KEY: SecretStr = Field("")
    hcpb_api_url: str | None = Field(None)
    hcpb_api_key: SecretStr | None = Field(None)
    LOGFIRE_TOKEN: SecretStr | None = Field(None)
    WEBHOOK_URL: str | None = Field(None)
    WEBHOOK_SECRET_TOKEN: SecretStr | None = Field(None)
    WEBHOOK_PORT: int = Field(8443)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
