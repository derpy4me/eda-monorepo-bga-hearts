"""core.py"""

# Standard Library Imports
from typing import TypeAlias
import logging

# Third Party Imports
from surrealdb import AsyncSurreal, AsyncWsSurrealConnection, AsyncHttpSurrealConnection

# Local App Imports
from bce.surreal_env_settings import get_surreal_settings

SurrealConnection: TypeAlias = AsyncWsSurrealConnection | AsyncHttpSurrealConnection


async def async_connect() -> SurrealConnection:
    """Asynchronous connection to SurrealdDB."""
    settings = get_surreal_settings()
    conn = AsyncSurreal(settings.url)
    try:
        await conn.signin(({"username": settings.user, "password": settings.password}))
        await conn.use(settings.namespace, settings.database)
        logging.info(f"Successfully connected to SurrealDB at {settings.url}")
        return conn
    except Exception as e:
        logging.fatal(f"Error connecting to SurrealDB: {e}")
        raise
