from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@db:5432/kantata_reddit"
    redis_url: str = "redis://redis:6379/0"
    app_env: str = "development"
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
