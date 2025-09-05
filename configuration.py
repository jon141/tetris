
import json
def print_aktuelle_konfiguration(data, forms):
    values_dict = data['konfiguration']
    print(f'''\033[32m
     _  __            __ _                       _   _             
    | |/ /           / _(_)                     | | (_)            
    | ' / ___  _ __ | |_ _  __ _ _   _ _ __ __ _| |_ _  ___  _ __  
    |  < / _ \| '_ \|  _| |/ _` | | | | '__/ _` | __| |/ _ \| '_ \  
    | . \ (_) | | | | | | | (_| | |_| | | | (_| | |_| | (_) | | | |
    |_|\_\___/|_| |_|_| |_|\__, |\__,_|_|  \__,_|\__|_|\___/|_| |_|
                            __/ |                                  
                           |___/                                   
    \033[0m
    
    Aktuell:
        Reihen: \033[31m{values_dict['rows']}\033[0m
        Spalten: \033[31m{values_dict['cols']}\033[0m
        Hintergrundsymbol: \033[31m{values_dict['symbol-background']}\033[0m
        Tetris-Symbol: \033[31m{values_dict['symbol-tetris']}\033[0m
        Formen: \033[31m{", ".join(values_dict['forms'])}\033[0m

Alle existierenden Formen: 
''')
    form_names = list(forms.keys())
    for number, name in enumerate(form_names):
        print(number + 1, ':', name)
        form = forms[name]
        print_form(form, 3, values_dict['symbol-tetris'], values_dict['symbol-background'])
        print(15*'_')


def print_form(form, abstandl, symbol_tetris, symbol_background):
    for row in form:
        row_string = abstandl*' '
        for col in row:
            # print(col)
            if col == 1:
                row_string += f"\033[32m{symbol_tetris} \033[0m"  # \033[44m  \033[0m
            elif col == 0:
                row_string += f"\033[34m{symbol_background} \033[0m"  # \033[44m  \033[0m
        print(row_string)

def form_konfigurations_eingabe(form_names):
    while True:
        formen = input('\033[0mFormen: (gib die Nummern ein.) (Beispiel: 1, 2, 3, 4)\033[31m')
        try:
            formen = formen.replace(' ', '')
            formen = list(map(int, formen.split(',')))
            print(formen)
            form_choice = []

            for number in formen:
                form_choice.append(form_names[number-1])
            return form_choice
        except:
            print('Error. Try again.')

def row_col_valid_checker(placeholder):
    while True:
        eingabe = input(f'\033[0m{placeholder} des Spielfelds: \033[31m')

        if eingabe in ('^[', '\x1b'):
            return None
        else:
            try:
                eingabe = int(eingabe)
                return eingabe
            except:
                print('Falsche Eingabe')


def spiel_konfigurieren(forms, data):
    #print('''
    #Konfiguriere dein eigenes Spiel:
    #Wie viele Reihen? Wie viele Spalten? Hintergrundsymbol? Tetrissymbol? Formen?
    #Du kannst nach Ende der Eingabe die Konfiguration verwerfen.
    #''')
    #print('Deine aktuelle Konfiguration:')

    print_aktuelle_konfiguration(data, forms)
    print('\033[?25h', end='')
    abbruch = input('Break with enter or ESC (mit ESC, dann Enter kann man immer abbrechen), continue with anderer Eingabe\n')
    if abbruch in ('', '^[', '\x1b'):
        print('\033[?25l', end='')
        return None

    #print("\033[H", end="")

    # durch die is None abfrage bei jeder eingabe abbrechbar
    rows = row_col_valid_checker('Reihen')
    if rows is None: # ist none, wenn abbruchbedingung ESC erfüllt ist
        return None

    cols = row_col_valid_checker('Spalten')
    if cols is None:
        return None

    # auch abbrechbar
    background_symbol = input('\033[0mHintergrundsymbol: \033[31m')
    if background_symbol in ('^[', '\x1b'):
        return None

    while True: # wenn vorder und hintergrund nicht gleich lang ist, verschiebt sich alles im spielfeld
        tetris_symbol = input('\033[0mTetris-Symbol: \033[31m')
        if tetris_symbol in ( '^[', '\x1b'):
            return None
        if len(tetris_symbol) != len(background_symbol):
            print('Das Tetris- und Hintergrundsymbol müssen gleich viele Zeichen beinhalten.')
        else: break

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
            background_color = int(input(f'\033[0mHintergrundfarbe ({colors[0]}0, {colors[1]}1, {colors[2]}2, {colors[3]}3, {colors[4]}4, {colors[5]}5, {colors[6]}6): \033[31m'))
            if str(background_color) in ( '^[', '\x1b'):
                return None
            if background_color in (0, 1, 2, 3, 4, 5, 6):
                break
            else:
                print('\033[37mFalsche Eingabe.')
        except:
            print('\033[37mFalsche Eingabe.')


    form_names = list(forms.keys())

    #print(form_names, 'ööö')
    print('\033[0m')
    #for form in form_names:
    #    print_form(forms[form], 5)

    for number, name in enumerate(form_names):
        print(number + 1, ':', name)
        form = forms[name]
        print_form(form, 3, tetris_symbol, background_symbol) # symbole der neuen konfiguration übergeben
        print(15*'_')

    form_choice_list = form_konfigurations_eingabe(form_names)
    bestaetigung = input('Bestätige deine Konfiguration, oder breche ab mit . ab')
    print('\033[?25l', end='')

    if bestaetigung == '.':
        return None
    else:
        data['konfiguration']['rows'] = rows
        data['konfiguration']['cols'] = cols
        data['konfiguration']['symbol-tetris'] = tetris_symbol
        data['konfiguration']['symbol-background'] = background_symbol
        data['konfiguration']['forms'] = form_choice_list
        data['konfiguration']['background-color'] = background_color

        json.dump(data, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)