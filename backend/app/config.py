import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "PVCPilot AI"
    DEBUG: bool = True
    SECRET_KEY: str = "8afb6de37397b91d9b3a3250b86a8775"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "pvcpilot_db"

    REDIS_URL: str = "redis://localhost:6379/0"

    GEMINI_API_KEY: str = "YOUR_GEMINI_API_KEY"

    MAIL_USERNAME: str = "noreply@pvcpilot.com"
    MAIL_PASSWORD: str = "dummy_password"
    MAIL_FROM: str = "noreply@pvcpilot.com"
    MAIL_SERVER: str = "localhost"
    MAIL_PORT: int = 1025

    TWILIO_ACCOUNT_SID: str = "dummy_sid"
    TWILIO_AUTH_TOKEN: str = "dummy_token"
    TWILIO_PHONE_NUMBER: str = "+1234567890"

    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    @property
    def parsed_origins(self) -> List[str]:
        if not self.ALLOWED_ORIGINS:
            return []
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
