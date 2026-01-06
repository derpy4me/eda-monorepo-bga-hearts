from faststream.redis import RedisBroker
from playground.bridge_agent.domain.model import SensorReading
from playground.bridge_agent.ports.repository import EventPublisher


class RedisPublisher(EventPublisher):
    def __init__(self, broker: RedisBroker, topic_name: str) -> None:
        self.broker = broker
        self.topic_name = topic_name

    async def publish_sensor_reading(self, reading: SensorReading, status: str) -> None:
        payload = {
            "id": reading.sensor_id,
            "val": reading.normalize(),
            "stat": status
        }
        await self.broker.publish(payload, self.topic_name)
