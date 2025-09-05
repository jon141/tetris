import json
import time
import os

import configuration
import addform
import animation
import asciiart
import gameclass
import statistik


# Daten laden
forms = json.load(open('forms.json', 'r', encoding='utf-8'))
data = json.load(open('data.json', 'r', encoding='utf-8'))


def clear_console():
    if os.name == "nt":  # Windows
        os.system("cls")
    else:  # Linux
        os.system("clear")
    print("\033[H\033[J", end='')  # wenn der rest nicht funktionniert hat

def valid_choice():
    while True:
        print("\033[H\033[J", end='')
        print('\033[32m')
        print(asciiart.tetris)
        print('\033[0m')

        print("""
        Wähle aus, was du machen willst (1-7):
            \033[31m1\033[0m Normales Spiel
            \033[31m2\033[0m gespeicherte Konfiguration spielen
            \033[31m3\033[0m Konfiguration ansehen / Spiel konfigurieren 
            \033[31m4\033[0m Neue Formen hinzugügen  
            \033[31m5\033[0m Statistik / Informationen / Steuerung
            \033[31m6\033[0m Spielstand zurücksetzen
            \033[31m7\033[0m Spiel beenden
                """)

        choice = input('            \033[0m\033[39m') # setzt curserfarbe zurück

        if choice in ['1', '2', '3', '4', '5', '6', '7', 'b', 'q', '^[', '\x1b']:
            return choice


def gamestart(config_data):
    tetris = gameclass.Tetris(rows=config_data['rows'], cols=config_data['cols'],
                  background=config_data['symbol-background'],
                  background_color=config_data['background-color'],
                  foreground=config_data['symbol-tetris'], forms=forms,
                  form_select=config_data['forms'])  # , placed_color=konfigurationsdaten["color-placed"])

    tetris.start_game()


clear_console()
print('\033[?25l') # curser verstecken
animation.animation(asciiart.tetris, 0.008) # Tetris Schriftzug erscheint zeichen für zeichen
while True:
    print("\033[H\033[J", end='')
    choice = valid_choice()
    print("\033[A\033[K", end="")  # Eine Zeile nach oben und löschen
    #print('es kann weiter gehen')
    if choice == '1' or choice == '2':
        #print('1')
        print("\033[H\033[J", end='') # ziehe dein bildschirm so groß, bis du alle 4 Ecken siehst
        #print_ramen(150, 30)
        input('Mach das Fenster ausreichend groß!!! Spiel kann beendet werden, wenn b/q/ESC gedrückt wird. Press enter to start the Game.')
        print("\033[H\033[J", end='')
        print(f'\033[36m{asciiart.tetris_gamestart}\033[0m', end='')
        time.sleep(1)

        clear_console()

        if choice == '1':
            konfigurationsdaten = data['normal']

        else:
            konfigurationsdaten = data['konfiguration']

        gamestart(konfigurationsdaten)

    elif choice == '3':
        print("\033[H\033[J", end='')
        configuration.spiel_konfigurieren(forms, data)
    elif choice == '4':
        addform.add_form(forms, asciiart.formen_hinzufuegen)
        print(forms)
    elif choice == '5':
        print("\033[H\033[J", end='')
        clear_console()
        statistik.print_statistics(data, asciiart)
        input()
    elif choice == '6':
        print('\033[?25h', end='')
        x = input('      Bist du sicher? Gib "ja" ein zum bestätigen. \n            >')
        if x == 'ja':
            print('\033[?25l', end='')

            import reset
            # daten neu laden
            forms = json.load(open('forms.json', 'r', encoding='utf-8'))
            data = json.load(open('data.json', 'r', encoding='utf-8'))
    else:
        break
    #input('')

#input('Do you want to end and close console???')