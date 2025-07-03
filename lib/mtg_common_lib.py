# mtg_common_lib.py
# Stores common functions for logging, and text file creation, etc.

from lib import mtg_logging_lib as log
from lib import mtg_data_lib as mtg

def Menu():
    log.PrintAndLog("Displaying menu to user")
    print("""
    
    1) Insert Pile of Cards
    2) Ask AI Model to make decisions on your card
    3) Add a card
    4) Remove a card
    5) Reveal cards in pile 
    
    Q) QUIT
    
    """)

    option = input(">: ")

    a = 0
    if option == "1":
        mtg.PasteDeckInTerminal()

        Menu()
    elif option == "2":
        a = 2
        Menu()
    elif option == "3":
        a = 3
        Menu()
    elif option == "4":
        a = 4
        Menu()
    elif option == "5":
        a = 5
        Menu()
    elif option.lower() == "q":
        exit()
    else:
        log.ErrorHandler("Invalid option chosen at Menu")




