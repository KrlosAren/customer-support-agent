import os
from pathlib import Path


from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


class Settings(BaseSettings):
    app_name: str = "Awesome API"
    environment: str = "development"
    debug: bool = True
    faq_url: str
    openai_api_key: str
    db_path: str
    llm_model: str

    model_config = SettingsConfigDict(
        env_file=f'.env.{"development" if os.getenv("ENVIRONMENT") is None else os.getenv("ENVIRONMENT")}',
        env_file_encoding="utf-8",
    )


def get_settings() -> Settings:
    environment = os.getenv("ENVIRONMENT", "development")
    project_root = Path(__file__).resolve().parent.parent.parent
    dotenv_path = project_root / f".{environment}.env"
    if not dotenv_path.exists():
        raise FileNotFoundError(f"Environment file {dotenv_path} does not exist.")

    load_dotenv(dotenv_path=dotenv_path)
    return Settings()
