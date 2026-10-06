from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FitBuddy"
    app_version: str = "1.0.0"

    database_url: str = "sqlite:///./fitbuddy.db"

    gemini_api_key: str = ""

    # Keep these configurable through .env so model names can be changed
    # without modifying application code.
    gemini_pro_model: str = "gemini-3.1-pro-preview"
    gemini_flash_model: str = "gemini-3.8-flash"

    # Simple protection for the admin page.
    admin_key: str = ""

    # When True, FitBuddy works without a Gemini API key.
    # This is useful for testing the application locally.
    demo_mode: bool = True

    max_feedback_chars: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()