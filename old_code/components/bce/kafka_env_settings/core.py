"""core.py"""

# Standard Library Imports

# Third Party Imports
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Local App Imports


class KafkaSettings(BaseSettings):
    """Environment variables for Surreal connection."""

    model_config = SettingsConfigDict(env_prefix="KAFKA_", env_file=".env", env_file_encoding="utf-8")

    bootstrap_servers: str = Field(
        description="Comma separated list of servers to connect to in Kafka.",
        examples=["localhost:9092,127.0.0.1:9092"],
    )
    subscribed_topic: str | None = Field(None, description="Topic to connect to in Kafka")
