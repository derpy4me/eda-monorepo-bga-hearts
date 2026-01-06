import io
import json
import sys
import msgpack

from minio import Minio
from kafka import KafkaConsumer
import structlog


logger = structlog.get_logger(__name__)

topic = sys.argv[1]
logger.debug("Subscribing to topic...", topic=topic)
consumer = KafkaConsumer(
    topic,
    bootstrap_servers="kafka-test.strata.win:9092,kafka-test.strata.win:9093,kafka-test.strata.win:9094",
    value_deserializer=lambda v: msgpack.unpackb(v, raw=False),
)

minio_client = Minio(
    "localhost:9000",
    access_key="root",
    secret_key="password",
    secure=False,
)

bucket_name = f"{topic.lower()}-test7"
try:
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
except:
    logger.exception("Unable to create bucket")

for message in consumer:
    logger.info(message.value)

    message_bytes = json.dumps(message.value).encode("utf-8")
    object_name = f"{message.key.decode()}.json"

    message_stream = io.BytesIO(message_bytes)

    try:
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=message_stream,
            length=len(message_bytes),
            content_type="application/json",
        )
        logger.info("object added...", name=object_name, bucket=bucket_name)
    except:
        logger.exception()
