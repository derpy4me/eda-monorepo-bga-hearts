"""idempotency_key.py"""

# Standard Library Imports

# Third Party Imports

# Local App Imports
from bce.surreal_connection_manager_lib import SurrealConnection

IDEMPOTENCY_TABLE = "idempotency_events"


async def check_idempotency_key_exists(surreal_conn: SurrealConnection, idempotency_key: str) -> bool:
    pass


async def add_idempotency_key(surreal_conn: SurrealConnection, idempotency_key: str, data: dict | None = None):
    pass


async def remove_idempotency_key(surreal_conn: SurrealConnection, idempotency_key: str):
    pass
