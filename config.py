# File to set up configuration variable to modify script behaviour

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

http_header = {'User-Agent': 'MTGCommanderAI/0.1 (https://github.com/dyeadal/mtg-commander-ai)'}

