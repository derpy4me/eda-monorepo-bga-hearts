"""play_card.py"""

# Standard Library Imports
from typing import Annotated

# Third Party Imports
from pydantic import BaseModel, Field, BeforeValidator

# Local App Imports


class CardDetails(BaseModel):
    """Specifies the structure of the 'card' object within the args."""

    id: int = Field(..., alias="id")
    suite_id: int = Field(..., alias="type")
    value: int = Field(..., alias="type_arg")
    card_id: str | None = None


class PlayCardArgs(BaseModel):
    """A specific model for the 'args' of a 'playCard' event. This ensures we only parse events that have the required data."""

    player_id: Annotated[str, BeforeValidator(lambda s: str(s))]
    player_name: str
    card: CardDetails
