"""core.py"""

# Standard Library Imports
from typing import Dict, Any
import logging

# Third Party Imports
import faust
from pydantic import ValidationError

# Local App Imports
from bce.bga_filtered_events_models.filtered import FilteredLogEvent
from bce.bga_filtered_event.services.play_card import process_play_card_event
from bce.bga_filtered_events_models.play_card import PlayCardArgs
from bce.surreal_connection_manager_lib import async_connect, SurrealConnection
from bce.kafka_env_settings import get_kafka_settings

KAFKA_SETTINGS = get_kafka_settings()


class SurrealDBManager:
    """Manages the connection and execution of queries against SurrealDB."""

    def __init__(self):
        logging.info("SurrealDB Manager initialized.")

    async def execute_atomic_update(self, query: str, params: Dict[str, Any]):
        """Executes the atomic 'check-then-act' query in SurrealDB."""
        logging.info(f"Executing Query: {query} with params: {params}")
        await asyncio.sleep(0.01)  # Simulate async I/O
        return {"status": "OK"}


db_manager = SurrealDBManager()

RELEVANT_MESSAGE_TYPES = {
    "tableInfosChanged",
    "newHand",
    "newRound",
    "playCard",
    "giveCards",
    "giveAllCardsToPlayer",
    "newScores",
    "tableWindow",
    "noSound",
}


class SurrealDbApp(faust.App):
    surreal_conn: SurrealConnection


app = SurrealDbApp(
    "hearts_stream_processor",
    broker=KAFKA_SETTINGS.bootstrap_servers,
    value_serializer="json",
)

# The topic now expects JSON messages representing a single FilteredLogEvent
filtered_logs_topic = app.topic(KAFKA_SETTINGS.subscribed_topic)


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
        app.surreal_conn = await async_connect()

    async def on_stop(self):
        """Close the database connection when the service stops.

        This method is automatically called by Faust when the worker stops,
        ensuring proper cleanup of database resources.

        Returns:
            None: This method doesn't return any value.
        """
        await app.surreal_conn.close()


@app.agent(filtered_logs_topic)
async def process_bga_filtered_event(events: faust.Stream[dict]):
    """Main Faust agent, now focused exclusively on processing 'playCard' events."""
    event_obj: dict
    async for event_obj in events:
        # Immediately filter out any event that is not 'playCard'. DEBUG
        try:
            if event_obj["type"] != "playCard":
                continue
        except KeyError as ke:
            logging.error(f"Unable to parse object: {ke}")
            logging.debug(event_obj.keys())

        if "game_id" not in event_obj:
            # Ignore old messages missing the added id DEBUG
            continue

        logging.debug(event_obj)

        try:
            event = FilteredLogEvent.model_validate(event_obj)
            play_card_args = event.get_parsed_args()

            if isinstance(play_card_args, PlayCardArgs):
                event_db_items = await process_play_card_event(live_surreal_conn, event, play_card_args)
            else:
                continue

            # check idempotency key

            atomic_query = f"""
                UPDATE live_game_state:{event.game_id}
                {event_db_items.event_query},
                processed_log_ids += $idempotency_key,
                last_updated = time::now()
                WHERE $idempotency_key NOT IN processed_log_ids;
            """
            logging.debug(event_db_items)
            logging.debug(atomic_query)

            await db_manager.execute_atomic_update(atomic_query, event_db_items.params)

        except ValidationError as e:
            logging.warning(f"Skipping malformed 'playCard' event {event_obj['uid']}: {e}")
        except Exception as e:
            logging.error(f"FATAL: Error processing event {event_obj['uid']}: {e}", exc_info=True)


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    meili_worker = faust.Worker(app, loop=loop, loglevel=logging.DEBUG)
    try:
        loop.run_until_complete(meili_worker.start())
    finally:
        meili_worker.stop_and_shutdown()
