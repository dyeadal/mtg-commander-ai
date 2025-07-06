
# Functions for Archidekt data, and Scryfall API
import custom_logging as log
import config as cfg
import requests
from collections import defaultdict
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


# ====== Pull Single Card Info from Scryfall ======
def PullCardFromScryfall(card_name):
    params = {"fuzzy": card_name}
    log.PrintAndLog(f"Requesting Scryfall data for card: {card_name}")

    try:
        cfg.Wait()
        response = requests.get(cfg.SCRYFALL_API_URL, headers=cfg.http_header, params=params, timeout=10)

        if response.status_code == 429:
            log.PrintAndLog("Rate limit hit. Waiting and retrying...")
            cfg.Wait()
            response = requests.get(cfg.SCRYFALL_API_URL, headers=cfg.http_header, params=params, timeout=10)

        response.raise_for_status()
        card = response.json()

        card_type = card.get("type_line", "")
        name = card.get("name", "")
        mana_cost = card.get("mana_cost", "")
        oracle_text = card.get("oracle_text", "").replace("\n", " ")
        power = card.get("power")
        toughness = card.get("toughness")
        is_legendary = "Legendary" in card_type

        card_data = {
            "name": name,
            "mana_cost": mana_cost,
            "type": card_type,
            "oracle_text": oracle_text,
            "is_legendary": is_legendary
        }

        if power is not None and toughness is not None:
            card_data["power"] = power
            card_data["toughness"] = toughness

        log.PrintAndLog(f"Card data assembled successfully for '{card_name}'")
        return card_data

    except Exception as e:
        log.PrintAndLog(f"[ERROR] Failed to fetch or parse '{card_name}' from Scryfall: {e}")
        return {"error": str(e), "name": card_name}


def PopulateListUsingScryfall(card_pile):
    extended_card_list = []  # fresh list for this run
    for card_name, quantity in card_pile.items():
        try:
            for _ in range(quantity):
                extended_card_list.append(PullCardFromScryfall(card_name))
            log.PrintAndLog(f"Added {quantity} entries for '{card_name}'")
        except Exception as e:
            log.PrintAndLog(f"[ERROR] While processing '{card_name}': {e}")
            extended_card_list.append({"error": str(e), "name": card_name})
    return extended_card_list


def FormatCardListToString(card_list):
    grouped_cards = defaultdict(lambda: {"count": 0, "data": None})
    formatted_output = []

    try:
        for card in card_list:
            try:
                name = card.get("name", "Unknown")
                grouped_cards[name]["count"] += 1
                grouped_cards[name]["data"] = card
            except Exception as e:
                log.PrintAndLog(f"[ERROR] Grouping issue with card: {e}")
        log.PrintAndLog("Successfully grouped cards")
    except Exception as e:
        log.PrintAndLog(f"[ERROR] Card grouping failed: {e}")
        return "[ERROR] Could not format card list"

    for name, group in grouped_cards.items():
        count = group["count"]
        data = group["data"]
        try:
            if "error" in data:
                formatted_output.append(f"[ERROR] {name} x{count} - {data['error']}")
                continue

            line = f"{data.get('type', '')} | {name} x{count} | {data.get('mana_cost', '')}"

            if "power" in data and "toughness" in data:
                line += f" | {data['power']}/{data['toughness']}"

            if "oracle_text" in data:
                line += f" | {data['oracle_text']}"

            if data.get("is_legendary"):
                line += " | [Legendary]"

            formatted_output.append(line)
        except Exception as e:
            log.PrintAndLog(f"[ERROR] Formatting issue for '{name}': {e}")
            formatted_output.append(f"[ERROR] {name} x{count} - formatting failed")

    log.PrintAndLog("Formatted card list successfully")
    return "\n".join(formatted_output)


if __name__ == "__main__":
    try:
        test_card_pile = GrabArchidektData("https://archidekt.com/decks/13934805/sultai_arisen_tdm")

        print("\nInitial Card Pile:")
        print(test_card_pile)
        print(f"Total unique cards: {len(test_card_pile)}")

        detailed_cards = PopulateListUsingScryfall(test_card_pile)
        output_string = FormatCardListToString(detailed_cards)

        print("\nFormatted Card Output:\n")
        print(output_string)
    except Exception as e:
        log.PrintAndLog(f"[FATAL ERROR] Program terminated unexpectedly: {e}")
