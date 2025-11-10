from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://app:app@db:5432/appdb"
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"

    S3_ENDPOINT_URL: str = "http://localstack:4566"
    AWS_REGION: str = "eu-central-1"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    S3_BUCKET: str = "ai-logo-studio"
    S3_PUBLIC_BASE: str = "http://localhost:4566"

    class Config:
        env_file = ".env"  # for future use; currently taking from environment variable

settings = Settings()
