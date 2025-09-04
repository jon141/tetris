import json
import time

print('       reset')

forms_default = {
    "I": [
        [1, 1, 1, 1]
    ],
    "Q": [
        [1, 1],
        [1, 1]
    ],
    "Ll": [
        [1, 0, 0],
        [1, 1, 1]
    ],
    "Lr": [
        [0, 0, 1],
        [1, 1, 1]
    ],
    "Zr": [
        [0, 1, 1],
        [1, 1, 0]
    ],
    "Zl": [
        [1, 1, 0],
        [0, 1, 1]
    ],
    "T": [
        [0, 1, 0],
        [1, 1, 1]
    ]
}

data_default = {
    "normal": {
        "rows": 20,
        "cols": 10,
        "symbol-background": "·",
        "symbol-tetris": "□",
        "background-color": 0,
        "forms": [
            "I",
            "Q",
            "Ll",
            "Lr",
            "Zr",
            "Zl",
            "T"
        ]
    },
    "konfiguration": {
        "rows": 20,
        "cols": 10,
        "symbol-background": "😀",
        "symbol-tetris": "#",
        "background-color": 3,
        "forms": [
            "I",
            "Q",
            "Ll",
            "Lr",
            "Zr",
            "Zl",
            "T"
        ]
    },
    "highscore": 0,
    "game-counter": 0,
    "gametime": 0

}

json.dump(forms_default, open('forms.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
json.dump(data_default, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

time.sleep(1)