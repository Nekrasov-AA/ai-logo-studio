from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://app:app@db:5432/appdb"

    class Config:
        env_file = ".env"  # на будущее; сейчас берём из переменной окружения

settings = Settings()
