from openai import OpenAI
from dotenv import load_dotenv
import os
import random
import time
from UI import slow_print  # import from UI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

class Shopkeeper:
    def __init__(self, name, personality):
        """
        personality: dictionary with keys:
        'name', 'description', 'style', 'catchphrases'
        """
        self.name = name
        self.personality = personality

    def negotiate(self, item, price, base_price):
        catch = random.choice(self.personality["catchphrases"])
        
        prompt = f"""
        You are a shopkeeper named {self.name}.
        Personality: {self.personality['name']} - {self.personality['description']}.
        Communication style: {self.personality['style']}.
        Catch phrase: "{catch}"

        The player is offering you {price} gold for a {item}.
        The base price is {base_price} gold.

        You are in a fantasy world; respond in character and negotiate naturally.
        You may counter-offer, compliment, or be rude (but no cursing).
        End your response by stating your new price or if you accept.
        """

        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a shopkeeper in a fantasy RPG."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )

        return response.choices[0].message.content.strip()

Greedy = {
    "name": "Greedy Merchant Joe",
    "description": "Always trying to squeeze as much money from the player as possible.",
    "style": "Quick-witted, arrogant, and stubborn.",
    "catchphrases": ["Nice try, kid.", "You thought you had me, huh?"],
}

Polite = {
    "name": "Town Merchant Brok",
    "description": "Generous and willing to lower his prices; polite as well.",
    "style": "Warm, kind, and easy to negotiate with.",
    "catchphrases": ["I'm sure we can work something out.", "Good luck on your adventure."],
}

personalities = [Greedy, Polite]

def shop_eviction(shopkeeper):
    slow_print(f'{shopkeeper["name"]}: "Time is money, friend. You\'re done here."', delay=0.04)

def run_shop(shopkeeper_dict, player):
    clerk = Shopkeeper(shopkeeper_dict["name"], shopkeeper_dict)

    shop_entry_time = time.perf_counter()
    kicked_out = False

    while True:
        now = time.perf_counter()
        elapsed = now - shop_entry_time

        if elapsed >= 30:
            shop_eviction(shopkeeper_dict)
            kicked_out = True
            break

        slow_print("\nYou are in the shop. What do you do?", delay=0.02)
        slow_print("1. Make an offer", delay=0.02)
        slow_print("2. Leave shop", delay=0.02)
        choice = input("> ").strip()

        if choice == "2":
            break
        elif choice == "1":
            # Ask what item/price, then call clerk.negotiate(...)
            pass
        else:
            slow_print("The shopkeeper stares at you, confused.", delay=0.02)

    return kicked_out
