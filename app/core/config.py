from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    secure_cookie: bool


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
        

settings = Settings()