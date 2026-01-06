from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream.redis import RedisBroker

from playground.bridge_agent.adapters.redis_repo import RedisPublisher
from .services import ingestion
from .settings import get_settings

settings = get_settings()

rabbit_broker: RabbitBroker = RabbitBroker(settings.amqp_broker.encoded_string())
redis_broker: RedisBroker = RedisBroker(settings.redis_broker.encoded_string())

app = FastStream(rabbit_broker)


@app.on_startup
async def on_start():
    await redis_broker.start()


@app.on_shutdown
async def on_shutdown():
    await redis_broker.stop()


@rabbit_broker.subscriber("in-topic")
async def handler(msg: dict):
    redis_publisher = RedisPublisher(redis_broker, "out-topic")
    await ingestion.process_sensor_reading(msg, redis_publisher)


if __name__ == '__main__':
    import asyncio

    asyncio.run(app.run())
