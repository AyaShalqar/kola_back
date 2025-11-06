from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_EXPIRE_MIN: int
    REFRESH_EXPIRE_DAYS: int
    CORS_ORIGINS: list[str] | str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
