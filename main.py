import json
import msvcrt
import time
#import random
import os
import threading
#import copy
import configuration
import addform
import animation
import asciiart
import gameclass
import statistik



#json.dump(dates_json, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
#json.dump(forms, open('forms.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

forms = json.load(open('forms.json', 'r', encoding='utf-8'))
data = json.load(open('data.json', 'r', encoding='utf-8'))

print("\033[H\033[J", end="")


def valid_choice1():
    while True:
        print("\033[H\033[J", end='')
        print('\033[32m')
        print(asciiart.tetris)
        print('\033[0m')

        print("""
        Wähle aus, was du machen willst (1-6):
            \033[31m1\033[0m Normales Spiel
            \033[31m2\033[0m gespeicherte Konfiguration spielen
            \033[31m3\033[0m Konfiguration ansehen / Spiel konfigurieren 
            \033[31m4\033[0m Neue Formen hinzugügen  
            \033[31m5\033[0m Statistik / Informationen / Steuerung
            \033[31m6\033[0m Spiel beenden
                """)

        choice = input('            ')

        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice


def print_ramen(width, height):
    # Obere Linie
    print(f"\033[31m#{' ' * (width - 2)}#", end='')

    # Mittlere Zeilen (vertikale Ränder)
    for row in range(height):
        print(f"{' ' * (width - 2)}")

    # Untere Linie
    print(f"#{' ' * (width - 2)}#\033[0m", end='')


# Beispielaufruf
#print_ramen(10, 5)


# Rechteck mit 20 Spalten und 10 Zeilen
#print_ramen(60, 30)




def main(konfigurationsdaten):

    time_start = time.time()

    def clock():
        while running:
            if Game.recentlyspawned is False and quit is False:
                time.sleep(1)
                if quit is False and Game.recentlyspawned is False: # sonst kommt es zu einer Verzögerung und das spielfeld wird nach beenden des Spiels nochmal geprintet
                    Game.move_down()
            if quit is True or running is False:
                break
    running = True
    quit = False
    Game = gameclass.Tetris(rows=konfigurationsdaten['rows'], cols=konfigurationsdaten['cols'], background=konfigurationsdaten['symbol-background'], foreground=konfigurationsdaten['symbol-tetris'], forms=forms, form_select=konfigurationsdaten['forms'])
    # tetris = game(konfigurationswerte)
    #print(Game)
    #input()
    Game.clear_console()
    Game.create_intersection_field()
    Game.clear_console()
    Game.print_intersection_field()
    time.sleep(2)
    Game.spawn_tetris()
    Game.create_intersection_field()
    Game.clear_console()
    Game.print_intersection_field()

    thread = threading.Thread(target=clock)
    thread.start()
    while running: #Hier kommt die Spiellogik hin
        if Game.gameover is True:
            running = False
            Game.clear_console()

        elif msvcrt.kbhit():
            key = Game.get_key_action()
            # print(key)
            if key == 'a' or key == 'K':  # links
                Game.move_left()
            elif key == 'd' or key == 'M':  # rechts
                Game.move_right()
            elif key == 'w' or key == 'H':  # oben
                Game.rotate_tetris_in_falling_field()
            elif key == 's' or key == 'P':  # unten
                Game.move_down()
            elif key == 'b':
                quit = True
                running = False
                Game.clear_console()

    if quit is False:

        if Game.score > data['highscore']:
            data['highscore'] = Game.score
        game_time = time.time()-time_start
        data['gametime'] += game_time
        data['game-counter'] += 1
        json.dump(data, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

        Game.clear_console()
        Game.clear_console()
        Game.print_intersection_field()
        print(f'\033[31m{asciiart.gameover}\033[0m')

        game_time = time.time()-time_start

        input() #Bei Enter zurück zur Spielauswahl

    #time.sleep(5)

        # spawn tetris
            # kollistion = False
            #while kollision == False:
                #Tastenabfragen: Drehen, Runter, Verschieben mit if msvcrt....
                #UND permanent Runter in gewissen Zeitabständen #Eventuell mit threding wenn es nicht anders geht
                # check for collision
            #(colission == True)
            #check for delete Row
            #ckeck for game over
            #erhöhe Highscore
print('\033[?25l') # curser verstecken
animation.animation(asciiart.tetris)
while True:
    print("\033[H\033[J", end='')
    choice = valid_choice1()
    print("\033[A\033[K", end="")  # Eine Zeile nach oben und löschen
    #print('es kann weiter gehen')
    if choice == '1' or choice == '2':
        #print('1')
        print("\033[H\033[J", end='') # ziehe dein bildschirm so groß, bis du alle 4 Ecken siehst
        #print_ramen(150, 30)
        input('Mach das Fenster ausreichend groß!!! (Auf Laptops Vollbild empfohlen) Spiel kann beendet werden, wenn b gedrückt wird. Press enter to start the Game.')
        print("\033[H\033[J", end='')
        print(f'\033[36m{asciiart.tetris_gamestart}\033[0m', end='')
        time.sleep(1)

        os.system('cls')

        if choice == '1':
            konfigurationsdaten = data['normal']

        else:
            konfigurationsdaten = data['konfiguration']
        main(konfigurationsdaten)
    elif choice == '3':
        print("\033[H\033[J", end='')
        configuration.spiel_konfigurieren(forms, data)
    elif choice == '4':
        addform.add_form(forms, asciiart.formen_hinzufuegen)
        print(forms)
    elif choice == '5':
        print("\033[H\033[J", end='')
        statistik.print_statistics(data, asciiart)
        input()
    else:
        break
    #input('')

#input('Do you want to end and close console???')