# Functions for Archidekt data, and Scryfall API
import custom_logging as log
import config as cfg
import requests

extended_card_list = []

def GrabArchidektData(url = None):

    # User did not submit a URL, prompt for one
    if url is None:
        # Store URL
        url = input("Copy and paste your Archidekt deck URL here: ")

    # User supplied URL
    elif url is not None:
        url = str(url)

    # Issue prompting or storing URL
    else:
        log.ThrowIntentionalError("Error running Archidekt API function ")

    # Splits URL to grab and store the Archidekt deck ID to query their API for JSON formatted data on their deck
    archidekt_deck_ID = url.split("/")[4]

    # Try requesting API for JSON data and return list of names and quantity of each card
    log.PrintAndLog(f"Attempting to grab Archidekt data from {url} via their API")
    try:
        # Create API URL using deck ID
        API_url = f"https://archidekt.com/api/decks/{archidekt_deck_ID}/"

        # Perform GET request with custom header and store JSON response
        deck_data = requests.get(API_url, cfg.http_header).json()

        # JSON value cards store list of unique cards, quantity and other information
        card_quantity_in_deck = len(deck_data.get("cards"))

        # Create empty dictionary to insert card name and its quantity
        card_pile = {}

        # Loop through each card
        i = 0
        while i < card_quantity_in_deck:
            # Grab and store card name
            name = deck_data.get('cards')[i].get('card').get('oracleCard').get('name')
            # Grab and store card quantity
            quantity = deck_data.get('cards')[i].get('quantity')

            # Insert card data into dict
            card_pile[name] = quantity
            i += 1
        log.PrintAndLog(f"Successfully grabbed Archidekt deck data")
        return card_pile

    except Exception as Error:
        log.PrintAndLog(f"Unable to grab deck data via Archidekt's API. Error: {Error}")


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

#PopulateListUsingScryfall(card_pile)

####################################################
# TEST TEST TEST TEST TEST TEST TEST TEST TEST
####################################################

# It is important to note return variable is a dictionary
# Visit W3 link below to see examples
# https://www.w3schools.com/python/python_dictionaries.asp

# Example of GrabArchidekt() function and using its returned dictionaries
test_card_pile = GrabArchidektData("https://archidekt.com/decks/13934805/sultai_arisen_tdm")
print(test_card_pile)

print(len(test_card_pile))

# This will loop through each card which we will use in the Scrfall info retrival function
# Ensure you implement delays and follow Scryfall API rules
for card, quantity in test_card_pile.items():
    print(card, quantity)
