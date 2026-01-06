import json


def extract_card_data(jsonl_file_path, output_json_path):
    """
    Extracts card IDs, suits (type), and values (type_arg) from a JSONL file
    containing BGA game messages and saves them to a JSON file.

    Args:
        jsonl_file_path (str): Path to the input JSONL file.
        output_json_path (str): Path to save the output JSON file.
    """
    all_cards_info = {}

    try:
        with open(jsonl_file_path, "r", encoding="utf-8") as f_in:
            for line_number, line in enumerate(f_in, 1):
                try:
                    # Each line can be a JSON object or a JSON array containing objects
                    parsed_line = json.loads(line)
                except json.JSONDecodeError:
                    print(f"Warning: Skipping malformed JSON on line {line_number}: {line.strip()}")
                    continue

                messages_to_process = []
                if isinstance(parsed_line, list):
                    messages_to_process.extend(parsed_line)
                elif isinstance(parsed_line, dict):
                    messages_to_process.append(parsed_line)
                else:
                    # Skip lines that are not lists or dictionaries
                    continue

                for message_item in messages_to_process:
                    if not isinstance(message_item, dict):
                        continue

                    # Navigate to the list of game events if present
                    # Expected path: message_item['push']['pub']['data']['data'] (for sequence packets)
                    # or message_item['push']['pub']['data'] (where 'data' itself is the list for single packets)
                    push_content = message_item.get("push")
                    if not isinstance(push_content, dict):
                        continue

                    pub_content = push_content.get("pub")
                    if not isinstance(pub_content, dict):
                        continue

                    data_payload = pub_content.get("data")
                    if not isinstance(data_payload, dict):
                        continue

                    # The actual game events are usually in a list under the 'data' key within data_payload
                    game_events = data_payload.get("data")
                    if not isinstance(game_events, list):
                        continue

                    for event in game_events:
                        if not isinstance(event, dict):
                            continue

                        event_type = event.get("type")
                        event_args = event.get("args")

                        if not isinstance(event_args, dict):
                            continue

                        # Handler for 'playCard' events
                        if event_type == "playCard":
                            card_data = event_args.get("card")
                            if (
                                isinstance(card_data, dict)
                                and "id" in card_data
                                and "type" in card_data
                                and "type_arg" in card_data
                            ):
                                card_id = str(card_data["id"])
                                suit = str(card_data["type"])  # This is the "type id" for suit
                                value = str(card_data["type_arg"])  # This is the "type_arg id" for value
                                all_cards_info[card_id] = {"suit": suit, "value": value}

                        # Handler for 'giveAllCardsToPlayer' events
                        elif event_type == "giveAllCardsToPlayer":
                            cards_on_table = event_args.get("cards")
                            if isinstance(cards_on_table, dict):
                                for card_id_str, card_details in cards_on_table.items():
                                    if (
                                        isinstance(card_details, dict)
                                        and "id" in card_details
                                        and "type" in card_details
                                        and "type_arg" in card_details
                                    ):
                                        # Ensure we use the 'id' from the details if available, otherwise the key
                                        actual_card_id = str(card_details.get("id", card_id_str))
                                        suit = str(card_details["type"])
                                        value = str(card_details["type_arg"])
                                        all_cards_info[actual_card_id] = {"suit": suit, "value": value}

                        # Handler for 'newHand' and 'takeCards' events
                        elif event_type in ["newHand", "takeCards"]:
                            cards_in_hand = event_args.get("cards")
                            if isinstance(cards_in_hand, list):
                                for card_data in cards_in_hand:
                                    if (
                                        isinstance(card_data, dict)
                                        and "id" in card_data
                                        and "type" in card_data
                                        and "type_arg" in card_data
                                    ):
                                        card_id = str(card_data["id"])
                                        suit = str(card_data["type"])
                                        value = str(card_data["type_arg"])
                                        all_cards_info[card_id] = {"suit": suit, "value": value}

    except FileNotFoundError:
        print(f"Error: Input file not found at {jsonl_file_path}")
        return
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}")
        return

    # Write the extracted card information to the output JSON file
    try:
        with open(output_json_path, "w", encoding="utf-8") as f_out:
            json.dump(all_cards_info, f_out, indent=2)
        print(f"Successfully extracted card data to {output_json_path}")
        print(f"Found information for {len(all_cards_info)} unique cards.")
    except IOError:
        print(f"Error: Could not write to output file {output_json_path}")
    except Exception as e:
        print(f"An unexpected error occurred during writing output: {e}")


if __name__ == "__main__":
    input_file = "extracted_bga_messages.jsonl"  # Replace with your actual input file path
    output_file = "card_data.json"  # Desired output file path

    # Make sure to place the script in the same directory as 'extracted_bga_messages.jsonl'
    # or provide the full path to the input file.
    extract_card_data(input_file, output_file)
