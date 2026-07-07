from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---- BRANDING - single source of truth ----
    APP_NAME: str = "GuardianGate"
    APP_TAGLINE: str = "Keeping every learner safe."
    BRAND_COLOR: str = "#2E9E43"

    # ---- Database ----
    DATABASE_URL: str = ""

    # ---- Security / auth ----
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ---- App ----
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()