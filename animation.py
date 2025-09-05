
import time
import random

def animation(text, time_per_char): # zeichen für zeichen

    colors = [
        "\033[31m",
        "\033[32m",
        "\033[33m",
        "\033[34m",
        "\033[35m",
        "\033[36m",
        "\033[37m"
    ]

    lines = text.splitlines()
    # Konsole löschen
    print("\033[H\033[J", end="")
    # Cursor verstecken
    print("\033[?25l", end="")

    logo = '\033[32m' # grün

    # für jede zeile, wird jedes zeichen zu logo hinzugefügt und geprintet
    for line in lines:
        for ch in line:
            logo += f'{random.choice(colors)}{ch}'
            print("\033[H", end="")
            print(logo)
            if ch != ' ':
                time.sleep(time_per_char)
        logo += '\n'

    print("\033[37m")
    return logo