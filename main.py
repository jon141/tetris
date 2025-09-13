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
        clear_console()
        print("\033[H\033[J", end='')
        print('\033[32m')
        #print(asciiart.tetris)
        #print(colored_tetris_logo) # kann man machen, dann bleibt es bunt
        print('\033[32m' + asciiart.tetris)

        print('\033[0m')

        print("""
        \033[34mWähle aus, was du machen willst (1-7):
            \033[31m1\033[0m Normales Spiel
            \033[31m2\033[0m Konfiguration spielen
            \033[31m3\033[0m Konfigurationen erstellen / ansehen / bearbeiten 
            \033[31m4\033[0m Neue Formen hinzufügen  
            \033[31m5\033[0m Steuerung / Statistik / Informationen 
            \033[31m6\033[0m Spielstand zurücksetzen
            \033[31m7\033[0m Spiel beenden
            """, end='')

        choice = input('\033[0m\033[39m') # setzt curserfarbe zurück

        if choice in ['1', '2', '3', '4', '5', '6', '7', 'b', 'q', '^[', '\x1b']:
            return choice


def gamestart(config_data):
    tetris = gameclass.Tetris(config_data, forms)  # , placed_color=konfigurationsdaten["color-placed"])

    tetris.start_game()


clear_console()
print('\033[?25l') # curser verstecken
colored_tetris_logo = animation.animation(asciiart.tetris, 0.01, 0, 'random') # Tetris Schriftzug erscheint zeichen für zeichen
print('\033[32m' + asciiart.tetris)
while True:

    forms = json.load(open('forms.json', 'r', encoding='utf-8'))
    data = json.load(open('data.json', 'r', encoding='utf-8'))

    print("\033[H\033[J", end='')
    choice = valid_choice()
    print("\033[A\033[K", end="")  # Eine Zeile nach oben und löschen
    #print('es kann weiter gehen')
    if choice == '1' or choice == '2':
        print("\033[H\033[J", end='') #

        if choice == '1':
            konfigurationsdaten = data['normal']

        else:
            print('\nWähle die Konfiguration aus.')
            tab = 4*' '
            c = 0  # stichpunktzähler
            configuration_names = []
            for name in data:
                if name not in ('normal', 'gametime', 'game-counter'):
                    c += 1
                    print(
                        f'{2 * tab}- \033[31m{c}\033[37m: "\033[33m{name}\033[37m"')
                    configuration_names.append(name)
            #print(configuration_names)

            config_choice = input('> ')
            try:
                config_name = configuration_names[int(config_choice) - 1]
            except (ValueError, IndexError):
                if config_choice not in ('b', 'q', '^[', '\x1b'):
                    print('Es kam zu einem Fehler – es wird ein normales Spiel gestartet.')
                    time.sleep(2)
                config_name = 'normal'
            if config_choice in ('b', 'q', '^[', '\x1b'): # abbrechbar mit bqESC
                konfigurationsdaten = False
            else:
                konfigurationsdaten = data[config_name]

        if konfigurationsdaten:
            start = input('''
Mach das Fenster ausreichend groß!!! 
Spiel kann beendet werden, wenn b/q/ESC gedrückt wird.
Falls sich das Spielfeld durch Veränderung der Terminalgröße unbrauchbar wird, drücke 'r', um es neu zu laden

Enter um zu starten; abbrechen mit b/q/ESC.
''')

            if start not in ('b', 'q', '^[', '\x1b'):

                print("\033[H\033[J", end='')
                print(f'\033[36m{asciiart.tetris_gamestart}\033[0m', end='')
                time.sleep(1)
                clear_console()

                gamestart(konfigurationsdaten)

    elif choice == '3':
        print("\033[H\033[J", end='')

        forms = json.load(open('forms.json', 'r', encoding='utf-8'))
        data = json.load(open('data.json', 'r', encoding='utf-8'))
        while True:
            forms = json.load(open('forms.json', 'r', encoding='utf-8'))
            data = json.load(open('data.json', 'r', encoding='utf-8'))
            finished = configuration.configuration_menu(forms, data)
            if not finished:
                clear_console()
            else:
                break

    elif choice == '4':
        addform.add_form(forms, asciiart.formen_hinzufuegen)
        print(forms)
    elif choice == '5':
        print("\033[H\033[J", end='')
        clear_console()
        data = json.load(open('data.json', 'r', encoding='utf-8'))
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
        print('\033[?25h')
        break
    #input('')

#input('Do you want to end and close console???')