def print_statistics(data, asciiart):
    print(f'''\033[32m
{asciiart.statistik}
\033[0m                                 
        Highscore:          \033[31m{data['highscore']}\033[0m
        Gespielte Spiele:   \033[31m{data['game-counter']}\033[0m
        Spielzeit in min:   \033[31m{data['gametime']//60}\033[0m

    \033[32m
{asciiart.information}
    \033[0m                                                                        
        Ascii-Art: \033[31mhttps://patorjk.com/software/taag/#p=display&f=Big&t= \033[0m                                                                    

\033[32m
{asciiart.steuerung}
    \033[0m  
          \033[31m🡅\033[0m             rotate \033[31m🡅\033[0m         /   \033[31mw\033[0m       
        \033[31m🡄\033[0m \033[31m🡇\033[0m \033[31m🡆\033[0m    \033[31m🡄\033[0m left down \033[31m🡇\033[0m right \033[31m🡆\033[0m  /  \033[31ma\033[0m \033[31ms\033[0m \033[31md\033[0m 
                       
                
(Press enter to go back)
    ''')