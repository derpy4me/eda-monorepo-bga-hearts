"""filtered.py"""

# Standard Library Imports
from typing import Any

# Third Party Imports
from pydantic import BaseModel, Field

# Local App Imports
from .play_card import PlayCardArgs


class FilteredLogEvent(BaseModel):
    """Represents a generic event from Kafka. We will validate its type and then attempt to parse its 'args' into a specific model."""

    game_id: str
    log_id: str = Field(..., alias="uid")
    event_type: str = Field(..., alias="type")
    args: dict[str, Any]

    def get_parsed_args(self) -> BaseModel | None:
        match self.event_type:
            case "giveAllCardsToPlayer":
                return None
            case "giveCards":
                return None
            case "newRound":
                return None
            case "newScores":
                return None
            case "noSound":
                return None
            case "playCard":
                return PlayCardArgs.model_validate(self.args)
            case "newHand":
                return None
            case "tableInfosChanged":
                return None
            case "tableWindow":
                return None
            case _:
                return None


class EventDbItems(BaseModel):
    params: dict
    event_query: str
    idempotency_key: str
