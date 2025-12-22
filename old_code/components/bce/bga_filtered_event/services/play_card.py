"""play_card.py"""

# Standard Library Imports
import logging

# Third Party Imports

# Local App Imports
from bce.bga_filtered_events_models.filtered import FilteredLogEvent
from bce.bga_filtered_events_models.play_card import PlayCardArgs
from bce.surreal_connection_manager_lib import SurrealConnection
from bce.surreal_live_state_lib.core import get_card_by_type_and_value
from bce.bga_filtered_events_models.filtered import EventDbItems


async def generate_play_card_idempotency_key(
    db_conn: SurrealConnection, event: FilteredLogEvent, play_card_args: PlayCardArgs
) -> str | None:
    """Generates a deterministic, composite key for a playCard event."""
    card = await get_card_by_type_and_value(db_conn, play_card_args.card.suite_id, play_card_args.card.value)
    if not card:
        logging.error(
            f"Unable to find card matching suite: {play_card_args.card.suite_id} and value: {play_card_args.card.value}"
        )
        # TODO: Update to raise error instead
        return None
    return f"{event.game_id}|{event.event_type}|{play_card_args.player_id}|{card['id']}"


def build_play_card_update_query() -> str:
    """Returns the SET part of the SurrealQL query for a playCard event."""
    return """
        SET current_trick += {
                card_id: card:$card_id,
                player_id: $player_id
            },
            played_cards += card:$card_id
    """


async def process_play_card_event(
    surreal_conn: SurrealConnection, event: FilteredLogEvent, play_card_args: PlayCardArgs
) -> EventDbItems:
    # get idempotency key
    idempotency_key = await generate_play_card_idempotency_key(surreal_conn, event, play_card_args)
    # update the database with played card
    card_query = build_play_card_update_query()
    params = {
        "idempotency_key": idempotency_key,
        "player_id": play_card_args.player_id,
        "card_id": play_card_args.card.card_id,
        "player_name": play_card_args.player_name,
    }
    logging.info(f"Processing playCard key: {idempotency_key}")
    logging.debug(f"key: {idempotency_key}; params: {params}")

    return EventDbItems(params=params, event_query=card_query, idempotency_key=idempotency_key)


##############
# Idempotency log structure
# id: uuid7 pk idx
# idempotency_key: str idx
# obj containing destructured idempotency key and any relevant items: Event store?
##############
