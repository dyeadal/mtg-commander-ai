import requests
import os
import time
import logging
from dotenv import load_dotenv
import openai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def mask_sensitive_env_vars():
    return {
        "OPENAI_API_KEY": "***masked***" if os.getenv("OPENAI_API_KEY") else None,
        "ARCHIDEKT_TOKEN": "***masked***" if os.getenv("ARCHIDEKT_TOKEN") else None,
        "ARCHIDEKT_USER_ID": "***masked***" if os.getenv("ARCHIDEKT_USER_ID") else None
    }

load_dotenv()
logging.debug(f"Loaded environment variables: {mask_sensitive_env_vars()}")

openai.api_key = os.getenv("OPENAI_API_KEY")
ARCHIDEKT_TOKEN = os.getenv("ARCHIDEKT_TOKEN")
ARCHIDEKT_USER_ID = os.getenv("ARCHIDEKT_USER_ID")

HEADERS = {
    "Authorization": f"Token {ARCHIDEKT_TOKEN}",
    "Content-Type": "application/json",
}

def call_olamma_to_build_deck(seed_cards):
    logging.info("Calling Olamma to build a Commander deck...")
    start_time = time.time()
    prompt = f"""
You are Olamma, an expert Magic: The Gathering Commander deck builder.

Given this list of cards as a base pool:
{chr(10).join(seed_cards)}

Build a unique, legal 100-card Commander deck (singleton format):
- Choose an appropriate commander from the cards or suggest one.
- Build synergy, ramp, removal, draw, lands, and so on.
- Format the decklist as plain text, one card per line.
- Start with the commander as the first line.

Only respond with the decklist.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=1500
    )
    elapsed_time = time.time() - start_time
    logging.debug(f"Olamma API response time: {elapsed_time:.2f} seconds")
    logging.info("Deck received from Olamma.")
    return response["choices"][0]["message"]["content"]

def get_card_price(name):
    logging.info(f"Looking up price for: {name}")
    url = f"https://api.scryfall.com/cards/named?exact={name}"
    for attempt in range(3):
        try:
            resp = requests.get(url)
            if resp.status_code != 200:
                logging.warning(f"Attempt {attempt + 1}: Failed to fetch price for {name}. Status: {resp.status_code}")
                time.sleep(1)
                continue
            data = resp.json()
            logging.debug(f"Raw Scryfall response for {name}: {data}")
            return {
                "name": data.get("name"),
                "usd": float(data.get("prices", {}).get("usd") or 0.0),
                "url": data.get("scryfall_uri")
            }
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1}: Exception during Scryfall request for {name}: {e}")
            time.sleep(1)
    logging.error(f"All attempts failed to fetch data for {name}")
    return None

def show_prices(deck_text):
    logging.info("Fetching card prices from Scryfall...")
    total_price = 0.0
    for line in deck_text.strip().splitlines():
        if not line:
            continue
        if "x " in line:
            qty, name = line.split("x ", 1)
        elif line[0].isdigit():
            qty, name = line.split(" ", 1)
        else:
            qty, name = 1, line
        try:
            qty = int(qty)
        except ValueError:
            qty = 1
        price_data = get_card_price(name)
        if price_data:
            subtotal = qty * price_data["usd"]
            total_price += subtotal
            print(f"{qty}x {price_data['name']:<30} ${price_data['usd']:.2f} each = ${subtotal:.2f}")
        else:
            print(f"{qty}x {name:<30} price not found")
    print(f"\n💰 Estimated total deck cost: ${total_price:.2f}")

def create_new_deck_on_archidekt(deck_name, format_id=1):
    logging.info(f"Creating new deck '{deck_name}' on Archidekt...")
    url = "https://archidekt.com/api/decks/"
    payload = {
        "name": deck_name,
        "description": "Built with Olamma via GPT",
        "format": format_id,
        "visibility": "private"
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code != 201:
        raise Exception(f"Failed to create new deck. Status code: {resp.status_code}, {resp.text}")
    logging.info("Deck created successfully.")
    return resp.json()["id"]

def search_card_id(card_name):
    logging.debug(f"Searching for Archidekt ID of card: {card_name}")
    url = f"https://archidekt.com/api/cards/search/?name={card_name}&formats=1"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        logging.warning(f"Failed to search {card_name}")
        return None
    data = resp.json()
    if data["results"]:
        return data["results"][0]["id"]
    return None

def upload_cards(deck_id, deck_text):
    logging.info(f"Uploading cards to deck ID: {deck_id}")
    url = f"https://archidekt.com/api/decks/{deck_id}/cards/bulk/"
    cards = []
    first_line = deck_text.strip().splitlines()[0].lower()
    for line in deck_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if "x " in line:
            qty, name = line.split("x ", 1)
        elif line[0].isdigit():
            qty, name = line.split(" ", 1)
        else:
            qty, name = 1, line
        try:
            qty = int(qty)
        except ValueError:
            qty = 1
        card_id = search_card_id(name)
        if card_id:
            category = "Commander" if name.lower() in first_line else "Mainboard"
            cards.append({"card": card_id, "quantity": qty, "category": category})
    logging.debug(f"Cards to upload: {cards}")
    logging.info(f"Uploading {len(cards)} cards...")
    resp = requests.post(url, headers=HEADERS, json={"cards": cards})
    if resp.status_code != 201:
        raise Exception(f"Failed to upload cards. Status code: {resp.status_code}, {resp.text}")
    logging.info(f"Uploaded {len(cards)} cards to Archidekt deck #{deck_id}.")

def fetch_card_list_from_archidekt(deck_id):
    logging.info(f"Fetching card list from Archidekt deck ID {deck_id}...")
    url = f"https://archidekt.com/api/decks/{deck_id}/"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch deck. Status: {resp.status_code}, {resp.text}")
    data = resp.json()
    card_names = [card["card"]['oracleCard']['name'] for card in data['cards'] if 'oracleCard' in card['card']]
    return card_names

def fetch_card_list_from_moxfield(deck_id):
    logging.info(f"Fetching card list from Moxfield deck ID {deck_id}...")
    url = f"https://api.moxfield.com/v2/decks/{deck_id}"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch Moxfield deck. Status: {resp.status_code}, {resp.text}")
    data = resp.json()
    card_names = list(data['mainboard'].keys())
    return card_names

def generate_commander_deck(base_card_list=None):
    if base_card_list is None:
        print("Choose input source:")
        print("1. Manual entry")
        print("2. Archidekt deck ID")
        print("3. Moxfield deck ID")
        choice = input("Enter option (1/2/3): ").strip()
        if choice == "2":
            deck_id = input("Enter Archidekt deck ID: ").strip()
            base_card_list = fetch_card_list_from_archidekt(deck_id)
        elif choice == "3":
            deck_id = input("Enter Moxfield deck ID: ").strip()
            base_card_list = fetch_card_list_from_moxfield(deck_id)
        else:
            print("Enter your base card list. Type one card per line. Enter an empty line to finish:")
            base_card_list = []
            while True:
                card = input("Card name: ").strip()
                if card == "":
                    break
                base_card_list.append(card)
    logging.info(f"User provided base card list: {base_card_list}")
    logging.info("Generating Commander deck...")
    try:
        deck_text = call_olamma_to_build_deck(base_card_list)
        print(f"📋 Generated Deck:")
        print(deck_text)
        show_prices(deck_text)
        new_deck_name = f"Olamma Commander Deck"
        new_deck_id = create_new_deck_on_archidekt(new_deck_name)
        upload_cards(new_deck_id, deck_text)
        print(f"\n🌐 View your deck: https://archidekt.com/decks/{new_deck_id}")
        with open("olamma_commander_deck.txt", "w", encoding="utf-8") as f:
            f.write(deck_text)
    except Exception as e:
        logging.exception("An error occurred while generating the Commander deck")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_commander_deck()
