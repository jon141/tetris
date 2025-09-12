import json
import time


def get_form_input():
    print('''
Gib deine neue Form ein:
    - Benutze 0 für lehre Felder
    - 1 für ausgefüllte deiner Form
    - Starte neue Zeile mit Enter
    - Breche ab, in dem du auf eine leere, oder mit "-" gefüllte Zeile Enter drückst. 

    Beispiel:\033[31m
    0 1 0
    0 1 0
    1 1 1 
    \n\033[37m 
Deine Eingabe: \n\033[31m''')


    rows = []
    row = ''
    while True:
        row = input()
        if row not in ('-', ''):
            row = row.replace(' ', '')
            rows.append(row)
        else:
            break

    form_list = []

    try: # prüft, ob der input gültig ist

        for row in rows:
            row = list(row)
            row = [int(x) for x in row]

            for n in row:
                if n not in [0, 1]:
                    print('\033[37m invalid input')
                    return None

            form_list.append(row)
        print('\033[37m ') # farbe zurücksetzen
        return form_list
    except ValueError:
        print('\033[37m invalid input')
        return None


def form_gueltig_machen(form_list):

    try:
        longest_row = max(len(row) for row in form_list)

        for row_ in form_list:
            difference = longest_row - len(row_)
            #print(difference)
            row_.extend([0] * difference) # reihen mit 0 auffüllen, bis alle gleichlang sind

        return form_list

    except:
        print('Ungültige Eingabe.')
        return False





def add_form(forms, formen_hinzufuegen_text):
    while True:
        print("\033[H\033[J", end='')

        print(f'''\033[32m
{formen_hinzufuegen_text}  \033[0m  ''')


        form_list = get_form_input()
        #if form_list is False:
        #    return
        if form_list is not None:
            break

    form_list = form_gueltig_machen(form_list)
    if form_list != False:
        print("\nDeine eingegebene Form:")
        for row in form_list:
            s = ''
            for element in row:
                s += f'{str(element)}  '
            print(s)

        while True:
            name = input("\nGib einen Namen für die Form ein und drücke Enter (Abbruch mit ., oder ESC): ")
            if name in ('.', '^[', '\x1b'):
                break
            if name in forms:
                print("Der Name existiert bereits. Bitte wähle einen anderen. Bereits existierende kannst du in Punkt 3 anschauen.")
            else:
                forms[name] = form_list
                json.dump(forms, open('forms.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

                print(f"\nDie Form '{name}' wurde erfolgreich hinzugefügt!")
                time.sleep(1)
                break
