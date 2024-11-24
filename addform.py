import json
def get_input_form():
    form_list = []
    eingabe = input('''
Gib deine neue Form ein:
    - Benutze 0 für lehre Felder
    - 1 für ausgefüllte
    - Starte neue Zeile mit /
    - Breche jetzt ab mit . oder enter 
    
Beispiel 111/111/111 \n\n''')
    if eingabe == '.' or eingabe == '':
        print('None')
        return False

    try:
        eingabe = eingabe.replace(' ', '')
        rows = eingabe.split('/')
        # print(rows)
        for row in rows:
            row = list(row)
            row = [int(x) for x in row]

            for n in row:
                if n not in [0, 1]:
                    print('invalid input')
                    return None

            form_list.append(row)
        return form_list
    except ValueError:
        print('invalid input')
        return None


def form_gueltig_machen(form_list):
    longest_row = 0
    for row in form_list:
        if len(row) > longest_row:
            longest_row = len(row)

    for row_ in form_list:
        difference = longest_row - len(row_)
        #print(difference)
        row_.extend([0] * difference)

    #if len(form_list) < longest_row: #macht Form mit Nullen quadtratisch, aber braucht man nicht
    #    form_list.append([0] * longest_row)

    return form_list


def add_form(forms, formen_hinzufuegen_text):
    while True:
        print("\033[H\033[J", end='')

        print(f'''\033[32m
{formen_hinzufuegen_text}  \033[0m  ''')


        form_list = get_input_form()
        if form_list is False:
            return
        elif form_list is not None:
            break

    form_list = form_gueltig_machen(form_list)

    print("\nDeine eingegebene Form:")
    for row in form_list:
        s = ''
        for element in row:
            s += f'{str(element)}  '
        print(s)

    while True:
        name = input("\nGib einen Namen für die Form ein und drücke Enter (Abbruch mit .): ")
        if name == '.':
            break
        if name in forms:
            print("Der Name existiert bereits. Bitte wähle einen anderen. Bereits existierende kannst du in Punkt 3 anschauen.")
        else:
            forms[name] = form_list
            json.dump(forms, open('forms.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

            print(f"Die Form '{name}' wurde erfolgreich hinzugefügt!")
            break
