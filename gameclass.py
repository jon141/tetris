import json
import random
import copy
import os
import threading
import time
import math
import sys
import traceback
import asciiart
import animation
from keyboard_input import KeyboardInput


###data = json.load(open('data.json', 'r', encoding='utf-8'))

# Idee: Farben nicht komplett random, nie 2x die gleiche, oder wenn eine Farbe kommt muss mind 2x eine andere kommen (speicherung in liste mit letzte 2 Farben)
colors = [ 
            "\033[31m",
            "\033[32m",
            "\033[33m",
            "\033[34m",
            "\033[35m",
            "\033[36m",
            "\033[37m"
        ]


class Tetris:
    def __init__(self, config_data: dict, forms: dict):#, placed_color: str): #evtl. noch gamemode

        # konfigurationsvariablen
        self.rows = config_data['rows'] #Reihen
        self.cols = config_data['cols'] # spalten
        self.backgound = config_data['symbol-background'] # Symbol des Hintergrunds
        self.backgound_color = config_data['background-color']
        self.foreground = config_data['symbol-tetris'] # Symbol des Vordergrunds -> also alle Tetris Steine, (Fallend und plaziert)
        self.forms = forms # alle Tetris Formen; Dictionary
        self.form_select = config_data['forms'] # auswahl der Formen aus Dictionary nach nummer
        self.old_highscore = config_data['highscore']

        self.config_name = config_data['config-name']

        self.speed = config_data['speed']
        if type(self.speed) in (int, float):
            self.game_mode = 'constant'
        else:
            self.game_mode = 'exp' if 'start-interval' in self.speed else 'level'
        self.level = 1


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
        self.old_intersection_field = self.create_empty_field()


        self.color_cache = []
        self.tetris_form_cache = []

        # der cache soll sich dynamisch anpassen, wenn es mehr oder weniger steine im spiel gibt
        self.form_cache_max = int(len(self.form_select)*0.72)         # 72 Prozent aller verschiedenen Steine; abgerundet auf eine ganze zahl -> bei regulären 7 steinen macht das 5

        self.starttime = time.time()

        # wenn mehrere threads und das hauptprogramm gleichzeitig den curser bewegen und das spielfeld überschreiben
        # kommt es manchmal zu komplikationen, was Geistersteine erzeugt (steine die im spielfeld beim überschreiben 'vergessen' werden und in der luft hängen bleiben, obwohl sie im spiel gar nicht existieren)
        # jedes mal, wenn irgendwo was überschrieben wird, sollen die threads blockiert werden
        self.overwrite_lock = threading.Lock()


    def update_gametime(self): # soll immer beim printen des intersection field aktualisiert werden
        coordinates = [5, 15] # zeile 5 zeichen 15
        gametime_seconds = int(time.time() - self.starttime)

        minutes = gametime_seconds // 60
        seconds = gametime_seconds % 60
        with self.overwrite_lock:
            sys.stdout.write(f"\033[{coordinates[0]};{coordinates[1]}H")
            sys.stdout.write(f"\033[33m\033[31m{minutes:02d}:{seconds:02d}\033[37m")  # überschreibt die Zeichen; immer 2 Stellen (02d); in rot
            sys.stdout.flush()

    def update_scores_info(self):
        coordinates_score = [7, 15]
        coordinates_highscore = [4, 15]

        with self.overwrite_lock:
            sys.stdout.write(f"\033[{coordinates_highscore[0]};{coordinates_highscore[1]}H")
            if self.score > self.old_highscore:
                sys.stdout.write(f"\033[33m\033[31m{self.score}\033[37m")  # überschreibt die Zeichen; in rot
            else:
                sys.stdout.write(f"\033[33m\033[31m{self.old_highscore}\033[37m")  # überschreibt die Zeichen; in rot
            sys.stdout.flush()

            sys.stdout.write(f"\033[{coordinates_score[0]};{coordinates_score[1]}H")
            sys.stdout.write(f"\033[33m\033[31m{self.score}\033[37m")  # überschreibt die Zeichen; in rot
            sys.stdout.flush()

    def update_level_info(self):
        coordinates_level = [6, 15]
        with self.overwrite_lock:
            sys.stdout.write(f"\033[{coordinates_level[0]};{coordinates_level[1]}H")
            sys.stdout.write(f"\033[33m\033[31m{self.level}\033[37m")  # überschreibt die Zeichen; in rot
            sys.stdout.flush()

    def start_game(self):


        def gametime_clock():
            while not self.gameover and not self.quit_game:
                self.update_gametime()
                time.sleep(0.1)

        def clock():  # lässt die Steine FAllen, mit ansteigender fallgeschwindigkeit
            ## simulation mit Exponentiellem wachstum
            #start_interval = 1  # sekunden
            #interval_min = 0.15  # damit es nicht zu schnell wird, eine grenze
            #k = 0.00095  # proportionalitätskonstante


            while not self.gameover:
                if self.recentlyspawned is False and self.quit_game is False:
                    score_value = self.score / self.cols
                    if self.game_mode == 'exp': # exonentielle geschwindigkeitsabnahme
                        interval = self.speed['min-interval'] + (self.speed['start-interval'] - self.speed['min-interval']) * math.exp(-self.speed['k'] * score_value)
                    elif self.game_mode == 'level':
                        all_scores = list((self.speed).keys())
                        next_level_score = all_scores[self.level]
                        current_level_score = all_scores[self.level-1]
                        if score_value >= int(next_level_score):
                            self.level += 1
                            interval = self.speed[next_level_score][1]
                            self.update_level_info()
                        else:
                            interval = self.speed[current_level_score][1]
                    elif self.game_mode == 'constant':
                        interval = self.speed
                    else:
                        interval = 0.5 # wenn der wert in data beschädigt ist

                    time.sleep(interval)
                    if self.recentlyspawned is True: # wenn neu gespawnt, dann erstmal pause, nicht direkt runter
                        time.sleep(1)
                    if self.quit_game is False and self.recentlyspawned is False:  # sonst kommt es zu einer Verzögerung und das spielfeld wird nach beenden des Spiels nochmal geprintet
                        self.move_down()
                if self.quit_game is True or self.gameover:
                    break


        # einrichung des spiels und der ausgabe
        self.clear_console() # erst konsole frei macen
        self.print_field() # leeres feld printen

        time.sleep(2) # längere pause wegen start

        self.starttime = time.time() # zeitzählung starten
        gametime_clock_thread = threading.Thread(target=gametime_clock)
        gametime_clock_thread.start()


        self.spawn_tetris() # ersten stein spawnen
        self.create_intersection_field()
        self.update_field()



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
                        elif key == ' ':
                            self.quick_drop()
                        elif key in ['b', '\x1b', 'q']:  # ESC; b: break; q: quit
                            self.quit_game = True
                            self.gameover = True #???
                            self.clear_console()
                            break
                        elif key in ['r', 'R']:  # wenn man die konsole zu klien zieht, ändern sich die koordinaten und es kommt zu problemen beim überzeichenen; dann einfach mit r reset neuladen
                            self.clear_console() # löscht alles und
                            self.print_field()   # erstellt das spielfeld neu auf der konsole
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
        gametime_clock_thread.join()

        self.end_game(starttime=self.starttime)

    def end_game(self, starttime):

        # nach Ende des Spiels highscore und gametime aktualisieren

        data = json.load(open('data.json', 'r', encoding='utf-8'))

        new_highscore = False

        if self.score > self.old_highscore:
            new_highscore = True
            data[self.config_name]['highscore'] = self.score
        game_time = time.time() - starttime - 2
        data['gametime'] += game_time
        data['game-counter'] += 1
        json.dump(data, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

        self.clear_console()
        self.print_field()
        self.update_gametime()

        #print(f'\033[31m{asciiart.gameover}\033[0m')
        animation.animation(asciiart.gameover,  time_per_char=0.005, row_position=5 + self.rows, color=0)


        if new_highscore:
            #print(f'\033[34m{asciiart.highscore}\033[0m')
            animation.animation(asciiart.highscore, time_per_char=0.005, row_position=5 + self.rows + 7, color='random')


        # kurser wieder anch unten
        sys.stdout.write("\033[999;0H")
        sys.stdout.flush()

        input("Enter zum beenden...")  # Bei Enter zurück zur Spielauswahl


    def create_empty_field(self): # erstelle eine Zweidimensionale Liste aus den angegebenen reihen und spalten: zb [ [0, 0, 0], [0, 0, 0], [0, 0, 0] ]
        return [[0 for col in range(self.cols)] for row in range(self.rows)]

    def print_infobox(self):
        box = '''┌───────────┐
│\033[36mT E T R I S\033[37m│
├───────────┴─────────┐
│ \033[33mHighscore :         \033[37m│
│ \033[33mZeit      : \033[31m00:00   \033[37m│
│ \033[33mLevel     : \033[31m1       \033[37m│
│ \033[33mScore     :         \033[37m│
│                     │
└─────────────────────┘'''
        with self.overwrite_lock:
            for index, line in enumerate(box.splitlines()):
                sys.stdout.write(f"\033[{index+1};1H{line}")  # \033[Zeile;SpalteH
            sys.stdout.flush()

        self.update_scores_info()
        self.update_level_info()

    def print_field(self):
        frame_size = (self.cols * (1 + len(self.backgound)) + 3)  # optional *3, wenn unten zwei leerzeichen
        margin_left = 24

        field = f'''

{margin_left * ' ' + "┌" + "─" * (frame_size - 2) + "┐"}\n'''

        for row in self.intersection_field:  # für jede reihe im Feld der Schnittmenge
            row_string = margin_left * ' ' + '│ '  # wird erstmal ein Abstand zur linken seite und der Rahmen erstellt
            for col in row:  # für jeden Eintrag in der Reihe
                if col in [1, 2, 3, 4, 5, 6, 7]:  # wird geschaut, welche Farbe die Tetrissteine im Feld haben
                    row_string += f"{colors[col - 1]}{self.foreground} \033[0m"
                else:
                    row_string += f"{colors[self.backgound_color]}{self.backgound} "  # Hintergrund
            row_string += '\033[37m│'  # Rahmen auf der anderen Seite schließen
            field += f'{row_string}\n'  # zum Gesamtsfeld hinzufügen

        field += (margin_left * ' ' + "└" + "─" * (frame_size - 2) + "┘")  # Rahmen nach unten abschließen

        with self.overwrite_lock:
            print(field)

        self.update_scores_info()

        self.print_infobox()


    def update_field(self): # auch score updaten
        # Score updaten:
        self.update_scores_info()


        margin_left = 24  #  Rand links
        start_left = margin_left + 3 # hier beginnt der erste hintergrundstein (einmal ramen einmal lücke, dann der stein)
        margin_top = 3
        background_width = len(self.backgound)

        for y, row in enumerate(self.intersection_field): # für jede Reihe im neuen intersection_field; mit index y
            for x, col in enumerate(row): # jedes element aus der Reihe mit index x
                if self.old_intersection_field[y][x] != col: # wenn das element nicht mit dem an der gleichen position im alten feld übereinstimmt, muss das feld an der stelle geupdatet werden
                    # Cursor positionieren
                    cursor_y = margin_top + (y+1) # +3 wegen abstand von oben (mit rahmen, Score usw); (y+1) weil erstes element index 0 hat, der curser aber mit koordinaten 1 | 1 anfängt
                    cursor_x = start_left + x * (1 + background_width)  # +1 wegen rahmen; (1 + background_width) wegen lücke und (x+1) weil das erste element index 0 hat

                    with self.overwrite_lock:
                        sys.stdout.write(f"\033[{cursor_y};{cursor_x}H") # curser an koordinaten

                        if col in [1, 2, 3, 4, 5, 6, 7]: # wird geschaut, welche Farbe der Stein hat und ov es einer ist
                            sys.stdout.write(f"{colors[col - 1]}{self.foreground}\033[0m") # überschreiben
                        else: # wenn kein stein, sondern Hintergrund
                            sys.stdout.write(f"{colors[self.backgound_color]}{self.backgound}\033[0m")

                        sys.stdout.flush()

        self.old_intersection_field = copy.deepcopy(self.intersection_field) # altes feld mit neuem ersetzen

        if not self.gameover:
           if not self.quit_game:
               self.update_gametime()

    def quick_drop(self):
        while True:
            arrived = self.move_down()
            if arrived: break


    def create_intersection_field(self):
        self.old_intersection_field = copy.deepcopy(self.intersection_field)  # aktuelles feld wird zum alten und neues wird erstellt
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

        while True: # immer letzte 3 farben werden als cache gespeichert, damit eine farbe nicht mehrmals hintereinander kommt
            color_choice = random.randint(0, 6)
            if color_choice not in self.color_cache:
                self.current_color_index = color_choice
                if len(self.color_cache) > 2:
                    self.color_cache.pop(0)
                self.color_cache.append(color_choice)
                break

        self.recentlyspawned = True
        def set_recentlyspawned_False(): # neu gespawnte steine sollen nicht direkt durch die clock fallen
            time.sleep(0.3)
            self.recentlyspawned = False
        thread = threading.Thread(target=set_recentlyspawned_False)
        thread.start()


        while True: # immer letzte 5 formen werden als cache gespeichert, damit eine farbe nicht mehrmals hintereinander kommt
            form_choice = random.choice(self.form_select)
            if self.form_cache_max > 0: # für den fall, dass nur ein teil ausgewählt wurde und der cachemax somit 0 wäre -> dann funktionniert pop nicht und das ganze macht dann ja auch keinen sinn
                if form_choice not in self.tetris_form_cache:
                    if len(self.tetris_form_cache) > self.form_cache_max - 1:
                        self.tetris_form_cache.pop(0)
                    self.tetris_form_cache.append(form_choice)
                    break
        #random_form = random.choice(self.form_select) #Zufälligen Formnamen aus Auswahl auswählen

        tetris_form = self.forms[form_choice] # Matrix der Form aus dem Dict hohlen


        self.form_rotation_level = [form_choice, 0] #Zufällig generierter Name der Form und Rotation-Status, der 0 ist

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
            self.update_field()
        #self.testprint_field_form(self.falling_tetris_field)
        self.score += 10 # 10 punkte für neu gespawnten stein

        threading.Thread(
            target=self.show_score_update,
            args=(10, 0.75, [8, 10]),  # Parameter weitergeben
            daemon=True  # beendet sich mit dem Hauptprogramm
        ).start()

        self.create_intersection_field()
        self.update_field()


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
                self.update_field()
            else:  # sonst soll nichts passieren
                pass
        else:
            pass

    def show_score_update(self, score, t, coordinates):
        #coordinates = [8, 4]
        text = f'+{score}{3 * " "}'
        with self.overwrite_lock:
            sys.stdout.write(f"\033[{coordinates[0]};{coordinates[1]}H")
            sys.stdout.write(f"\033[33m\033[31m{text}\033[37m")  # überschreibt die Zeichen; in rot
            sys.stdout.flush()
        time.sleep(t)
        with self.overwrite_lock:
            overwrite_text = len(text) * ' '
            sys.stdout.write(f"\033[{coordinates[0]};{coordinates[1]}H")
            sys.stdout.write(f"\033[33m\033[37m{overwrite_text}\033[37m")  # überschreibt die Zeichen; in rot
            sys.stdout.flush()

    def check_rows_for_delete(self):
        multiplier = [0, 1, 3, 5, 8, 12, 17] # multiplikator für 0, 1, 2, 3, 4, 5, 6 Reihen
        row_counter = 0 # zählt, wie viele Reihen auf einmal gelöscht werden
        for index, row in enumerate(self.existing_block_field):
            #if all(element in [1, 2, 3, 4, 5, 6, 7] for element in row): # alle elemente ein stein sind (also nicht einmal hintergrund), dann reihe löschen
            if all(element != 0 for element in row):
                del self.existing_block_field[index] # reihe löschen
                self.existing_block_field.insert(0, [0 for col in range(self.cols)])  # oben neue, leere Reihe hinzufügen
                row_counter += 1

        row_counter = min(row_counter, 6) # für den fall, dass es mehr als 6 reihen auf einmal sind (nur bei konfiguration möglich)
        add_score = self.cols * 10 * multiplier[row_counter] # spalten (normal 10) * 10 * multiplikator je nach Reihen
        if add_score != 0:
            self.score += add_score

            threading.Thread(
                target=self.show_score_update,
                args=(add_score, 0.75, [8, 4]),  # Parameter weitergeben
                daemon=True  # beendet sich mit dem Hauptprogramm
            ).start()


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
            self.update_field()
            return False
        else:
            self.falling_tetris_field = backup
            #print('unten angekommen, oder überschneidung: Feld der exestierenden Blöcke muss erweitert werden.')
            self.expand_existing_block_field(True)
            return True # wenn es unten angekommen ist; wichtig für quickdrop

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
                self.update_field()
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
                self.update_field()

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

