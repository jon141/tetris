
import time

def animation(text, time_per_char): # zeichen für zeichen
    lines = text.splitlines()
    # Konsole löschen
    print("\033[H\033[J", end="")
    # Cursor verstecken
    print("\033[?25l", end="")

    logo = '\033[32m' # grün

    # für jede zeile, wird jedes zeichen zu logo hinzugefügt und geprintet
    for line in lines:
        for ch in line:
            logo += ch
            print("\033[H", end="")
            print(logo)
            if ch != ' ':
                time.sleep(time_per_char)
        logo += '\n'

