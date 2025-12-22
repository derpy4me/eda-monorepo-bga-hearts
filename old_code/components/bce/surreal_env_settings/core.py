"""core.py"""

# Standard Library Imports

# Third Party Imports
from pydantic_settings import BaseSettings, SettingsConfigDict

# Local App Imports


class SurrealSettings(BaseSettings):
    """Environment variables for Surreal connection."""

    model_config = SettingsConfigDict(env_prefix="SURREAL_", env_file=".env", env_file_encoding="utf-8")

    url: str
    user: str = "root"
    password: str = "root"
    namespace: str = "bce"
    database: str = "kafka-raw-ingest"
