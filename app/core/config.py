from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "Prank Call Analyzer"
    VERSION: str = "1.0.0"

    # LLM Configuration
    LLM_MODEL: str = "google-gla:gemini-2.0-flash"
    LLM_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
