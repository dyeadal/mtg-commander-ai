# Functions for Archidekt data, and Scryfall API

Archidekt_List = "Sol Ring", "Command Tower"

extended_card_list = []

def PasteDeckInTerminal(archidekt_deck = None):

    if archidekt_deck is None:
        archidekt_deck = input("Copy and paste your Archidekt data into here. For more information insert \"HELP\" instead.\nEnter :")

        if archidekt_deck.upper() == "HELP":
            print("""

            1) Navigate to your Archidekt deck online in a browser.
            2) Click on "Extras"
            3) Click "Export Deck"
            4) Click on the blue "Copy" button
            5) Paste contents in the terminal prompt below.
        
            """)

            PasteDeckInTerminal()

        else:
            return archidekt_deck
    else:
        return archidekt_deck

testvar = PasteDeckInTerminal()

print(testvar)

# Function to pull data about a single card name (string) #TODO

def PullCardFromScryfall(card_name):

    card = ""

    # if card contains power, toughness (likely a creature)
    return # name, cast_cost, card_type, card_description, power, toughness

    # if card does not return power, toughness
    return card # name, cast_cost, card_type, card_description


# Function to create card #TODO
"""
def PopulateListUsingScryfall(archidek_list):

    for card in archidekt_list:
        extended_card_list.append(PullCardFromScryfall(card))
        log.Wait()
    return extended_card_list
"""

