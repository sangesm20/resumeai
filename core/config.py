from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str

    HF_TOKEN: str

    HF_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    DEFAULT_SIMILARITY_THRESHOLD: float = 0.30
    DEFAULT_TOP_K: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()