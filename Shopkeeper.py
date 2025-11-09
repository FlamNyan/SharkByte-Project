import google.generativeai as genai
from dotenv import load_dotenv
import os
import random
import time
from UI import slow_print

# ------------------- Setup -------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# global negotiation counter
var = 0


# ------------------- Shopkeeper Class -------------------
class Shopkeeper:
    def __init__(self, name, personality):
        self.name = name
        self.personality = personality
        self.is_accepted = False
        self.last_counter_offer = None

    def negotiate(self, item_name, price, offer, prevoffer):
        """
        One negotiation step with the LLM.
        Uses global var as a rough 'patience / mood' counter.
        """
        global var
        var += 1
        catch = random.choice(self.personality["catchphrases"])

        if var <= 2:
            mood = "Default personality"
        elif var <= 4:
            mood = "Slightly annoyed"
        elif var <= 6:
            mood = "Very annoyed"
        else:
            mood = "Refuses to negotiate further"

        prompt = f"""
        You are a shopkeeper named {self.name}.
        Personality: {self.personality['name']} - {self.personality['description']}.
        Style: {self.personality['style']}.
        Catchphrase: "{catch}"
        Current mood: {mood}.

        The player is offering {offer} gold for a {item_name}, base price {price} gold.
        Previous counter-offer you made: {self.last_counter_offer if self.last_counter_offer else "None"}.
        Respond in character and negotiate naturally.
        Be polite or aggressive depending on your personality.
        Also consider the player's previous offer {prevoffer}. If it's 0 disregard it.
        Your mood ("{mood}") should influence your responses and negotiation preferences.

        IMPORTANT:
        - Do NOT use the words "accept" or "deal" anywhere in your message EXCEPT on the final line.
        - At the VERY END of your reply, add ONE extra line in ALL CAPS with NO extra words:
            DECISION: ACCEPT
          or
            DECISION: REJECT
        The entire decision must be on that single line.
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Remember last counter-offer by scraping a number from the text
        import re

        numbers = re.findall(r"\d+", text)
        if numbers:
            self.last_counter_offer = int(numbers[-1])

        # Detect acceptance ONLY from the final decision line
        lines = text.splitlines()
        decision_line = lines[-1].strip().lower() if lines else ""

        if "decision: accept" in decision_line:
            self.is_accepted = True
        else:
            self.is_accepted = False

        return text

    def sell(self, character, time_limit_seconds=60):
        """
        Run one shop visit:
          - Player picks an item
          - Negotiation loop with:
              * max 7 steps (global 'var')
              * hard time limit (time_limit_seconds)
          - Item has a randomized hidden "base price" for this visit
          - Returns True if player bought something, False otherwise.
        """
        global var
        var = 0
        self.is_accepted = False
        self.last_counter_offer = None

        slow_print(
            f'{self.name}: "Welcome, traveler! Take a look at my wares."',
            delay=0.02,
        )
        for i, itm in enumerate(ITEMS, 1):
            slow_print(f"{i}. {itm['name']}", delay=0.01)

        print()

        try:
            choice = int(input("Enter the number of the item you want to buy: ")) - 1
            offer = int(input("How much gold do you offer? \n"))
            print()
        except ValueError:
            slow_print(
                "You mumble something unintelligible. The merchant just sighs.",
                delay=0.02,
            )
            return False

        if not (0 <= choice < len(ITEMS)):
            slow_print("You point at the wall. That is not for sale.", delay=0.02)
            return False

        selected_item = ITEMS[choice]
        prevoffer = 0

        # --- Hidden, randomized base price for this visit ---
        base_price = selected_item["Price"]
        # Random range: 80% - 140% of the base item price, at least 1 gold
        min_hidden = max(1, int(base_price * 0.8))
        max_hidden = int(base_price * 1.4)
        hidden_price = random.randint(min_hidden, max_hidden)

        shop_entry_time = time.perf_counter()
        purchased = False
        ended_with_custom_line = False  # prevents double closing messages

        while not self.is_accepted and var <= 7:
            now = time.perf_counter()
            elapsed = now - shop_entry_time

            if elapsed >= time_limit_seconds:
                # Time out flavor – this is the ONLY closing line for timeout
                slow_print(
                    f'\n{self.name}: "If you stare any longer, I\'ll start charging for the view. '
                    'Come back when you can decide."',
                    delay=0.02,
                )
                ended_with_custom_line = True
                break

            response_text = self.negotiate(
                selected_item["name"],
                hidden_price,  # randomized hidden base price for the LLM
                offer,
                prevoffer,
            )
            prevoffer = offer

            # Strip off the DECISION line before showing text to the player
            lines = response_text.splitlines()
            if lines and lines[-1].strip().upper().startswith("DECISION:"):
                display_text = "\n".join(lines[:-1]).strip()
            else:
                display_text = response_text

            slow_print(f"{self.name}: {display_text}", delay=0.01)

            if self.is_accepted:
                if character.money >= offer:
                    character.money -= offer
                    if not hasattr(character, "inventory"):
                        character.inventory = []
                    character.inventory.append(selected_item)
                    slow_print(
                        f"You bought {selected_item['name']} for {offer} gold. "
                        f"Remaining gold: {character.money}",
                        delay=0.02,
                    )
                    purchased = True
                else:
                    slow_print(
                        "You pat your pockets and realize they're lighter than your mouth. No deal.",
                        delay=0.02,
                    )
                    ended_with_custom_line = True
                break

            # Mood hard cap: var == 7 means 'Refuses to negotiate further'
            if var >= 7:
                slow_print(
                    f'{self.name}: "Enough! Haggling with you is costing me coin. Out."',
                    delay=0.02,
                )
                ended_with_custom_line = True
                break

            try:
                offer = int(input("Make a new offer: \n"))
            except ValueError:
                slow_print(
                    f'{self.name}: "If you can\'t count your own gold, we\'re done here."',
                    delay=0.02,
                )
                ended_with_custom_line = True
                break

        # Generic "we're done" line, only if we DIDN'T already show a custom one
        if (
            not purchased
            and not self.is_accepted
            and not ended_with_custom_line
        ):
            slow_print(
                f'{self.name}: "Time is money, friend. Come back when you know what you want."',
                delay=0.02,
            )

        return purchased


# ------------------- Personalities -------------------
greedy = {
    "name": "Greedy Merchant Joe",
    "description": "Always trying to get the most money possible (within reason). Will gladly accept if you go over his offer.",
    "style": "Arrogant and quick-witted.",
    "catchphrases": ["Nice try, kid.", "You thought you had me, huh?"],
}

polite = {
    "name": "Town Merchant Brok",
    "description": "Kind and fair, often lowers prices for travelers (within reason). Will attempt to keep things reasonable, but will accept higher prices.",
    "style": "Warm and polite.",
    "catchphrases": [
        "I'm sure we can work something out.",
        "Good luck on your adventure!",
    ],
}

PERSONALITIES = [greedy, polite]

# ------------------- Items -------------------
SWORD = {"name": "Sword", "Type": "weapon", "Damage": 5, "Price": 15}
ARMOR = {"name": "Armor", "Type": "defense", "Defense": 10, "Price": 18}
ITEMS = [SWORD, ARMOR]
