my_dict = {
    "event_name": "bgamsg",
    "payload": [
        {
            "packet_id": 251,
            "packet_type": "sequence",
            "channel": "/table/t564886435",
            "id": 1,
            "data": [
                {
                    "uid": "66ecd7c38c051",
                    "type": "playCard",
                    "log": "${player_name} plays ${color_displayed}${value_displayed}",
                    "args": {
                        "player_id": 89223814,
                        "player_name": "Jean Qc",
                        "color_displayed": '<span style="color:black" class="suit_1">♠</span>',
                        "value_displayed": 7,
                        "card": {"id": 11, "type": 1, "type_arg": 7, "location": "hand", "location_arg": 89223814},
                        "heartbreak": False,
                    },
                    "h": "714efe",
                },
                {
                    "uid": "66ecd7c38c34b",
                    "type": "updateReflexionTime",
                    "log": "",
                    "args": {"player_id": 89223814, "delta": 8, "max": 84},
                },
                {
                    "uid": "66ecd7c38c7ce",
                    "type": "gameStateChange",
                    "log": "",
                    "args": {
                        "id": 32,
                        "active_player": 89223814,
                        "args": None,
                        "type": "game",
                        "reflexion": {"total": {"96639266": 84, "89223814": 84, "94190068": 84, "96483178": 84}},
                        "updateGameProgression": 62,
                    },
                },
                {
                    "uid": "66ecd7c38d44e",
                    "type": "gameStateChange",
                    "log": "",
                    "args": {
                        "id": 31,
                        "active_player": 94190068,
                        "args": [],
                        "type": "activeplayer",
                        "reflexion": {"total": {"96639266": 84, "89223814": 84, "94190068": 84, "96483178": 84}},
                    },
                    "lock_uuid": "9dae7889-8fbb-4516-8b8b-26730836a758",
                },
            ],
            "move_id": 115,
            "table_id": 564886435,
            "prevpacket": {"0": 249, "89223814": 248, "94190068": 250, "96483178": 242, "96639266": 244},
            "gamename": "hearts",
            "time": 1726797763,
        }
    ],
}


random_data = [
    [
        {"str": "${player_name}", "args": {"player_name": "spencercal"}, "type": "header"},
        {"str": "${player_name}", "args": {"player_name": "jordonet"}, "type": "header"},
        {"str": "${player_name}", "args": {"player_name": "keithcal"}, "type": "header"},
        {"str": "${player_name}", "args": {"player_name": "testMyPill"}, "type": "header"},
    ],
    [
        {"str": '<span style="color:red" class="suit_2">♥</span>', "args": []},
        11,
        "",
        2,
    ],
    [
        {"str": '<span style="color:black" class="suit_1">♠</span>Q', "args": []},
        "✓",
        "",
        "",
    ],
    [
        {"str": '<span style="color:red" class="suit_4">♦</span>J', "args": []},
        "",
        "",
        "✓",
    ],
    [{"str": "Hand score", "args": []}, -24, 0, 8, 0],
    [{"str": "Total score", "args": []}, 51, 75, 83, 75],
]
