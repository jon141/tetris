
import time
import random

def animation2(text, time_per_char): # zeichen für zeichen

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
    #print("\033[H\033[J", end="")
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

def animation(text, time_per_char, row_position, color): # zeichen für zeichen

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
    # Konsole löschen
    #print("\033[H\033[J", end="")
    # Cursor verstecken
    print("\033[?25l", end="")

    if color != 'random':
        logo = f'{colors[min(color, 6)]}' # ganzes logo in einer farbe
    else:
        logo = ''

    # für jede zeile, wird jedes zeichen zu logo hinzugefügt und geprintet
    for line in lines:
        for ch in line:
            if color == 'random':
                logo += f'{random.choice(colors)}{ch}'
            else:
                logo += ch
            #print("\033[H", end="")
            #print(logo)

            print(f"\033[{row_position};0H{logo}", end="", flush=True) # setzt curser wieder

            if ch != ' ':
                time.sleep(time_per_char)
        logo += '\n'

    print("\033[37m")
    return logo