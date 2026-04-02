import json
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    data_dir: str = "data/processed"
    sample_data_dir: str = "data/sample"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    """Return the data directory, falling back to sample if processed is empty."""
    processed = BASE_DIR / settings.data_dir
    sample = BASE_DIR / settings.sample_data_dir
    if processed.exists() and any(processed.glob("*.json")):
        return processed
    return sample


def load_json(filename: str) -> list | dict:
    """Load a JSON file from the active data directory."""
    path = get_data_dir() / filename
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)
