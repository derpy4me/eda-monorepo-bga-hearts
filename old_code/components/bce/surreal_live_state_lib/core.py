"""core.py"""

# Standard Library Imports

# Third Party Imports
from surrealdb import RecordID

# Local App Imports
from cachetools_async import cached
from bce.surreal_connection_manager_lib import SurrealConnection


CARD_TABLE = "card"


async def get_card_data(db_conn: SurrealConnection) -> list[dict]:
    results = await db_conn.select(CARD_TABLE)

    return results


@cached(cache={})
async def get_card_by_type_and_value(db_conn: SurrealConnection, suite_id: int, value: int) -> dict | None:
    result = await db_conn.query(
        "SELECT * FROM ONLY card WHERE suite_id = $suite_id AND value = $value", {"suite_id": suite_id, "value": value}
    )

    return result
