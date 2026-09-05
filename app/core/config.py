from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


    class Config:
        env_file = ".env"


settings = Settings()