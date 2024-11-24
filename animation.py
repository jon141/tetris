
import time
def animation(text):

    print("\033[H\033[J", end="")
    #print('\033[?25l')# Konsole löschen / curser verstecken
    lines = text.splitlines()
    max_len = max(len(line) for line in lines)  # Maximale Breite des Logos
    revealed_logo = [" " * max_len for _ in lines]  # Start mit Leerzeichen
    print('')
    for row in range(len(lines)):
        for col in range(len(lines[row])):
            revealed_logo[row] = (
                revealed_logo[row][:col] + lines[row][col] + revealed_logo[row][col+1:]
            )
            print("\033[H", end="")  # Cursor zurücksetzen
            print("\033[32m\n".join(revealed_logo))  # Logo mit aktuellem Fortschritt drucken
            time.sleep(0.005)  # Kurze Pause zwischen den Zeichen