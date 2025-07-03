# Functions for Archidekt data, and Scryfall API
import requests

from lib.logging import PrintAndLog

extended_card_list = []

def GrabArchidektData():

    # Store URL
    url = input("Copy and paste your Archidekt deck URL here: ")

    str(url)
    # Try to establish connection to HTTP page
    try:
        return requests.get(url)
    except Exception as Error:
        PrintAndLog(f"{Error}")


# Function to pull data about a single card name (string) #TODO

def PullCardFromScryfall(card_name):

    card = ""

    # if card contains power, toughness (likely a creature)
    return # name, cast_cost, card_type, card_description, power, toughness

    # if card does not return power, toughness
    return card # name, cast_cost, card_type, card_description


# Function to create card #TODO
def PopulateListUsingScryfall(card_pile):

    for card in card_pile:
        extended_card_list.append(PullCardFromScryfall(card))
        log.Wait()
    return extended_card_list


card_pile = {"Sol Ring": 1 , "Arcane Signet" : 1 , "Llanowar Elves": 1 , "Forest" : 5, "Command Tower" : 1}
# Example of  future function call card_pile = GrabArchidektData("https://archidekt.com/decks/12028998/sultai_arisen_tarkir_dragonstorm_commander")

PopulateListUsingScryfall(card_pile)
