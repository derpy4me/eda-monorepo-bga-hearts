"""Process individual messages from a WebSocket connection."""

import orjson
import pendulum

from mitmproxy import http
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import structlog

logger = structlog.get_logger("__name__")


bootstrap_servers = (
    "dev-kafka-n1.mine.com:9092,dev-kafka-n2.mine.com:9092,dev-kafka-n3.mine.com:9092"
)

logger.debug("BGA Script starting...")

try:
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        # value_serializer=lambda v: msgpack.packb(v),
        value_serializer=lambda v: orjson.dumps(v),
    )
except NoBrokersAvailable:
    logger.error("No Kafka brokers available")
    producer = None


def process_webhook(
    topic: str,
    ws_message: dict,
    kafka_client: KafkaProducer | None = None,
):
    """
    Process a WebSocket message by sending it to Kafka or logging it.

    This function takes a WebSocket message, adds a timestamp, and either
    sends it to a Kafka topic (if a Kafka client is provided) or logs it
    (if no Kafka client is available).

    Args:
        topic (str): The Kafka topic to send the message to.
        ws_message (dict): The WebSocket message to process.
        kafka_client (KafkaProducer | None, optional): The Kafka producer client.
            If None, the message will be logged instead of sent to Kafka.
            Defaults to None.

    Returns:
        None
    """
    payload_to_send = {
        "capture_timestamp_utc": pendulum.now("UTC").isoformat(),
        "original_message": ws_message,
    }

    message_key = str(pendulum.now("UTC").timestamp()).encode("utf-8")

    if kafka_client:
        logger.info(
            f"Sending raw message to {topic}",
            key=message_key.decode("utf-8"),
        )
        kafka_client.send(topic, payload_to_send, key=message_key)
        kafka_client.flush()
    else:
        logger.info(
            "Raw WEBSOCKET message (Kafka producer is None)",
            topic=topic,
            key=message_key,
            payload=payload_to_send,
        )


def websocket_message(flow: http.HTTPFlow):
    """
    Process WebSocket messages from BoardGameArena.

    This function is called by mitmproxy when a WebSocket message is intercepted.
    It filters for messages from boardgamearena.com, extracts the message content,
    determines whether it's from the client or server, and processes each JSON
    message by sending it to Kafka.

    Args:
        flow (http.HTTPFlow): The HTTP flow containing WebSocket data.
            The flow must have a websocket attribute.

    Returns:
        None
    """
    assert flow.websocket is not None
    if "boardgamearena" not in flow.request.host:
        return
    logger.info(f"Receiving message from host: {flow.request.host}")

    # get the latest message
    ws_data = flow.websocket
    message = ws_data.messages[-1]
    if message.from_client:
        topic = "bga-logs-client-raw"
        logger.debug("Client sent a message...")
    else:
        topic = "bga-logs-server-raw"
        logger.debug("Server sent a message...")

    logger.debug("Original Message", original_message=message.content)
    json_messages = [orjson.loads(message) for message in message.content.splitlines()]
    logger.debug("Decoded Messages", decoded_message=json_messages)
    for json_message in json_messages:
        process_webhook(topic, json_message, producer)
