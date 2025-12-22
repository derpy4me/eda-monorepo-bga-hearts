"""live_game_state.py"""

# Standard Library Imports

# Third Party Imports
from surrealdb import RecordID

# Local App Imports
from bce.surreal_connection_manager_lib import SurrealConnection

TABLE_STATE_TABLE = "live_game_state"


async def get_live_game_state(db_conn: SurrealConnection, bga_table_id: str) -> dict:
    record_id = RecordID(TABLE_STATE_TABLE, bga_table_id)

    result = await db_conn.select(record_id)

    return result


async def save_live_game_state(db_conn: SurrealConnection, bga_table_id: str, state: dict) -> dict:
    record_id = RecordID(TABLE_STATE_TABLE, bga_table_id)
    updated_state_dict = await db_conn.update(record_id, state)

    return updated_state_dict
