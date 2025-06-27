# === mtg_bot/commands/rule_search.py ===
import os

CSV_DIRECTORY = r"CVS_DIRECTORY"
RULES_FILE_PATH = os.path.join(CSV_DIRECTORY, 'mtg_rules.txt.txt')

async def search_rule(ctx, *, search_terms: str):
    RULES_CHANNEL_NAME = '🧐card-ruling'

    if ctx.channel.name != RULES_CHANNEL_NAME:
        await ctx.send(f'🚫 This command can only be used in #{RULES_CHANNEL_NAME}.' )
        return

    if not os.path.exists(RULES_FILE_PATH):
        await ctx.send('⚠️ Rules file not found.')
        return

    with open(RULES_FILE_PATH, 'r', encoding='utf-8') as f:
        rules = f.readlines()

    search_terms = search_terms.lower().split()
    matching_rules = [line for line in rules if all(term in line.lower() for term in search_terms)]

    if matching_rules:
        response = '📜 **Found Rules:**\n' + ''.join(matching_rules[:7])
        if len(matching_rules) > 7:
            response += f"\n...and {len(matching_rules) - 7} more. Please refine your search."
    else:
        response = '❌ No rules found matching those terms.'

    await ctx.send(response)
