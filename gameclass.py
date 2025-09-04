import json
import random
import copy
import os
import threading
import time
import math
import traceback
import asciiart
from keyboard_input import KeyboardInput


###data = json.load(open('data.json', 'r', encoding='utf-8'))

# Idee: Farben nicht komplett random, nie 2x die gleiche, oder wenn eine Farbe kommt muss mind 2x eine andere kommen (speicherung in liste mit letzte 2 Farben)
colors = [ # Farbe, der plazierten Blöcke kann entfernt werden, damit es nicht in der gleichen Farbe spawnt
            "\033[31m",
            "\033[32m",
            "\033[33m",
            "\033[34m",
            "\033[35m",
            "\033[36m",
            "\033[37m"
        ]


class Tetris:
    def __init__(self, rows: int, cols: int, background: str, background_color: str, foreground: str, forms: dict, form_select: list):#, placed_color: str): #evtl. noch gamemode
        # konfigurationsvariablen
        self.rows = rows #Reihen
        self.cols = cols # spalten
        self.backgound = background # Symbol des Hintergrunds
        self.backgound_color = background_color
        self.foreground = foreground # Symbol des Vordergrunds -> also alle Tetris Steine, (Fallend und plaziert)
        self.forms = forms # alle Tetris Formen; Dictionary
        self.form_select = form_select # auswahl der Formen aus Dictionary nach nummer


        # Spielvariablen
        self.score = 0
        self.gameover = False

        self.form_rotation_level = [None, None] # Die Aktuelle Tetris-Form mit dem Grad der Drehung im Feld
        self.coordinates = [None, None] # x und y Koordinaten des aktuellen fallenden Steins (linke obere ekce)
        self.recentlyspawned = True # Wenn ein Stein neu spawnt, soll er nicht direkt fallen. wenn True wird das fallen plaziert (verschieben geht); wird nach ablauf einer Zeit automatisch False gesetzt

        self.quit_game = False # spiel kann manuell mit eingabe b q esc (break) abgebrochen werden

        self.current_color_index = None
        # evtl. noch Höhe und Breite, weil das braucht man auch später noch, geht aber auch mit self.form_rotation_level
        ###self.current_form = None #Die aktuelle Form mit Drehung und ohne unnötige Zeilen

        # Felder (zu Beginn alle leer)
        self.falling_tetris_field = self.create_empty_field() #self.create_field() # Enthält nur aktuellen Tetris-Stein mit Position und Rotation-Level
        self.existing_block_field = self.create_empty_field() # Alle Blöcke, die Fest sind (schon plaziert wurden)
        self.intersection_field = self.create_empty_field() # SChnittmenge zwischen den beiden anderen Feldern, wird in printbares Feld übersetzt



    def start_game(self):

        time_start = time.time()

        def clock():  # lässt die Steine FAllen, mit ansteigender fallgeschwindigkeit
            # simulation mit Exponentiellem wachstum
            start_interval = 1  # sekunden
            interval_min = 0.15  # damit es nicht zu schnell wird, eine grenze
            k = 0.00095  # proportionalitätskonstante

            while not self.gameover:
                if self.recentlyspawned is False and self.quit_game is False:
                    x = self.score * k
                    abnahme = -math.exp(x - 5.6) + start_interval
                    if abnahme >= interval_min:
                        interval = abnahme
                    else:
                        interval = interval_min
                    # interval = 1.5 - Game.score
                    time.sleep(interval)
                    # print(Game.recentlyspawned)
                    if self.recentlyspawned is True: # wenn neu gespawnt, dann erstmal pause, nicht direkt runter
                        time.sleep(1)
                        # print('recently spawned true')
                    if self.quit_game is False and self.recentlyspawned is False:  # sonst kommt es zu einer Verzögerung und das spielfeld wird nach beenden des Spiels nochmal geprintet
                        self.move_down()
                if self.quit_game is True or self.gameover:
                    break


        # einrichung des spiels und der ausgabe

        self.clear_console() # erst konsole frei macen
        ###self.create_intersection_field() #   ### ???
        ###self.clear_console() ### ???
        self.print_intersection_field() # leeres feld printen
        time.sleep(2) # längere pause wegen start
        self.spawn_tetris() # ersten stein spawnen
        self.create_intersection_field() # schnittfeld erstellen
        self.clear_console() # konsole leeren
        self.print_intersection_field() # schnittfeld ausgeeben



        def key_loop():
            with KeyboardInput() as kb:
                while not self.gameover:  # Spiellogik: solange das spiel nicht verloren ist, oder nicht abgebrochen wurde
                    if kb.kbhit():
                        key = kb.getch()
                        if key in ['a', 'A','\x1b[D']: # Left
                            self.move_left()
                        elif key in ['d', 'D', '\x1b[C']: # Right
                            self.move_right()
                        elif key in ['w', 'W', '\x1b[A']: # Up
                            self.rotate_tetris_in_falling_field()
                        elif key in ['s', 'S', '\x1b[B'] and self.recentlyspawned is False: # Down
                            self.move_down()
                        elif key in ['b', '\x1b', 'q']:  # ESC; b: break; q: quit
                            self.quit_game = True
                            self.clear_console()
                            break
                    time.sleep(0.005)

        # Threads definieren: falling clock und keyinput
        clock_thread = threading.Thread(target=clock)
        key_loop_thread = threading.Thread(target=key_loop)

        #Starten
        clock_thread.start()  # starten
        key_loop_thread.start() #  starten

        # Warten bis Threads fertig sind
        clock_thread.join()
        key_loop_thread.join()
                
        self.end_game(starttime=time_start)

    def end_game(self, starttime):

        # nach Ende des Spiels highscore und gametime aktualisieren

        data = json.load(open('data.json', 'r', encoding='utf-8'))

        if self.score > data['highscore']:
            data['highscore'] = self.score
        game_time = time.time() - starttime
        data['gametime'] += game_time
        data['game-counter'] += 1
        json.dump(data, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

        self.clear_console()
        self.clear_console()
        self.print_intersection_field()
        print(f'\033[31m{asciiart.gameover}\033[0m')

        input("Enter zum beenden...")  # Bei Enter zurück zur Spielauswahl


    def create_empty_field(self): # erstelle eine Zweidimensionale Liste aus den angegebenen reihen und spalten: zb [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ]
        return [[0 for col in range(self.cols)] for row in range(self.rows)]

    def print_intersection_field(self):
        frame_size = (self.cols * 2 + 3) # optional *3, wenn unten zwei leerzeichen
        margin = 14

        field = f'''{20*'_'}
\033[31m\033[1mT E T R I S   Score: {self.score}\033[0m
{margin*' '+ frame_size * '_'}\n'''

        for row in self.intersection_field: # für jede reihe im Feld der SChnittmenge
            row_string = margin*' '+'| '    # wird erstmal ein Abstand zur linken seite und der Rahmen erstellt
            for col in row:                 # für jeden Eintrag in der Reihe
                #print(col)
                if col in [1, 2, 3, 4, 5, 6, 7]: # wird geschaut, welche Farbe die Tetrissteine im Feld haben
                    row_string += f"{colors[col-1]}{self.foreground} \033[0m"  # \033[44m  \033[0m

                else:
                    row_string += f"{colors[self.backgound_color]}{self.backgound} "  # außer der Eintrag ist nur Hintergrund
            row_string += '\033[37m|' # RAhmen auf der anderen Seite schließen
            #print(row_string)
            field += f'{row_string}\n' # den String der reihe zum string des gesammten Feldes hinzufügen

        field += (margin*' '+frame_size * '‾')      # rahmen nach unten abschließen

        print(field)

    def create_intersection_field(self):
        self.intersection_field = copy.deepcopy(self.existing_block_field)  # das intersection_field (schnittmenge) wird mit existing_block_field  (Plazierte steine feld) überschrieben (Deepcopy, weil sonst Doof)
        for row_index, row in enumerate(self.falling_tetris_field):     # jede reihe im falling_tetris_field einzeln
            for col_index, col in enumerate(row):
                if col != 0:
                    self.intersection_field[row_index][col_index] = self.current_color_index + 1

    def expand_existing_block_field(self, respawn):
        for row_index, (row_1, row_2) in enumerate(zip(self.existing_block_field, self.falling_tetris_field)):
            for col_index, (col_1, col_2) in enumerate(zip(row_1, row_2)):
                if col_1 in [1, 2, 3, 4, 5, 6, 7]:
                    self.existing_block_field[row_index][col_index] = col_1 # hier ist überlappungsfehler der farben

                elif col_2 == 1:
                    self.existing_block_field[row_index][col_index] = self.current_color_index + 1 # hier ist überlappungsfehler der farben

        if respawn:
            self.spawn_tetris() #?
        self.check_rows_for_delete()

    def spawn_tetris(self):

        self.check_rows_for_delete()

        self.current_color_index = random.randint(0, 6)

        self.recentlyspawned = True
        def set_recentlyspawned_False():
            time.sleep(0.3)
            self.recentlyspawned = False
        thread = threading.Thread(target=set_recentlyspawned_False)
        #print(self.recentlyspawned, 20*'--')
        thread.start()
        #print(self.recentlyspawned, 20*'++')

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

        if self.check_for_ueberschneidung(self.existing_block_field, self.falling_tetris_field): # wenn es beim spawn eine überschneidung gibt, ist das spiel vorbei
            self.gameover = True
            self.expand_existing_block_field(False)
            self.create_intersection_field()
            self.print_intersection_field()
        #self.testprint_field_form(self.falling_tetris_field)
        self.score += 10
        self.create_intersection_field()
        self.clear_console()
        self.print_intersection_field()

    def rotate_tetris_in_falling_field(self): ### !!!Wichtig: es darf nur rotiert werden, wenn nach rechts und unten noch genug Platz ist
        x_position, y_position = self.coordinates # Koordinaten im falling field
        #print(x_position, y_position)
        form_name, rotation_level = self.form_rotation_level

        tetris_to_insert = self.rotate_form(form_name, rotation_level+1) # der Tetris stein, mit rotierter form

        new_falling_tetris_field = self.create_empty_field()

        widht = len(tetris_to_insert[0])
        height = len(tetris_to_insert)


        if (self.rows - y_position - height >= 0) and (self.cols - x_position - widht >= 0): # die erste bedingung schließt aus, dass der stein beim drehen nach ohen aus dem spielfeld rutscht, die zweite, ob das nach rechts passiert
            for counter, row in enumerate(tetris_to_insert): # links oben ist Punkt 0|0
                new_falling_tetris_field[counter + y_position][x_position:x_position + widht] = row     # der rotierte stein wird in ein neues falling field eingefügt

            if not self.check_for_ueberschneidung(self.existing_block_field, new_falling_tetris_field): # wenn es keine überschneidung gibt, ist drehung in ordnung und das feld kann übernommen werden
                self.falling_tetris_field = new_falling_tetris_field

                #self.testprint_field_form(self.falling_tetris_field)

                self.form_rotation_level[1] += 1
                self.create_intersection_field()
                self.clear_console()

                self.print_intersection_field()
            else:  # sonst soll nichts passieren
                pass
        else:
            pass


    def check_rows_for_delete(self):
        for index, row in enumerate(self.existing_block_field):
            if all(element in [1, 2, 3, 4, 5, 6, 7] for element in row): # alle elemente ein stein sind (also nicht einmal hintergrund), dann reihe löschen
                del self.existing_block_field[index] # reihe löschen
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
        widht = len(self.rotate_form(form_name, rotation_level)[0]) # beim bewegen nach rechts ist wichtig, wie breit der fallende stein in der aktuellen drehung ist

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

        if x_position != 0: # bei null gehts nicht weiter nach links
            for row in self.falling_tetris_field: #in jeder reihe von falling_tetris_field, das erste element löschen und rechts hinten einfügen -> verschiebt tetris stein nach links
                del row[0]
                row.append(0)
            if self.check_for_ueberschneidung(self.existing_block_field, self.falling_tetris_field): # wenn es eine überschneidung gibt, darf (kann) der Tetris stein nicht nach links bewegt werden
                self.falling_tetris_field = backup  # dann die verschiebung durch das backup rückgängig machen
                #print('Geht nicht wegen überschneidung left')

            else: # sonst die koordinaten verändern und das durch die änderung (verschiebung) entstandene Feld erstellen und ausgeben
                self.coordinates[0] -= 1
                self.create_intersection_field()
                self.clear_console()

                self.print_intersection_field()

        else:
            pass
            #print('nicht genug Platz')


    def check_for_ueberschneidung(self, placed_field, falling_field): # auf englishc check for overlap
        for placed_row, falling_row in zip(placed_field, falling_field): #geht jede Reihe und Spalte durch in beiden feldern und prüft, ob zwei tetris steine auf dem gleichen feld liegen würden
            #print(placed_row, falling_row)
            for col_in_placed_row, col_in_falling_row in zip(placed_row, falling_row):
                #print('1', col_in_placed_row, col_in_falling_row)
                if col_in_placed_row != 0 and col_in_falling_row != 0: # wenn beides nicht 0 ist, ist es eine überschneidung zwischen [1, 2, 3, 4, 5, 6, 7]
                    #print('True')
                    return True

        return False #


    def rotate_form(self, form_name, level): # nimmt die ursprüngliche form und dreht sie so lange, bis sie auf dem richtigen rotation level ist
        form = self.forms[form_name]
        for l in range(level % 4):
            form = [list(reversed(k)) for k in zip(*form)]
        return form


    def clear_console(self):
        if os.name == "nt":  # Windows
            os.system("cls")
        else:  # Linux
            os.system("clear")
        print("\033[H\033[J", end='') # wenn der rest nicht funktionniert hat

    def __str__(self):  # gibt alle konfigurationsdaten aus
        return f'\033[0mKonfigurationsdaten: \n - rows: \033[31m{self.rows}\033[0m \n - cols: \033[31m{self.cols}\033[0m \n - background: \033[31m{self.backgound}\033[0m \n - foreground: \033[31m{self.foreground}\033[0m \n - form select: \033[31m{self.form_select}\033[0m'

