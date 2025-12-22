"""Settings for connections to surrealdb."""

from functools import lru_cache
from .core import SurrealSettings


@lru_cache()
def get_surreal_settings() -> SurrealSettings:
    return SurrealSettings()


__all__ = ["SurrealSettings", "get_surreal_settings"]
