import json
import os
import time


# ----------------------new----------------------

def clear_console():
    if os.name == "nt":  # Windows
        os.system("cls")
    else:  # Linux
        os.system("clear")
    print("\033[H\033[J", end='')  # wenn der rest nicht funktionniert hat


def delete_last_lines(lines):
    print(lines * '\033[F\033[2K', end='')


def print_form(form, abstandl, symbol_tetris, symbol_background, color_tetris, color_background):
    colors = [
        "\033[31m",  # rot
        "\033[32m",  # grün
        "\033[33m",  # gelb
        "\033[34m",  # blau
        "\033[35m",  # magenta
        "\033[36m",  # cyan
        "\033[37m",  # weiß
    ]
    for row in form:
        row_string = abstandl * ' '
        for col in row:
            # print(col)
            if col == 1:
                row_string += f"{colors[color_tetris]}{symbol_tetris} \033[0m"  # \033[44m  \033[0m
            elif col == 0:
                row_string += f"{colors[color_background]}{symbol_background} \033[0m"  # \033[44m  \033[0m
        print(row_string)


def print_configuration(data, forms, config_name):
    colors = [
        "\033[31m",  # rot
        "\033[32m",  # grün
        "\033[33m",  # gelb
        "\033[34m",  # blau
        "\033[35m",  # magenta
        "\033[36m",  # cyan
        "\033[37m",  # weiß
    ]

    values_dict = data[config_name]
    print(f'''\033[32m
{config_name}           \033[0m
    Highscore        : \033[31m{values_dict['highscore']}\033[0m
    Reihen           : \033[31m{values_dict['rows']}\033[0m
    Spalten          : \033[31m{values_dict['cols']}\033[0m
    Hintergrundsymbol: \033[31m{values_dict['symbol-background']}\033[0m
    Tetris-Symbol    : \033[31m{values_dict['symbol-tetris']}\033[0m
    Hintergrundfarbe : {colors[values_dict['background-color']]}{values_dict['background-color']}\033[0m
    Formen           : \033[31m{", ".join(values_dict['forms'])}\033[0m

Formen: 
''')
    form_names = list(forms.keys())
    for number, name in enumerate(form_names):
        form = forms[name]
        if name in values_dict['forms']:
            # print('\033[31m' + 15 * '_')
            print('\033[31m', end='')

        print(number + 1, ':', name, '\033[37m')
        if name in values_dict['forms']:
            print_form(form, 3, values_dict['symbol-tetris'], values_dict['symbol-background'], 1, 3)
        else:
            print_form(form, 3, '1', '0', 6, 6)


def row_col_valid_checker(placeholder):
    while True:
        eingabe = input(f'\033[0m{placeholder} des Spielfelds: \033[31m')

        if eingabe in ('^[', '\x1b'):
            return None
        elif eingabe == '-':
            return False
        else:
            try:
                eingabe = int(eingabe)
                return eingabe
            except:
                print('Falsche Eingabe')


def form_choice_input(form_names):
    while True:
        formen = input('\033[0mFormen: (gib die Nummern ein.) (Beispiel: 1, 2, 3, 4): \033[31m')
        try:
            formen = formen.replace(' ', '')
            formen = list(map(int, formen.split(',')))
            #print(formen)
            form_choice = []

            for number in formen:
                form_choice.append(form_names[number - 1])
            return form_choice
        except:
            print('Error. Try again.')


def configure_game(forms, data, config_name):
    # wenn name = False ist, dann wird das spiel neu erstellt und es muss ein neuer name gewählt werden. ist der name nicht false, also schon existent, muss beim speichern überschrieben werden und alte werte die nicht verändert werden wollen können beibelassen werden

    # durch die is None abfrage bei jeder eingabe abbrechbar
    rows = row_col_valid_checker('Reihen')
    if rows is None:  # ist none, wenn abbruchbedingung ESC erfüllt ist
        return None
    elif rows is False:
        if config_name:  # wenn der name nicht false ist
            rows = data[config_name]['rows']
        else:  # sonst die werte der normalen konfig übernehmen
            rows = data['normal'][rows]

    cols = row_col_valid_checker('Spalten')
    if cols is None:
        return None
    elif cols is False:
        if config_name:  # wenn der name nicht false ist
            cols = data[config_name]['cols']
        else:  # sonst die werte der normalen konfig übernehmen
            cols = data['normal']['cols']

    # auch abbrechbar
    background_symbol = input('\033[0mHintergrundsymbol: \033[31m')
    if background_symbol in ('^[', '\x1b'):
        return None
    elif background_symbol == '-':
        if config_name:  # wenn der name nicht false ist
            background_symbol = data[config_name]['symbol-background']
        else:  # sonst die werte der normalen konfig übernehmen
            background_symbol = data['normal']['symbol-background']

    while True:  # wenn vorder und hintergrund nicht gleich lang ist, verschiebt sich alles im spielfeld
        tetris_symbol = input('\033[0mTetris-Symbol: \033[31m')
        if tetris_symbol in ('^[', '\x1b'):
            return None
        elif tetris_symbol == '-':
            if config_name:  # wenn der name nicht false ist
                tetris_symbol = data[config_name]['symbol-tetris']
            else:  # sonst die werte der normalen konfig übernehmen
                tetris_symbol = data['normal']['symbol-tetris']
            if len(tetris_symbol) == len(background_symbol):
                break
        if len(tetris_symbol) != len(background_symbol):
            print('Das Tetris- und Hintergrundsymbol müssen gleich viele Zeichen beinhalten.')
        else:
            break

    colors = [
        "\033[31m",
        "\033[32m",
        "\033[33m",
        "\033[34m",
        "\033[35m",
        "\033[36m",
        "\033[37m"
    ]

    while True:
        try:
            background_color = int(input(
                f'\033[0mHintergrundfarbe ({colors[0]}0, {colors[1]}1, {colors[2]}2, {colors[3]}3, {colors[4]}4, {colors[5]}5, {colors[6]}6): \033[31m'))
            if str(background_color) in ('^[', '\x1b'):
                return None
            if background_color in (0, 1, 2, 3, 4, 5, 6):
                break
            elif background_color == '-': # warum auch immer, das geht nicht
                if config_name:  # wenn der name nicht false ist
                    tetris_symbol = data[config_name]['background-color']
                else:  # sonst die werte der normalen konfig übernehmen
                    tetris_symbol = data['normal']['background-color']
                break
            else:
                print('\033[37mFalsche Eingabe.')
        except:
            print('\033[37mFalsche Eingabe.')

    print('\033[0m')

    form_names = list(forms.keys())

    for number, name in enumerate(form_names):
        print(15 * '_')
        print(number + 1, ':', name)
        form = forms[name]
        print_form(form, 3, tetris_symbol, background_symbol, 1, 5)  # symbole der neuen konfiguration übergeben

    form_choice_list = form_choice_input(form_names)

    print('\033[0m')

    # ----- fallgeschwindigkeits system setzten -> standart level; exponentiell, mit den 3 werten (min, start, k); konstanter wert

    print("\n\033[0mFallgeschwindigkeitsmodus wählen:")
    print("  \033[31m1\033[37m: Konstanter Wert")
    print("  \033[31m2\033[37m: Exponentiell (minimun, startwert, k-Proportionalitätsfaktor)")
    print("  \033[31m3\033[37m: standart Levelsystem (kann in data.json individuell angepasst werden)")

    while True:
        speed_choice = input("\033[0mModus wählen: \033[31m")
        if speed_choice in ('^[', '\x1b', 'q', 'b'):
            return None

        if speed_choice == "1":
            # Konstanter Wert
            try:
                speed = float(input("\033[0mKonstante Geschwindigkeit in Sekunden (z.B. 0.75): \033[31m"))
                break
            except:
                print("Ungültige Eingabe.")

        elif speed_choice == "2":
            try:
                start_interval = float(input("Startgeschwindigkeit: "))
                min_interval = float(input("Minimale Geschwindigkeit: "))
                k = float(input("Proportionalitätskonstante k: "))
                speed = {
                    "start-interval": start_interval,
                    "min-interval": min_interval,
                    "k": k
                }
                break
            except:
                print("Ungültige Eingabe.")
        elif speed_choice == "3":
            speed = data['normal']['speed']  # nur Marker, später kannst du Levels in deinem Code umsetzen
            break
        else:
            print("Falsche Eingabe, wähle 1, 2 oder 3.")
    print('\033[0m')


    if not config_name:
        config_name = input(
            'Gib deiner Konfiguration einen Namen. (existiert ein Name schon, wird die zugehörige Konfiguration überschrieben.): ')

    bestaetigung = input('Bestätige deine Konfiguration, oder breche ab mit b/q/ESC ab. ')
    print('\033[?25l', end='')

    if bestaetigung in ('b', '\x1b', 'q', '^['):
        return None
    else:
        data[config_name]['rows'] = rows
        data[config_name]['cols'] = cols
        data[config_name]['symbol-tetris'] = tetris_symbol
        data[config_name]['symbol-background'] = background_symbol
        data[config_name]['forms'] = form_choice_list
        data[config_name]['background-color'] = background_color
        data[config_name]['speed'] = speed
        data[config_name]['config-name'] = config_name


        json.dump(data, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)


def configuration_menu(forms, data):
    print(f'''\033[32m
     _  __            __ _                       _   _             
    | |/ /           / _(_)                     | | (_)            
    | ' / ___  _ __ | |_ _  __ _ _   _ _ __ __ _| |_ _  ___  _ __  
    |  < / _ \| '_ \|  _| |/ _` | | | | '__/ _` | __| |/ _ \| '_ \  
    | . \ (_) | | | | | | | (_| | |_| | | | (_| | |_| | (_) | | | |
    |_|\_\___/|_| |_|_| |_|\__, |\__,_|_|  \__,_|\__|_|\___/|_| |_|
                            __/ |                                  
                           |___/   

        \033[0m''')

    tab = 4 * ' '  # abstand nach links

    print(f'{tab}Zahl eingeben. Zurück mit b/q/ESC:')
    print(f'{2 * tab}- \033[31m1\033[37m: \033[32mNeue Konfiguration\033[37m')
    print(f'{2 * tab}- \033[31m2\033[37m: \033[32mKonfiguration löschen\033[37m')
    c = 2  # stichpunktzähler
    configuration_names = []
    for name in data:
        if name not in ('normal', 'gametime', 'game-counter'):
            c += 1
            print(f'{2 * tab}- \033[31m{c}\033[37m: Konfiguration "\033[33m{name}\033[37m" ansehen/konfigurieren')
            configuration_names.append(name)

    break_options = ['b', 'q', '^[', '\x1b']
    options = [str(x) for x in range(1, c + 1)]
    while True:
        choice = input(f'{3 * tab + " "}> \033[0m\033[39m')
        if choice in options:
            # dann konfiguration anzeigen
            if choice == '1':
                configure_game(forms, data, False)
                # neue konfiguration erstellen starten
                # pass
            elif choice == '2':
                # Konfiguration löschen
                delete_last_lines(1)
                confic_nr = input(f'Gib die Nummer der konfiguration an. Abbrechen, mit falscher Eingabe.\n')
                if confic_nr in options and confic_nr not in ('1', '2'):
                    config_name = configuration_names[int(confic_nr) - 3]
                    del data[config_name]
                    configuration_names.remove(config_name)
                    json.dump(data, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

                    print('gelöscht')
                    time.sleep(0.5)
                return False
            else:  # konfiguration je nach eingabe anzeigen bearbeiten
                config_name = configuration_names[int(choice) - 3]
                clear_console()
                print_configuration(data, forms, config_name)  # gibt konfiguration aus

                print('Enter zum zurückgehen, weiter mit anderer Eingabe')
                # while True:
                back = input()
                if back == '':
                    return False

                configure_game(forms, data, config_name)

                return False

        elif choice in break_options:  # direkt abbrechen
            print('break')
            return True
        else:
            delete_last_lines(1)  # sonst eingabe löschen (indem curser eine zeile hoch geht und diese lösche) und neu abfragen, bis gültiger wert
