
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
        print_form(form, 3, data)
        print(15*'_')


def print_form(form, abstandl, data):
    for row in form:
        row_string = abstandl*' '
        for col in row:
            # print(col)
            if col == 1:
                row_string += f"\033[32m{data['konfiguration']['symbol-tetris']} \033[0m"  # \033[44m  \033[0m
            elif col == 0:
                row_string += f"\033[34m{data['konfiguration']['symbol-background']} \033[0m"  # \033[44m  \033[0m
        print(row_string)

def form_konfigurations_eingabe(form_names):
    while True:
        formen = input('\033[0mFormen: (gib die Nummern ein.) (Beispiel: 1, 2, 3, 4)\033[31m')
        formen = formen.replace(' ', '')
        formen = list(map(int, formen.split(',')))
        print(formen)
        form_choice = []
        try:
            for number in formen:
                form_choice.append(form_names[number-1])
            return form_choice
        except:
            print('Error. Try again.')

def row_col_valid_checker(placeholder):
    while True:
        eingabe = input(f'\033[0m{placeholder} des Spielfelds: \033[31m')
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
    abbruch = input('Break with enter, continue with anderer Eingabe\n')
    if abbruch == '':
        return None

    #print("\033[H", end="")


    rows = row_col_valid_checker('Reihen')
    cols = row_col_valid_checker('Spalten')
    backgound_symbol = input('\033[0mHintergrundsymbol: \033[31m')
    tetris_symbol = input('\033[0mTetris-Symbol: \033[31m')
    form_names = list(forms.keys())
    print(form_names, 'ööö')
    print('\033[0m')
    #for form in form_names:
    #    print_form(forms[form], 5)

    for number, name in enumerate(form_names):
        print(number + 1, ':', name)
        form = forms[name]
        print_form(form, 3, data)
        print(15*'_')

    form_choice_list = form_konfigurations_eingabe(form_names)
    bestaetigung = input('Bestätige deine Konfiguration, oder breche ab mit . ab')
    if bestaetigung == '.':
        return
    else:
        data['konfiguration']['rows'] = rows
        data['konfiguration']['cols'] = cols
        data['konfiguration']['symbol-tetris'] = tetris_symbol
        data['konfiguration']['symbol-background'] = backgound_symbol
        data['konfiguration']['forms'] = form_choice_list

        json.dump(data, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)