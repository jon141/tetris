#import json
import random
import copy
import msvcrt
import os
import threading
import time


#forms = json.load(open('forms.json', 'r', encoding='utf-8'))
#data = json.load(open('data.json', 'r', encoding='utf-8'))

class Tetris:
    def __init__(self, rows: int, cols: int, background: str, foreground: str, forms: dict, form_select: list): #evtl. noch gamemode
        # übergebene Variablen
        self.rows = rows
        self.cols = cols
        self.backgound = background
        self.foreground = foreground
        self.forms = forms
        self.form_select = form_select

        # Game Values
        self.score = 0
        self.gameover = False
        self.form_rotation_level = [None, None] # Die Aktuelle Tetris-Form mit dem Grad der Drehung im Feld
        self.coordinates = [None, None] # x und y Koordinaten des aktuellen fallenden Steins (linke obere ekce)
        self.recentlyspawned = True
        # evtl. noch Höhe und Breite, weil das braucht man auch später noch, geht aber auch mit self.form_rotation_level
        ###self.current_form = None #Die aktuelle Form mit Drehung und ohne unnötige Zeilen

        # Felder     (zu Beginn alle leer)
        self.falling_tetris_field = self.create_empty_field() #self.create_field() # Enthält nur aktuellen Tetris-Stein mit Position und Rotation-Level
        self.existing_block_field = self.create_empty_field() # Alle Blöcke, die Fest sind und schon plaziert wurden
        self.intersection_field = self.create_empty_field() # SChnittmenge zwischen den beiden anderen Feldern, wird in printbares Feld übersetzt

        #print('starting')
        #print(self.existing_block_field)
    def create_empty_field(self):
        return [[0 for col in range(self.cols)] for row in range(self.rows)]

    def print_intersection_field(self):
        #print(20*'-')
        #print('-------------existing Block field-----------------------------')
        #print(self.existing_block_field)
        #print('-----------------------falling tetris field------------------')
        #print(self.falling_tetris_field)
        #print('---------------------------intersection field-------------------')
        #print(self.intersection_field)
        frame_size = (self.cols * 2 + 3) # optional *3, wenn unten zwei leerzeichen
        margin = 14

        field = f'''{20*'_'}
\033[31mT E T R I S   Score: {self.score}\033[0m
{margin*' '+ frame_size * '_'}\n'''
        #print(f'\033[31mT E T R I S   Score: {self.score}\033[0m')
        #print(field)
        #print(margin*' '+ frame_size * '_')
        for row in self.intersection_field:
            #print(row)
            row_string = margin*' '+'| '
            for col in row:
                #print(col)
                if col == 1:
                    row_string += f"\033[32m{self.foreground} \033[0m"#\033[44m  \033[0m
                elif col == 3:
                    row_string += f"\033[34m{self.foreground} \033[0m"  # \033[44m  \033[0m
                else:
                    row_string += f"{self.backgound} "
            row_string += '|'
            #print(row_string)
            field += f'{row_string}\n'
            #print('| ' +str(row).replace(',', ' ').replace('[', '').replace(']', '').replace('0', self.symbol_background).replace('1', self.symbol_tetris) + ' |')
        #print(margin*' '+frame_size * '‾')
        field += (margin*' '+frame_size * '‾')

        print(field)

    def create_intersection_field(self):
        self.intersection_field = copy.deepcopy(self.existing_block_field)
        for row_index, row in enumerate(self.falling_tetris_field):
            for col_index, col in enumerate(row):
                if col == 1:
                    self.intersection_field[row_index][col_index] = 3

    def expand_existing_block_field(self, respawn):
        for row_index, (row_1, row_2) in enumerate(zip(self.existing_block_field, self.falling_tetris_field)):
            for col_index, (col_1, col_2) in enumerate(zip(row_1, row_2)):
                if col_1 == 1 or col_2 == 1:
                    self.existing_block_field[row_index][col_index] = 1
        if respawn == True:
            self.spawn_tetris() #?
        self.check_rows_for_delete()

    def spawn_tetris(self):
        self.recentlyspawned = True
        def set_recentlyspawned_False():
            time.sleep(1.5)
            self.recentlyspawned = False
        thread = threading.Thread(target=set_recentlyspawned_False)
        thread.start()
        #print(self.forms, 'forms')
        random_form = random.choice(self.form_select) #Zufälligen Formnamen aus Auswahl auswählen
        tetris_form = self.forms[random_form] # Matrix der Form aus dem Dict hohlen
        #self.testprint_field_form(tetris_form)
        #tetris_form = [row for row in tetris_form if not all(cell == 0 for cell in row)] # entfernt die lehren reihen
        self.form_rotation_level = [random_form, 0] #Zufällig generierter Name der Form und Rotation-Status, der 0 ist

        widht = len(tetris_form[0]) # Breite der Tetris-Form
        x_position = (self.cols // 2) - (widht // 2)  # x-Postion für den Spawn soll in der Mitte des Feldes sein auf höhe 0

        self.coordinates = [x_position, 0]

        self.falling_tetris_field = self.create_empty_field()

        for counter, row in enumerate(tetris_form):
            self.falling_tetris_field[counter][x_position:x_position + widht] = row

        if self.check_for_ueberschneidung(self.existing_block_field, self.falling_tetris_field) == True:
            self.gameover = True
            self.expand_existing_block_field(False)
            self.create_intersection_field()
            self.print_intersection_field()
        #self.testprint_field_form(self.falling_tetris_field)
        self.score += 10

    def rotate_tetris_in_falling_field(self): ### !!!Wichtig: es darf nur rotiert werden, wenn nach rechts und unten noch genug Platz ist
        x_position, y_position = self.coordinates # Koordinaten im falling field
        #print(x_position, y_position)
        form_name, rotation_level = self.form_rotation_level
        #print(form_name, rotation_level, 'values')
        #widht = len(self.rotate_form(form, rotation_level)[0]) # höhe und Breite des Tetris
        #height = len(self.rotate_form(form, rotation_level))

        tetris_to_insert = self.rotate_form(form_name, rotation_level+1)
        #print(tetris_to_insert, 'tetris to insert')

        new_falling_tetris_field = self.create_empty_field()

        widht = len(tetris_to_insert[0])
        height = len(tetris_to_insert)
        #print(widht, 'width')

        #print('x', (self.cols - x_position - widht), f'cols{self.cols}, x {x_position}, width {widht}', (self.cols - y_position - height) > 0)
        #print('y', (self.rows - y_position - height), f'rows{self.rows}, x {y_position}, width {height}')

        if (self.rows - y_position - height >= 0) and (self.cols - x_position - widht >= 0):
            for counter, row in enumerate(tetris_to_insert): # links oben ist Punkt 0|0
                new_falling_tetris_field[counter + y_position][x_position:x_position + widht] = row

            if self.check_for_ueberschneidung(self.existing_block_field, new_falling_tetris_field) == False:
                self.falling_tetris_field = new_falling_tetris_field

                #self.testprint_field_form(self.falling_tetris_field)

                self.form_rotation_level[1] += 1
                self.create_intersection_field()
                self.clear_console()

                self.print_intersection_field()
            else:
                pass
                #print('Drehen ist nicht möglich, weil es sonst zu einer Übershneidung kommt')
        else:
            pass
            #print('Drehen nicht möglich, weil der Platz nicht reicht')

        #backup = self.falling_tetris_field


    def check_rows_for_delete(self):
        #self.existing_block_field = [
        #    [0 for _ in range(self.cols)]
        #    if all(cell == 1 for cell in row) else row
        #    for row in self.existing_block_field
        #]

        for index, row in enumerate(self.existing_block_field):
            if all(element == 1 for element in row): # alle elemente 1, dann reihe löschen
                del self.existing_block_field[index]
                self.existing_block_field.insert(0, [0 for col in range(self.cols)])  # oben neue, leere Reihe hinzufügen
                self.score += self.cols * 30

    def move_down(self):
        backup = copy.deepcopy(self.falling_tetris_field)
        x_position, y_position = self.coordinates # Koordinaten im falling field
        form_name, rotation_level = self.form_rotation_level
        #widht = len(self.rotate_form(form_name, rotation_level)[0]) # höhe und Breite des Tetris
        height = len(self.rotate_form(form_name, rotation_level))

        del self.falling_tetris_field[-1] # unterste Reihe entfernen
        self.falling_tetris_field.insert(0, [0 for col in range(self.cols)]) #oben neue, leere Reihe hinzufügen

        #Wenn noch Platz für eine Verschiebung gibt und es keine Kollision gibt
        if (self.rows - y_position - height > 0) and self.check_for_ueberschneidung(self.existing_block_field, self.falling_tetris_field) == False:
            #print(self.rows - y_position - height)
            self.coordinates[1] += 1 #y-koordinate um 1 erhöhen
            self.create_intersection_field()
            self.clear_console()

            self.print_intersection_field()
        else:
            self.falling_tetris_field = backup
            #print('unten angekommen, oder überschneidung: Feld der exestierenden Blöcke muss erweitert werden.')
            self.expand_existing_block_field(True)

        #self.testprint_field_form(self.falling_tetris_field)
        #print('')


    def move_right(self):
        x_position, y_position = self.coordinates
        form_name, rotation_level = self.form_rotation_level
        widht = len(self.rotate_form(form_name, rotation_level)[0])

        backup = copy.deepcopy(self.falling_tetris_field)
        #print(widht, 'width')
        if x_position < self.cols - widht:
            for row in self.falling_tetris_field:
                del row[-1]
                row.insert(0, 0)
            #print('Verschiebung nach rechts')
            if self.check_for_ueberschneidung(self.existing_block_field, self.falling_tetris_field):
                self.falling_tetris_field = backup
                #print('Geht nicht wegen übershneidung right')
            else:
                self.coordinates[0] += 1
                self.create_intersection_field()
                self.clear_console()

                self.print_intersection_field()
        else:
            pass
            #print('Nicht genug Platz')

        #self.testprint_field_form(self.falling_tetris_field)


    def move_left(self):
        x_position, y_position = self.coordinates
        backup = copy.deepcopy(self.falling_tetris_field)

        if x_position != 0:
            for row in self.falling_tetris_field:
                del row[0]
                row.append(0)
            if self.check_for_ueberschneidung(self.existing_block_field, self.falling_tetris_field):
                self.falling_tetris_field = backup
                #print('Geht nicht wegen überschneidung left')

            else:
                self.coordinates[0] -= 1
                self.create_intersection_field()
                self.clear_console()

                self.print_intersection_field()

        else:
            pass
            #print('nicht genug Platz')



    def check_for_ueberschneidung(self, placed_field, falling_field):
        for placed_row, falling_row in zip(placed_field, falling_field): #geht jede Reihe und Spalte durch in beiden feldern und Vergleicht diese auf einsen
            #print(placed_row, falling_row)
            for col_in_placed_row, col_in_falling_row in zip(placed_row, falling_row):
                #print('1', col_in_placed_row, col_in_falling_row)
                if col_in_placed_row == 1 and col_in_falling_row == 1:
                    #print('True')
                    return True
        #print('Überschneidung == False')
        return False


    def rotate_form(self, form_name, level):
        form = self.forms[form_name]
        for l in range(level % 4):
            form = [list(reversed(k)) for k in zip(*form)]
        return form


    def testprint_field_form(self, field_form):
        for row in field_form:
            row_string = ''
            for col in row:
                if col == 1:
                    row_string += f'\033[31m {col}\033[0m'
                else:
                    row_string += f' {col}'
            print(row_string)
    # def translate matrix (print)

    def get_key_action(self):
        #key = msvcrt.getch()  # Liest die gedrückte Taste
        return msvcrt.getch().decode('utf-8', errors='ignore')

    def clear_console(self):
        os.system('cls')
        print("\033[H\033[J", end='')

    def __str__(self):
        return f'\033[0mKonfigurationsdaten: \n - rows: \033[31m{self.rows}\033[0m \n - cols: \033[31m{self.cols}\033[0m \n - background: \033[31m{self.backgound}\033[0m \n - foreground: \033[31m{self.foreground}\033[0m \n - form select: \033[31m{self.form_select}\033[0m'

#konfigurationsdaten = data['normal']

##tetris = Game(rows=konfigurationsdaten['rows'], cols=konfigurationsdaten['cols'],
#                        background=konfigurationsdaten['symbol-background'],
#                        foreground=konfigurationsdaten['symbol-tetris'], forms=forms,
#                        form_select=konfigurationsdaten['forms'])
#
#tetris.spawn_tetris()
##tetris.rotate_tetris_in_falling_field()
##tetris.rotate_tetris_in_falling_field()
##tetris.rotate_tetris_in_falling_field()
##tetris.rotate_tetris_in_falling_field()
#
#for i in range(3):
#    tetris.move_down()
#tetris.rotate_tetris_in_falling_field()
#
#for n in range(12):
#    tetris.move_left()
#
#tetris.rotate_tetris_in_falling_field()
#tetris.print_intersection_field()
##tetris.move_down()
##tetris.testprint_field_form(tetris.existing_block_field)
##tetris.testprint_field_form(tetris.rotate('Ll', 0))
##print('')
##tetris.testprint_field_form(tetris.rotate('Ll', 1))
##print('')
##
##tetris.testprint_field_form(tetris.rotate('Ll', 2))
##print('')
##
##tetris.testprint_field_form(tetris.rotate('Ll', 3))