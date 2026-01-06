from collections.abc import Callable
from typing import Protocol, TypeVar
from playground.bridge_agent.domain.model import SensorReading

HandlerFunc = TypeVar("HandlerFunc", bound=Callable[..., None])


class EventPublisher(Protocol):
    async def publish_sensor_reading(self, reading: SensorReading, status: str) -> None:
        ...
