import json
from collections import Counter, defaultdict
from typing import Any, Dict, List, Union, Tuple


def load_jsonl_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Loads data from a JSONL-like file.
    Each line can be a single JSON object or a JSON array of objects.
    All successfully parsed dictionaries are collected into a single list.
    """
    all_individual_objects: List[Dict[str, Any]] = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                try:
                    # Attempt to parse the line as JSON
                    parsed_json_entity: Union[Dict[str, Any], List[Any]] = json.loads(line)

                    if isinstance(parsed_json_entity, list):
                        # If the line is a JSON array, process each item
                        for item_index, item in enumerate(parsed_json_entity):
                            if isinstance(item, dict):
                                all_individual_objects.append(item)
                            else:
                                print(
                                    f"Warning: Item {item_index} in array on line {i+1} is not a dictionary: {type(item)}"
                                )
                    elif isinstance(parsed_json_entity, dict):
                        # If the line is a single JSON object
                        all_individual_objects.append(parsed_json_entity)
                    else:
                        print(
                            f"Warning: Parsed data on line {i+1} is neither a dictionary nor a list: {type(parsed_json_entity)}"
                        )
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON on line {i+1}: {e}")
                    print(f"Problematic line content snippet: {line[:200]}...")
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return all_individual_objects


def get_value_type_summary(value: Any) -> str:
    """Returns a string representation of the value's type, summarizing collections."""
    if isinstance(value, dict):
        return "dict"
    elif isinstance(value, list):
        if not value:
            return "list (empty)"
        # Get type of the first element if list is not empty and all elements are similar
        first_item_type = type(value[0]).__name__
        if all(type(item).__name__ == first_item_type for item in value):
            return f"list of {first_item_type}"
        return "list (mixed types)"
    return type(value).__name__


def analyze_object_structure(obj: Dict[str, Any], depth: int = 0, max_depth: int = 2) -> Dict[str, Any]:
    """
    Analyzes the structure of a single dictionary, showing keys and value types.
    """
    if depth > max_depth:
        return {"...": "max depth reached"}

    structure = {}
    for key, value in obj.items():
        type_summary = get_value_type_summary(value)
        structure[key] = type_summary
        if type_summary == "dict" and depth < max_depth:
            structure[key] = {"type": "dict", "nested_structure": analyze_object_structure(value, depth + 1, max_depth)}
        elif type_summary.startswith("list of dict") and value and isinstance(value[0], dict) and depth < max_depth:
            # Analyze the structure of the first dictionary in the list
            structure[key] = {
                "type": type_summary,
                "list_item_structure": analyze_object_structure(value[0], depth + 1, max_depth),
            }
    return structure


def get_top_level_keys_summary(objects: List[Dict[str, Any]]) -> Counter:
    """Counts occurrences of top-level keys across all loaded objects."""
    top_level_keys = Counter()
    for obj in objects:
        if isinstance(obj, dict):
            for key in obj.keys():
                top_level_keys[key] += 1
    return top_level_keys


def get_push_event_types_summary(objects: List[Dict[str, Any]]) -> Tuple[Counter, Dict[str, Counter]]:
    """
    Summarizes event types found in "push" messages and counts keys in their 'args'.
    """
    event_type_counts = Counter()
    # Stores: event_type -> Counter of (arg_key -> count)
    event_args_key_counts_by_type: Dict[str, Counter] = defaultdict(Counter)

    for obj in objects:
        if not (isinstance(obj, dict) and obj.get("push")):
            continue

        push_content = obj["push"]
        if not (isinstance(push_content, dict) and push_content.get("pub")):
            continue

        pub_content = push_content["pub"]
        if not (isinstance(pub_content, dict) and pub_content.get("data")):
            continue

        pub_data_content = pub_content["data"]
        if not (isinstance(pub_data_content, dict) and isinstance(pub_data_content.get("data"), list)):
            continue

        events_list = pub_data_content["data"]
        for event in events_list:
            if isinstance(event, dict) and isinstance(event.get("type"), str):
                event_type = event["type"]
                event_type_counts[event_type] += 1

                event_args = event.get("args")
                if isinstance(event_args, dict):
                    for arg_key in event_args.keys():
                        event_args_key_counts_by_type[event_type][arg_key] += 1

    return event_type_counts, dict(event_args_key_counts_by_type)


if __name__ == "__main__":
    file_path = "/home/tscott/.bga-logs/extracted_bga_messages.jsonl"
    all_data = load_jsonl_data(file_path)

    if not all_data:
        print("No data was loaded. Please check the file path and content.")
    else:
        print(f"Successfully loaded {len(all_data)} individual JSON objects from the file.\n")

        print("--- Top-Level Keys Summary (across all objects) ---")
        top_keys = get_top_level_keys_summary(all_data)
        if top_keys:
            for key, count in top_keys.most_common():
                print(f'- "{key}": {count} occurrences')
        else:
            print("No top-level keys found (or no objects loaded).")
        print("\n" + "=" * 50 + "\n")

        print("--- Structure of First Few Objects (Sample) ---")
        for i, item in enumerate(all_data[: min(5, len(all_data))]):  # Analyze first 5 or fewer
            print(f"Object {i+1} Structure:")
            structure = analyze_object_structure(item, max_depth=1)  # Keep max_depth low for overview
            for k, v_type_info in structure.items():
                if isinstance(v_type_info, dict) and "type" in v_type_info:  # Nested structure
                    print(f"  - \"{k}\": {v_type_info['type']}")
                    if "nested_structure" in v_type_info:
                        for nk, nv_type in v_type_info["nested_structure"].items():
                            print(f'    - "{nk}": {nv_type}')
                    elif "list_item_structure" in v_type_info:
                        print(f"    (List item structure):")
                        for nk, nv_type in v_type_info["list_item_structure"].items():
                            print(f'      - "{nk}": {nv_type}')
                else:  # Simple type
                    print(f'  - "{k}": {v_type_info}')
            print("-" * 20)
        print("\n" + "=" * 50 + "\n")

        print('--- "Push" Message Event Types Summary ---')
        push_event_types, push_event_args_summary = get_push_event_types_summary(all_data)
        if push_event_types:
            print("Most common event types within 'push.pub.data.data' (and their common 'args' keys):")
            for etype, count in push_event_types.most_common(15):  # Show top 15 event types
                print(f'\n- Event Type "{etype}": {count} occurrences')
                if etype in push_event_args_summary and push_event_args_summary[etype]:
                    print("  Common 'args' keys:")
                    for arg_key, arg_count in push_event_args_summary[etype].most_common(5):  # Top 5 args keys
                        print(f'    - "{arg_key}" (seen ~{arg_count} times in this event type)')
        else:
            print("No 'push' message event types found or 'push' structure not as expected.")
        print("\n" + "=" * 50 + "\n")

        print("--- Key Observations & Next Steps for Parsing/Processing ---")
        print(
            "1.  **Mixed Line Formats:** The file contains lines that are single JSON objects and lines that are JSON arrays. The `load_jsonl_data` function handles this by flattening arrays."
        )
        print("2.  **Dominant Structures:**")
        print(
            '    *   **Push Messages:** Objects with a top-level `"push"` key seem to be the most frequent. These contain game-related events under `push.pub.data.data` (a list).'
        )
        print(
            '        *   Each event in this list has a `"type"` (e.g., "playCard", "gameStateChange") which dictates the structure of its `"args"` field.'
        )
        print(
            '        *   Common keys within these events include `"uid"`, `"log"`, `"args"`, and sometimes `"h"` or `"lock_uuid"`.'
        )
        print(
            '    *   **Connection/Subscription Messages:** Other objects (like those with `"connect"`, `"subscribe"`, `"id"`, `"presence"` keys) relate to the WebSocket connection and channel subscriptions. These often appear grouped in arrays on a single line in your source log.'
        )
        print("3.  **Value Type Consistency:**")
        print(
            "    *   Pay attention to IDs (e.g., `player_id`, `active_player` in `gameStateChange` args, values in `reflexion.total`). Your sample data shows these can sometimes be numbers and sometimes strings. This is crucial for robust parsing; you might need to normalize them."
        )
        print(
            "4.  **Variable `args` Field:** The `args` dictionary within game events (`push.pub.data.data[i].args`) is highly variable based on the event `type`. You'll need to develop specific parsing logic for each event type you care about."
        )
        print("5.  **Keywords to Look For:**")
        print('    *   Top-level: `"push"`, `"connect"`, `"subscribe"`, `"id"`, `"presence"`.')
        print(
            '    *   Inside `push.pub.data`: `"packet_type"` (e.g., "sequence", "single"), `"channel"` (e.g., "/table/...", "/player/...").'
        )
        print('    *   Event `"type"` strings are key for dispatching parsing logic.')
        print("\n**To proceed with parsing and processing:**")
        print(
            "   a. **Filter by Top-Level Key:** Decide if you want to process 'push' messages, connection messages, or both."
        )
        print("   b. **For 'push' messages:** Iterate through the `data` list under `push.pub.data`.")
        print(
            "   c. **Dispatch on Event `type`:** For each event, use its `type` to call a specific handler function that knows how to parse the corresponding `args` structure."
        )
        print(
            "   d. **Handle Type Inconsistencies:** Implement logic to convert IDs or other fields to a consistent type (e.g., always treat `player_id` as a string)."
        )
        print(
            "   e. **Extract Specific Data:** Once you have the parsing logic for an event type, you can extract the specific fields you need from its `args`."
        )
