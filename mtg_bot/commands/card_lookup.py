# === mtg_bot/commands/card_lookup.py ===
import discord
import requests

async def card_lookup(ctx, *, card_name: str):
    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        await ctx.send("🚫 Could not retrieve card data. Check your spelling and try again.")
        return

    name = data.get("name", "Unknown Card")
    set_name = data.get("set_name", "Unknown Set")
    image_url = data.get("image_uris", {}).get("normal", None)
    oracle_text = data.get("oracle_text", "No rules text available.")
    mana_cost = data.get("mana_cost", "N/A")
    type_line = data.get("type_line", "Unknown Type")
    power = data.get("power", "")
    toughness = data.get("toughness", "")
    loyalty = data.get("loyalty", "")
    price_usd = data.get("prices", {}).get("usd", "N/A")
    price_foil = data.get("prices", {}).get("usd_foil", "N/A")
    price_tix = data.get("prices", {}).get("tix", "N/A")
    scryfall_url = data.get("scryfall_uri", "")

    legalities = data.get("legalities", {})
    legal_formats = [fmt.upper() for fmt, status in legalities.items() if status == "legal"]
    legality_text = ", ".join(legal_formats) if legal_formats else "None"

    related_prints = []
    related_url = f"https://api.scryfall.com/cards/search?q=oracleid:{data.get('oracle_id')}"
    related_response = requests.get(related_url)

    if related_response.status_code == 200:
        related_data = related_response.json()
        related_prints = [f"[{card.get('set_name')}]({card.get('scryfall_uri')})" for card in related_data.get("data", [])]

    related_text = ", ".join(related_prints[:5]) if related_prints else "No other prints found."

    embed = discord.Embed(title=name, description=f"{type_line} | {set_name}", color=0x1F8B4C)
    if image_url:
        embed.set_thumbnail(url=image_url)
    embed.add_field(name="Mana Cost", value=mana_cost, inline=True)

    if power and toughness:
        embed.add_field(name="Power/Toughness", value=f"{power}/{toughness}", inline=True)
    elif loyalty:
        embed.add_field(name="Loyalty", value=loyalty, inline=True)

    embed.add_field(name="Oracle Text", value=oracle_text[:1024], inline=False)
    embed.add_field(name="Price (USD)", value=f"${price_usd}" if price_usd != "N/A" else "N/A", inline=True)
    embed.add_field(name="Foil Price (USD)", value=f"${price_foil}" if price_foil != "N/A" else "N/A", inline=True)
    embed.add_field(name="MTGO Price (TIX)", value=price_tix, inline=True)
    embed.add_field(name="Legality", value=legality_text, inline=False)
    embed.add_field(name="Related Prints", value=related_text, inline=False)
    embed.add_field(name="More Info", value=f"[Scryfall Link]({scryfall_url})", inline=False)

    await ctx.send(embed=embed)
