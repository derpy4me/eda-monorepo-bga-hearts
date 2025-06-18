"""Faust worker for cleaning up old and invalid records in SurrealDB.

This module provides a scheduled task that runs periodically to clean up the SurrealDB
database by removing "dud" logs (those with empty original_message) and logs older
than 3 months to prevent database bloat and maintain performance.
"""

import faust

import pendulum
from surrealdb import RecordID
from uuid_utils.compat import uuid7


from bce.surrealdb_manager_lib.core import SurrealDBManager

app = faust.App(
    "bga_cleanup_worker",
    broker="dev-kafka-n1.strataops.com:9092,dev-kafka-n2.strataops.com:9092,dev-kafka-n3.strataops.com:9092",
)


@app.timer(interval=86400)  # Runs once every 24 hours (86400 seconds)
async def cleanup_job():
    """Performs scheduled cleanup of the SurrealDB database.

    This function runs as a scheduled task every 24 hours and performs two types of cleanup:
    1. Removes "dud" logs that have empty original_message fields
    2. Removes logs older than 3 months to prevent database bloat

    The function connects to the database using SurrealDBManager, identifies records
    to delete, and then performs the deletion operation if any records are found.

    Returns:
        None: This function doesn't return any value.
    """
    print("--- [Cleanup Worker] Starting scheduled cleanup job. ---")

    async with SurrealDBManager() as db_manager:
        all_ids_to_delete = []

        # Find and delete "dud" logs (empty original_message)
        print("Searching for dud logs (empty original_message)...")
        dud_logs_query = "select id from raw_logs where object::is_empty(original_message);"
        dud_records = await db_manager.query(dud_logs_query)
        dud_ids = [record["id"] for record in dud_records]
        if dud_ids:
            print(f"Found {len(dud_ids)} dud records to delete.")
            all_ids_to_delete.extend(dud_ids)
        else:
            print("No dud logs found.")

        print("Searching for logs older than 3 months...")
        cutoff_datetime = pendulum.now("UTC").subtract(days=90)

        # Generate a UUIDv7 that corresponds to the beginning of that time.
        cutoff_id = uuid7(cutoff_datetime.int_timestamp)
        unix_ms = cutoff_id.int >> 80
        unix_seconds = unix_ms / 1000
        print(f"Generated cutoff ID {cutoff_id} which corresponds to datetime: {pendulum.from_timestamp(unix_seconds)}")

        cutoff_record_id = RecordID("raw_logs", cutoff_id)
        old_logs_query = "SELECT id FROM raw_logs WHERE id < $cutoff_id;"
        old_records = await db_manager.query(old_logs_query, {"cutoff_id": cutoff_record_id})
        old_ids = [record["id"] for record in old_records]

        if old_ids:
            print(f"Found {len(old_ids)} records older than {cutoff_datetime.to_iso8601_string()} to delete.")
            all_ids_to_delete.extend(old_ids)
        else:
            print("No old logs found to delete.")

        if all_ids_to_delete:
            print(f"Total records to delete: {len(all_ids_to_delete)}")
            await db_manager.delete_records_by_ids(list(all_ids_to_delete))
        else:
            print("No records needed deletion in this run.")

    print("--- [Cleanup Worker] Cleanup job finished. ---")


if __name__ == "__main__":
    import asyncio
    import logging

    loop = asyncio.get_event_loop()
    meili_worker = faust.Worker(app, loop=loop, loglevel=logging.INFO)
    try:
        loop.run_until_complete(meili_worker.start())
    finally:
        meili_worker.stop_and_shutdown()
