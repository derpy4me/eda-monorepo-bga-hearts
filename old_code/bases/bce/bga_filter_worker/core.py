"""Faust worker application that processes raw Board Game Arena (BGA) logs from a Kafka topic.

This worker acts as a bridge between the raw BGA logs collection system and downstream consumers
that need only the relevant game events for analysis or processing.
"""

import faust

from bce.kafka_raw_logs_filter.core import BgaLogFilter

app = faust.App(
    "bga-logs-filter-worker",
    broker="dev-kafka-n1.strataops.com:9092,dev-kafka-n2.strataops.com:9092,dev-kafka-n3.strataops.com:9092",
    value_serializer="json",
)

raw_logs_topic = app.topic("bga-logs-server-raw")
filtered_logs_topic = app.topic("bga-logs-server-filtered")

bga_filter = BgaLogFilter()


@app.agent(raw_logs_topic)
async def process_raw_log(messages):
    """Faust agent that processes raw BGA log messages from the Kafka topic.

    This agent:
    1. Extracts the BGA log message from the 'original_message' field
    2. Filters the message for strategically relevant events using BgaLogFilter
    3. Publishes relevant events to the filtered logs topic
    4. Logs information about processed and discarded messages

    Args:
        messages (faust.StreamT): Stream of messages from the raw logs Kafka topic.

    Returns:
        None: This function doesn't return any value, it processes the stream continuously.
    """
    async for message in messages:
        # The actual BGA log we want to process is nested inside the 'original_message' key.
        bga_log_message = message.get("original_message")

        if not isinstance(bga_log_message, dict) or not bga_log_message:
            print("--- Discarded Message (missing or invalid 'original_message' field) ---")
            continue

        relevant_events = bga_filter.filter_message(bga_log_message)

        if relevant_events:
            print(
                f"--- Producing {len(relevant_events)} relevant event(s) to '{filtered_logs_topic.get_topic_name()}' ---"
            )
            for event in relevant_events:
                print(f"  -> Sending event type: {event.get('type')}")
                await filtered_logs_topic.send(value=event)
        else:
            # We extract event types from the nested message for accurate logging.
            original_events = bga_filter.extract_events_from_log(bga_log_message)
            original_types = [event.get("type", "unknown") for event in original_events]

            if original_types:
                print(f"--- Discarded Message (contained irrelevant types: {original_types}) ---")
            else:
                # This case handles messages that didn't contain an event array, like 'connect' or 'join'.
                message_type = "N/A"
                if "connect" in bga_log_message:
                    message_type = "connect"
                elif "subscribe" in bga_log_message:
                    message_type = "subscribe"
                elif "push" in bga_log_message and "join" in bga_log_message["push"]:
                    message_type = "join"

                print(f"--- Discarded Message (non-event type: {message_type}) ---")


if __name__ == "__main__":
    import asyncio
    import logging

    loop = asyncio.get_event_loop()
    meili_worker = faust.Worker(app, loop=loop, loglevel=logging.INFO)
    try:
        loop.run_until_complete(meili_worker.start())
    finally:
        meili_worker.stop_and_shutdown()
