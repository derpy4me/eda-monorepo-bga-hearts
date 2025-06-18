"""Board Game Arena (BGA) Log Filter Module.

This module provides functionality to filter and extract relevant game events
from Board Game Arena log files or individual log messages. It's designed to
work with both file-based logs and message-by-message processing (e.g., from Kafka).

The module identifies strategically important game events based on predefined
message types and extracts them for further analysis.
"""

# Standard Library Imports
import json
import re
from typing import List, Dict, Any, Set, Generator

# Third Party Imports

# Local App Imports


class BgaLogFilter:
    """Filters Board Game Arena (BGA) log files or individual log messages.

    This class provides methods to extract and filter strategically relevant
    game events from BGA logs. It can process both complete log files and
    individual log messages (e.g., from a Kafka stream).

    The filter identifies events based on a predefined set of relevant message
    types that are important for game analysis and strategy.
    """

    RELEVANT_TYPES: Set[str] = {
        "tableInfosChanged",
        "newHand",
        "newRound",
        "gameStateChange",
        "playCard",
        "giveCards",
        "takeCards",
        "giveAllCardsToPlayer",
        "gameStateChangePrivateArg",
        "newScores",
        "tableWindow",
        "noSound",
    }

    def extract_events_from_log(self, log_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extracts the list of individual event objects from a raw log message.

        BGA logs often nest the actual events inside a 'data' array. This method
        navigates the nested structure to find and extract the relevant event data.

        Args:
            log_obj: A dictionary representing a parsed JSON log message.
                     This is typically the raw message received from Kafka or read from a log file.

        Returns:
            A list of event dictionaries extracted from the log message.
            Returns an empty list if no events are found or if the structure is unexpected.
        """
        # The core data is usually in push->pub->data->data
        try:
            events = log_obj.get("push", {}).get("pub", {}).get("data", {}).get("data", [])
            if isinstance(events, list):
                return events
        except AttributeError:
            # The object doesn't have the expected nested structure.
            return []

        # Some simpler messages might have data at the top level
        if "data" in log_obj and isinstance(log_obj["data"], list):
            return log_obj["data"]

        return []

    def filter_message(self, log_message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filters a single, parsed BGA log message to extract relevant events.

        This method extracts events from the log message and filters them based on
        the predefined set of relevant message types (RELEVANT_TYPES).

        Args:
            log_message: A dictionary representing a single JSON log message,
                         typically from a Kafka stream or parsed from a log file.

        Returns:
            A list of relevant event dictionaries found within the message.
            Returns an empty list if no relevant events are found.

        Example:
            >>> filter = BgaLogFilter()
            >>> events = filter.filter_message(kafka_message)
            >>> for event in events:
            ...     process_event(event)
        """
        relevant_events = []
        all_events = self.extract_events_from_log(log_message)
        for event in all_events:
            if event.get("type") in self.RELEVANT_TYPES:
                relevant_events.append(event)
        return relevant_events

    def _stream_from_file(self, file_path: str) -> Generator[Dict[str, Any], None, None]:
        """Reads a BGA log file and yields each raw message object as a generator.

        This method is primarily for testing and validation with full log files.
        It handles the parsing of potentially complex JSON structures in the log file,
        including error recovery for malformed JSON.

        Args:
            file_path: The path to the BGA log file to read.

        Yields:
            Dictionary objects representing individual log messages from the file.

        Note:
            This is an internal method as indicated by the leading underscore.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        cleaned_content = re.sub(r"\[source: \d+]\s*", "", content)

        decoder = json.JSONDecoder()
        pos = 0
        while pos < len(cleaned_content):
            if not cleaned_content[pos].strip():
                pos += 1
                continue

            try:
                obj, end_pos = decoder.raw_decode(cleaned_content, pos)
                log_list = obj if isinstance(obj, list) else [obj]
                for log_item in log_list:
                    yield log_item
                pos = end_pos
            except json.JSONDecodeError:
                # Find the next potential start of a JSON object/array
                next_obj_start = min(
                    filter(lambda i: i != -1, [cleaned_content.find("{", pos + 1), cleaned_content.find("[", pos + 1)]),
                    default=-1,
                )
                if next_obj_start == -1:
                    break
                pos = next_obj_start

    def filter_log_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Reads a BGA log file and filters all messages to extract relevant events.

        This method processes an entire log file, extracting and filtering relevant
        game events. It uses the message-based filter (`filter_message`) internally
        for consistent filtering logic across both file and message-based processing.

        Args:
            file_path: The path to the BGA log file to process.

        Returns:
            A list containing all relevant log events extracted from the entire file.
            Returns an empty list if no relevant events are found or if the file is empty.

        Example:
            >>> filter = BgaLogFilter()
            >>> events = filter.filter_log_file("game_logs.jsonl")
            >>> print(f"Found {len(events)} relevant game events")
        """
        all_relevant_logs = []
        for message in self._stream_from_file(file_path):
            all_relevant_logs.extend(self.filter_message(message))
        return all_relevant_logs


if __name__ == "__main__":
    bga_filter = BgaLogFilter()
    log_file = "extracted_bga_messages.jsonl"

    print("--- Simulating Kafka Consumer (Message-by-Message Filtering) ---")

    # In a real consumer, you'd get 'raw_message' from Kafka.
    # Here, we simulate it by reading from the file.
    filtered_from_stream: List[Dict[str, Any]] = []
    raw_message_count = 0
    for raw_message in bga_filter._stream_from_file(log_file):
        raw_message_count += 1
        # This is the line your consumer would run for each message:
        relevant_events = bga_filter.filter_message(raw_message)

        if relevant_events:
            filtered_from_stream.extend(relevant_events)

    print(f"Processed {raw_message_count} raw top-level messages.")
    print(f"Found {len(filtered_from_stream)} relevant events.")
    print("-" * 30)

    print("\n--- Verifying with Full File-Based Filtering ---")

    # This uses the original file-based method for comparison.
    filtered_from_file = bga_filter.filter_log_file(log_file)
    print(f"Found {len(filtered_from_file)} relevant events using the file method.")

    # Verification
    assert len(filtered_from_stream) == len(filtered_from_file), "Mismatch between methods!"
    print("Verification successful: Both methods yield the same number of events.")
    print("-" * 30)

    print("\nExample of the first 3 relevant logs:")
    for log in filtered_from_stream[:3]:
        print(json.dumps(log, indent=2))
