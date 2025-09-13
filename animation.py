import time
import random

def animation(text, time_per_char=0.01, row_position=1, color='random'): # zeichen für zeichen

    colors = [
        "\033[31m",  # rot
        "\033[32m",  # grün
        "\033[33m",  # gelb
        "\033[34m",  # blau
        "\033[35m",  # magenta
        "\033[36m",  # cyan
        "\033[37m",  # weiß
    ]

    lines = text.splitlines()

    # Cursor verstecken
    print("\033[?25l", end="")

    if color != 'random':
        print(f'{colors[min(color, 6)]}') # ganzes logo in einer farbe

    print(f"\033[{row_position};0H", end="", flush=True)  # in richtige reihe gehen

    # für jede zeile, wird jedes zeichen zu logo hinzugefügt und geprintet
    for line in lines:
        for ch in line:
            if color == 'random':
                print(f'{random.choice(colors)}{ch}', end='', flush=True)
            else:
                print(f'{ch}', end='', flush=True)
            if ch != ' ':
                time.sleep(time_per_char)

        print('\n', end='', flush=True)

    print("\033[37m") # curser wirder weiß