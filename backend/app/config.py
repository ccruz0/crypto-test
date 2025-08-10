import os
from pydantic import BaseModel

class Settings(BaseModel):
    CRYPTO_API_KEY: str = os.getenv("CRYPTO_API_KEY", "")
    CRYPTO_API_SECRET: str = os.getenv("CRYPTO_API_SECRET", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    ENV: str = os.getenv("ENV", "local")

settings = Settings()
