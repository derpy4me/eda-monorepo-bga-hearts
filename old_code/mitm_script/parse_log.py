import re
import ast
import json  # For saving the extracted data as JSON


def extract_data_from_log(log_file_path):
    """
    Extracts and parses structured data from log lines.

    The function looks for lines containing "[debug] Decoded Message(s)"
    and then parses the Python literal string found after "decoded_message=".

    Args:
        log_file_path (str): The path to the log file.

    Returns:
        list: A list of Python objects (dictionaries or lists) parsed
              from the 'decoded_message' parts of the log.
    """
    extracted_objects = []
    # Regex to identify the target log lines and capture the data string.
    # It looks for "[debug] Decoded Message" (or "Messages")
    # and then captures everything after "decoded_message=".
    # (?:s?) makes the 's' in 'Messages' optional.
    log_line_pattern = re.compile(r"\[debug\s*] Decoded Messages?\s*decoded_message=(.*)")

    try:
        with open(log_file_path, "r", encoding="utf-8") as log_file:
            for line_number, line in enumerate(log_file, 1):
                match = log_line_pattern.search(line)
                if match:
                    # Extract the string representation of the data
                    data_string_repr = match.group(1).strip()

                    if data_string_repr:  # Proceed if the string is not empty
                        try:
                            # ast.literal_eval safely parses a string containing a Python literal
                            # (strings, numbers, tuples, lists, dicts, booleans, None).
                            # This is suitable here because the log format is Python-like.
                            parsed_object = ast.literal_eval(data_string_repr)
                            if not parsed_object:
                                continue
                            if isinstance(parsed_object, list) and len(parsed_object) == 1 and not parsed_object[0]:
                                continue
                            extracted_objects.append(parsed_object)
                        except (ValueError, SyntaxError) as e:
                            print(f"Warning: Could not parse data on line {line_number}: {e}")
                            # Optionally, log the problematic string for debugging:
                            # print(f"Problematic string snippet: '{data_string_repr[:200]}...'")
                    # else:
                    # print(f"Info: Empty data string on line {line_number} after 'decoded_message='.")

    except FileNotFoundError:
        print(f"Error: Log file not found at '{log_file_path}'")
    except Exception as e:
        print(f"An unexpected error occurred while processing the log file: {e}")

    return extracted_objects


if __name__ == "__main__":
    # Specify the path to your log file
    log_file_path = "./mitmdump.log"

    extracted_data = extract_data_from_log(log_file_path)

    if extracted_data:
        print(f"Successfully extracted {len(extracted_data)} data objects from the log.")

        # --- Storing the data for later processing and analysis ---

        # Option 1: Work with the data directly in Python
        # For example, print the first few extracted objects:
        print("\nFirst 3 extracted objects:")
        for i, item in enumerate(extracted_data[:3]):
            print(f"Object {i+1}: {type(item)} - {str(item)[:100]}...")  # Print type and a snippet

        # Option 2: Save all extracted objects to a JSON Lines (JSONL) file
        # Each line in a .jsonl file is a separate, valid JSON object.
        # This is good for streaming or processing large datasets.
        output_jsonl_file = "extracted_bga_messages.jsonl"
        try:
            with open(output_jsonl_file, "w", encoding="utf-8") as outfile:
                for item in extracted_data:
                    # Convert the Python object to a JSON string
                    json_record = json.dumps(item)
                    outfile.write(json_record + "\n")
            print(f"\nAll extracted data has been saved to '{output_jsonl_file}'.")
            print("Each line in this file is a JSON representation of a decoded message.")
        except IOError as e:
            print(f"Error writing to JSONL file '{output_jsonl_file}': {e}")

        # Option 3: Save all extracted objects to a single JSON file (as a JSON array)
        # output_json_file = "extracted_bga_messages.json"
        # try:
        #     with open(output_json_file, 'w', encoding='utf-8') as outfile:
        #         json.dump(extracted_data, outfile, indent=2) # indent for pretty printing
        #     print(f"\nAll extracted data has been saved to '{output_json_file}' as a single JSON array.")
        # except IOError as e:
        #     print(f"Error writing to JSON file '{output_json_file}': {e}")

    else:
        print("No data was extracted. Please check the log file path and its content.")
