from playground.bridge_agent.domain.model import SensorReading
from playground.bridge_agent.ports.repository import EventPublisher


async def process_sensor_reading(msg: dict, publisher: EventPublisher):
    reading = SensorReading(**msg)
    status = reading.determine_status()
    await publisher.publish_sensor_reading(reading, status)
