"""Environment variables for managing Kafka connection."""

from functools import lru_cache
from .core import KafkaSettings


@lru_cache()
def get_kafka_settings() -> KafkaSettings:
    return KafkaSettings()


__all__ = ["KafkaSettings", "get_kafka_settings"]
