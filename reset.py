import json
import time

print('       reset')

forms_default = {
    "I": [
        [
            1,
            1,
            1,
            1
        ]
    ],
    "Q": [
        [
            1,
            1
        ],
        [
            1,
            1
        ]
    ],
    "Ll": [
        [
            1,
            0,
            0
        ],
        [
            1,
            1,
            1
        ]
    ],
    "Lr": [
        [
            0,
            0,
            1
        ],
        [
            1,
            1,
            1
        ]
    ],
    "Zr": [
        [
            0,
            1,
            1
        ],
        [
            1,
            1,
            0
        ]
    ],
    "Zl": [
        [
            1,
            1,
            0
        ],
        [
            0,
            1,
            1
        ]
    ],
    "T": [
        [
            0,
            1,
            0
        ],
        [
            1,
            1,
            1
        ]
    ],
    "2x3": [[1,1,1],
          [1,1,1]],
  "5er": [[1, 1, 1, 1, 1]],
  "1er": [[1]],
  "2er": [[1, 1]],
  "4": [[1,0,0],
 [1,1,1],
 [0,1,0]],
  "bar-code": [
    [1,0,1,0,1]
],
  "berge": [
    [0,1,0,1],
    [1,1,1,1]
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
        ],
        "highscore": 0,
        "config-name": "normal",
        "speed": {
            "0": [
                1,
                1.0
            ],
            "17": [
                2,
                0.9
            ],
            "30": [
                3,
                0.82
            ],
            "40": [
                4,
                0.74
            ],
            "70": [
                5,
                0.67
            ],
            "110": [
                6,
                0.6
            ],
            "160": [
                7,
                0.54
            ],
            "220": [
                8,
                0.48
            ],
            "290": [
                9,
                0.43
            ],
            "370": [
                10,
                0.39
            ],
            "460": [
                11,
                0.35
            ],
            "560": [
                12,
                0.31
            ],
            "670": [
                13,
                0.28
            ],
            "790": [
                14,
                0.25
            ],
            "920": [
                15,
                0.22
            ],
            "1060": [
                16,
                0.2
            ],
            "1210": [
                17,
                0.18
            ],
            "1370": [
                18,
                0.16
            ],
            "1540": [
                19,
                0.14
            ],
            "1720": [
                20,
                0.12
            ]
        }
    },
    "Custom-Tetris-1": {
        "rows": 23,
        "cols": 13,
        "symbol-background": "·",
        "symbol-tetris": "@",
        "background-color": 6,
        "forms": [
            "I",
            "Q",
            "Ll",
            "Lr",
            "Zr",
            "Zl",
            "T",
            "2x3",
            "5er",
            "1er",
            "2er",
            "4",
            "bar-code",
            "berge"
        ],
        "highscore": 0,
        "config-name": "Custom-Tetris-1",
        "speed": {
            "0": [
                1,
                1.0
            ],
            "17": [
                2,
                0.9
            ],
            "30": [
                3,
                0.82
            ],
            "40": [
                4,
                0.74
            ],
            "70": [
                5,
                0.67
            ],
            "110": [
                6,
                0.6
            ],
            "160": [
                7,
                0.54
            ],
            "220": [
                8,
                0.48
            ],
            "290": [
                9,
                0.43
            ],
            "370": [
                10,
                0.39
            ],
            "460": [
                11,
                0.35
            ],
            "560": [
                12,
                0.31
            ],
            "670": [
                13,
                0.28
            ],
            "790": [
                14,
                0.25
            ],
            "920": [
                15,
                0.22
            ],
            "1060": [
                16,
                0.2
            ],
            "1210": [
                17,
                0.18
            ],
            "1370": [
                18,
                0.16
            ],
            "1540": [
                19,
                0.14
            ],
            "1720": [
                20,
                0.12
            ]
        }
    },
    "Annoying-Tetris": {
        "rows": 25,
        "cols": 18,
        "symbol-background": "0",
        "symbol-tetris": "1",
        "background-color": 3,
        "forms": [
            "1er",
            "2er"
        ],
        "highscore": 0,
        "config-name": "Annoying-Tetris",
        "speed": 1
    },
    "Unspielbar": {
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
        ],
        "highscore": 0,
        "config-name": "Unspielbar",
        "speed": {
            "start-interval": 1.0,
            "min-interval": 0.05,
            "k": 0.1
        }
    },
    "game-counter": 0,
    "gametime": 0.0
}

json.dump(forms_default, open('forms.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
json.dump(data_default, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

time.sleep(1)