"""core.py"""

# Standard Library Imports

# Third Party Imports
from aiokafka import AIOKafkaProducer
import orjson

# Local App Imports
from bce.kafka_env_settings import get_kafka_settings
from bce.surreal_connection_manager_lib import async_connect

kafka_settings = get_kafka_settings()
TOPIC = kafka_settings.subscribed_topic if kafka_settings.subscribed_topic else "bga-test-raw-dump"


async def main():
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_settings.bootstrap_servers,
        value_serializer=lambda v: orjson.dumps(v),
    )
    await producer.start()
    connection = await async_connect()
    try:
        last_record_id = None
        while True:
            inside_query = "WHERE id > $id" if last_record_id else ""
            query = f"SELECT * FROM raw_logs {inside_query} ORDER BY id LIMIT 1000"
            print(query)
            params = None
            if last_record_id:
                params = {"id": last_record_id}
            records = await connection.query(query, params)
            print(f"Received {len(records)} records...")
            if not records:
                print("No more records")
                break
            for record in records:
                record_copy = record.copy()
                record_id = record.get("id")
                str_id = str(record_id)
                record_copy["surreal_id"] = str_id
                del record_copy["id"]
                await producer.send(TOPIC, key=str_id.encode("UTF-8"), value=record_copy)
            print("Flushing producer...")
            await producer.flush()
            last_record_id = records[-1].get("id")
            if last_record_id is None:
                print("No id found in last record.")
                print(records[-1])
                break
            print(f"New last_record_id: {last_record_id}")
    finally:
        await producer.stop()
        await connection.close()
        print("Connections closed.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
