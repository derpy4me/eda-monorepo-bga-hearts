"""Faust worker for ingesting raw BGA logs from Kafka and archiving them to SurrealDB.

This module provides functionality to consume messages from a Kafka topic containing
raw BGA logs and store them in a SurrealDB database for further processing and analysis.
"""

import faust
from bce.surrealdb_manager_lib.core import SurrealDBManager

app = faust.App(
    "bga_raw_ingest_worker",
    broker="dev-kafka-n1.strataops.com:9092,dev-kafka-n2.strataops.com:9092,dev-kafka-n3.strataops.com:9092",
    value_serializer="json",
)

raw_logs_topic = app.topic("bga-logs-server-raw")

db_manager = SurrealDBManager()


@app.service
class DbService(faust.Service):
    """Service for managing database connections in the Faust worker.

    This service handles the lifecycle of the SurrealDB connection,
    ensuring proper connection establishment at startup and
    clean disconnection during shutdown.
    """

    async def on_start(self):
        """Initialize the database connection when the service starts.

        This method is automatically called by Faust when the worker starts.

        Returns:
            None: This method doesn't return any value.
        """
        await db_manager.connect()

    async def on_stop(self):
        """Close the database connection when the service stops.

        This method is automatically called by Faust when the worker stops,
        ensuring proper cleanup of database resources.

        Returns:
            None: This method doesn't return any value.
        """
        await db_manager.close()


@app.agent(raw_logs_topic)
async def archive_raw_log(messages):
    """Process and archive raw log messages from the Kafka topic.

    This function is a Faust agent that consumes messages from the raw logs topic
    and archives them to SurrealDB. It tracks the number of processed messages
    and periodically logs progress.

    Args:
        messages (faust.StreamT): An asynchronous stream of messages from the Kafka topic.

    Returns:
        None: This function doesn't return any value, it processes the stream continuously.
    """
    num_messages = 0
    async for message in messages:
        # Skip message if already present in database.
        surreal_id = message.get("surreal_id")
        if surreal_id:
            continue

        result = await db_manager.archive_raw_log(message)

        if "error" in result:
            print(f"Failed to archive message. Error: {result['error']}")
            continue

        num_messages += 1
        if num_messages % 100 == 0:
            print(f"Added {num_messages} logs to db so far...")


if __name__ == "__main__":
    import asyncio
    import logging

    loop = asyncio.get_event_loop()
    meili_worker = faust.Worker(app, loop=loop, loglevel=logging.INFO)
    try:
        loop.run_until_complete(meili_worker.start())
    finally:
        meili_worker.stop_and_shutdown()
