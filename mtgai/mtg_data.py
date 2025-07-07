import custom_logging as log
import config as cfg
import requests
import os
import json
from collections import defaultdict

# ===========================
# Utility: Delete Cache File
# ===========================
def delete_scryfall_bulk_cache(file_path="oracle_cards.json"):
    """
    Deletes the local Scryfall bulk data cache file if it exists.
    This is useful during development or testing to force the script
    to download fresh card data from Scryfall.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        log.PrintAndLog(f"Deleted cached bulk file: {file_path}")
    else:
        log.PrintAndLog(f"No cached file found at: {file_path}")

# =======================================
# Archidekt API: Retrieve Deck Card Data
# =======================================
def GrabArchidektData(url = None):
    """
    Fetches card names and their quantities from a given Archidekt deck URL
    using Archidekt's public API. Returns a dictionary of card name => quantity.
    """
    if url is None:
        url = input("Copy and paste your Archidekt deck URL here: ")
    elif url is not None:
        url = str(url)
    else:
        log.ThrowIntentionalError("Error running Archidekt API function ")

    # Extract deck ID from the URL
    archidekt_deck_ID = url.split("/")[4]
    log.PrintAndLog(f"Attempting to grab Archidekt data from {url} via their API")

    try:
        API_url = f"https://archidekt.com/api/decks/{archidekt_deck_ID}/"
        deck_data = requests.get(API_url, cfg.http_header).json()
        card_quantity_in_deck = len(deck_data.get("cards"))
        card_pile = {}

        # Collect card names and quantities into a dictionary
        for i in range(card_quantity_in_deck):
            name = deck_data['cards'][i]['card']['oracleCard']['name']
            quantity = deck_data['cards'][i]['quantity']
            card_pile[name] = quantity

        log.PrintAndLog("Successfully grabbed Archidekt deck data")
        return card_pile

    except Exception as Error:
        log.PrintAndLog(f"Unable to grab deck data via Archidekt's API. Error: {Error}")

# ======================================
# Scryfall Bulk Data: Load into Memory
# ======================================
bulk_card_lookup = {}  # Dictionary to store card data from bulk JSON

def DownloadAndLoadScryfallBulk():
    """
    Downloads the full Scryfall oracle_cards dataset if not already cached.
    Loads it into memory as a dictionary mapping card names (lowercase) to card data.
    """
    try:
        bulk_file = "oracle_cards.json"

        if not os.path.exists(bulk_file):
            log.PrintAndLog("Downloading bulk Scryfall data...")
            index_url = "https://api.scryfall.com/bulk-data"
            index_resp = requests.get(index_url, timeout=15)
            index_resp.raise_for_status()

            # Find the oracle_cards type entry
            data = index_resp.json()
            oracle_entry = next((e for e in data["data"] if e["type"] == "oracle_cards"), None)

            if not oracle_entry:
                raise ValueError("oracle_cards not found in bulk data index")

            # Download and save the full oracle_cards dataset
            download_url = oracle_entry["download_uri"]
            download_resp = requests.get(download_url, timeout=60)
            download_resp.raise_for_status()

            with open(bulk_file, "w", encoding="utf-8") as f:
                f.write(download_resp.text)
            log.PrintAndLog("Scryfall bulk data downloaded and saved.")
        else:
            log.PrintAndLog("Using cached Scryfall bulk data.")

        # Load the JSON into memory
        with open(bulk_file, "r", encoding="utf-8") as f:
            all_cards = json.load(f)

        global bulk_card_lookup
        bulk_card_lookup = {card["name"].lower(): card for card in all_cards if "name" in card}
        log.PrintAndLog(f"Loaded {len(bulk_card_lookup)} cards into lookup table.")

    except Exception as e:
        log.PrintAndLog(f"[FATAL ERROR] Failed to download or load Scryfall bulk data: {e}")
        raise

# ======================================
# Get Card Info From Bulk or API Backup
# ======================================
def PullCardFromScryfall(card_name):
    """
    Attempts to retrieve a card's data by name using bulk data.
    If not found in bulk, queries the Scryfall API as a fallback.
    Returns card metadata including name, type, mana cost, text, etc.
    """
    card = bulk_card_lookup.get(card_name.lower())

    if not card:
        log.PrintAndLog(f"[WARN] '{card_name}' not found in bulk data. Falling back to Scryfall API.")
        try:
            cfg.Wait()
            response = requests.get(cfg.SCRYFALL_API_URL, headers=cfg.http_header, params={"fuzzy": card_name}, timeout=10)
            if response.status_code == 429:
                log.PrintAndLog("Rate limit hit. Retrying after wait...")
                cfg.Wait()
                response = requests.get(cfg.SCRYFALL_API_URL, headers=cfg.http_header, params={"fuzzy": card_name}, timeout=10)
            response.raise_for_status()
            card = response.json()
        except Exception as e:
            log.PrintAndLog(f"[ERROR] Scryfall API lookup failed for '{card_name}': {e}")
            return {"error": f"Scryfall API error: {e}", "name": card_name}

    try:
        # Extract desired card fields
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

        return card_data

    except Exception as e:
        log.PrintAndLog(f"[ERROR] Failed to parse card data for '{card_name}': {e}")
        return {"error": str(e), "name": card_name}

# ====================================
# Build Full Card List with Quantities
# ====================================
def PopulateListUsingScryfall(card_pile):
    """
    Given a dictionary of card names and quantities (from Archidekt),
    returns a list of card data repeated according to quantity.
    """
    extended_card_list = []
    for card_name, quantity in card_pile.items():
        try:
            for _ in range(quantity):
                extended_card_list.append(PullCardFromScryfall(card_name))
        except Exception as e:
            log.PrintAndLog(f"[ERROR] While processing '{card_name}': {e}")
            extended_card_list.append({"error": str(e), "name": card_name})
    return extended_card_list

# ====================================
# Output: Format Card List for Display
# ====================================
def FormatCardListToString(card_list):
    """
    Takes a full list of card data entries and formats them as readable text,
    grouped by card name, showing type, mana cost, oracle text, and stats.
    """
    grouped_cards = defaultdict(lambda: {"count": 0, "data": None})
    formatted_output = []

    # Group cards by name and keep count
    for card in card_list:
        name = card.get("name", "Unknown")
        grouped_cards[name]["count"] += 1
        grouped_cards[name]["data"] = card

    # Format each grouped entry
    for name, group in grouped_cards.items():
        count = group["count"]
        data = group["data"]

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

    return "\n".join(formatted_output)

# =======================
# Entry Point For Script
# =======================
if __name__ == "__main__":
    """
      Main execution block:
      - Downloads or loads bulk Scryfall card data for fast lookups.
      - Retrieves a sample deck from Archidekt using the provided URL.
      - Fetches detailed card information for the deck.
      - Formats and prints the card list output.
      - Logs any fatal exceptions during the run.
      """
    try:
        delete_scryfall_bulk_cache()  # Remove old bulk cache for testing
        DownloadAndLoadScryfallBulk()  # Load or download Scryfall bulk data

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
