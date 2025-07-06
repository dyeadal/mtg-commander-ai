# File to set up configuration variable to modify script behaviour
import time
#################################################
# User Variables
#################################################
# Change to "True" if you want to store debug/terminal messages to a log file
LogEnable = False

# Takes None or string of directory path as a value
LogLocation = None

# LLM to use, you can find other models to use at https://ollama.com/
Ollama_Model = "deepseek-r1"

#################################################
# System Variables
#################################################
# DO NOT TOUCH UNLESS YOU KNOW WHAT YOU ARE DOING

#http_header = {'User-Agent': 'MTGCommanderAI/0.1 (https://github.com/dyeadal/mtg-commander-ai)'}



# User-Agent (required by Scryfall TOS)
SCRYFALL_USER_AGENT = "mtg-deck-parser/1.0 (https://github.com/dyeadal/mtg-commander-ai)"  # Replace with real contact email

# API URL
SCRYFALL_API_URL = "https://api.scryfall.com/cards/named"

# Rate limiting delay (max 10 requests/sec = 0.1s minimum)
SCRYFALL_API_DELAY = 1.0
# Scryfall headers
http_header = {
    "Accept": "application/json",
    "User-Agent": SCRYFALL_USER_AGENT
}

# Function to wait between API requests
def Wait():
    time.sleep(SCRYFALL_API_DELAY)

