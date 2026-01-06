import json


def recursive_decode(value):
    """
    Recursively decode a value, parsing inner JSON strings if possible.
    """
    try:
        if isinstance(value, list):
            return [recursive_decode(item) for item in value]
        elif isinstance(value, dict):
            return {k: recursive_decode(v) for k, v in value.items()}
        elif isinstance(value, str):
            # Attempt to parse the string as JSON
            parsed_value = json.loads(value)
            return recursive_decode(parsed_value)
    except (json.JSONDecodeError, TypeError):
        pass

    return value


def decode_socketio(encoded_message):
    try:
        # Remove the socket.IO message type (first two bytes, i.e., '42')
        message = encoded_message.decode("utf-8")
        if len(message) <= 2:
            return {"message": message}

        # Split the message into the event name and JSON payload
        split_index = message.find("[")
        if split_index != -1:
            payload_str = message[split_index:]
        else:
            payload_str = message

        # Parse the payload JSON array
        payload = json.loads(payload_str)

        # Sanity check for the event name
        if not payload:
            return {}

        # Recursively decode the payload to handle nested JSON strings
        cleaned_payload = [recursive_decode(item) for item in payload[1:]]

        return {"event_name": payload[0], "payload": cleaned_payload}
    except Exception as e:
        print(f"Error decoding message: {e}")
        return {}


if __name__ == "__main__":
    test_bytes = b'42["bgamsg","{\\"packet_id\\":251,\\"packet_type\\":\\"sequence\\",\\"channel\\":\\"\\\\/table\\\\/t564886435\\",\\"id\\":1,\\"data\\":[{\\"uid\\":\\"66ecd7c38c051\\",\\"type\\":\\"playCard\\",\\"log\\":\\"${player_name} plays ${color_displayed}${value_displayed}\\",\\"args\\":{\\"player_id\\":\\"89223814\\",\\"player_name\\":\\"Jean Qc\\",\\"color_displayed\\":\\"<span style=\\\\\\"color:black\\\\\\" class=\\\\\\"suit_1\\\\\\">\\\\u2660<\\\\/span>\\",\\"value_displayed\\":\\"7\\",\\"card\\":{\\"id\\":\\"11\\",\\"type\\":\\"1\\",\\"type_arg\\":\\"7\\",\\"location\\":\\"hand\\",\\"location_arg\\":\\"89223814\\"},\\"heartbreak\\":false},\\"h\\":\\"714efe\\"},{\\"uid\\":\\"66ecd7c38c34b\\",\\"type\\":\\"updateReflexionTime\\",\\"log\\":\\"\\",\\"args\\":{\\"player_id\\":\\"89223814\\",\\"delta\\":\\"8\\",\\"max\\":\\"84\\"}},{\\"uid\\":\\"66ecd7c38c7ce\\",\\"type\\":\\"gameStateChange\\",\\"log\\":\\"\\",\\"args\\":{\\"id\\":32,\\"active_player\\":\\"89223814\\",\\"args\\":null,\\"type\\":\\"game\\",\\"reflexion\\":{\\"total\\":{\\"96639266\\":\\"84\\",\\"89223814\\":84,\\"94190068\\":\\"84\\",\\"96483178\\":\\"84\\"}},\\"updateGameProgression\\":62}},{\\"uid\\":\\"66ecd7c38d44e\\",\\"type\\":\\"gameStateChange\\",\\"log\\":\\"\\",\\"args\\":{\\"id\\":31,\\"active_player\\":94190068,\\"args\\":[],\\"type\\":\\"activeplayer\\",\\"reflexion\\":{\\"total\\":{\\"96639266\\":\\"84\\",\\"89223814\\":\\"84\\",\\"94190068\\":\\"84\\",\\"96483178\\":\\"84\\"}}},\\"lock_uuid\\":\\"9dae7889-8fbb-4516-8b8b-26730836a758\\"}],\\"move_id\\":115,\\"table_id\\":\\"564886435\\",\\"prevpacket\\":{\\"0\\":\\"249\\",\\"89223814\\":\\"248\\",\\"94190068\\":\\"250\\",\\"96483178\\":\\"242\\",\\"96639266\\":\\"244\\"},\\"gamename\\":\\"hearts\\",\\"time\\":1726797763}"]'
    decode_socketio(test_bytes)