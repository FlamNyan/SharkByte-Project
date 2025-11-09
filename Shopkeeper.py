
from google import genai
import google.generativeai as genai
from dotenv import load_dotenv
from Characters import Character
import os
import random

# ------------------- Setup -------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

var = 0

# ------------------- Shopkeeper Class -------------------
class Shopkeeper:
    def __init__(self, name, personality):
        self.name = name
        self.personality = personality
        self.is_accepted = False

    def negotiate(self, item_name, price, offer, prevoffer):
        global var
        var += 1
        catch = random.choice(self.personality["catchphrases"])

        mood = "Default personality"

        if var <= 2:
            mood = "Default personality"

        elif var <= 4:
            mood = "Slightly annoyed"
        
        elif var <= 6:
            mood = "Very annoyed"

        elif var == 7:
            mood = "Refuses to negotiate further"

        prompt = f"""
        You are a shopkeeper named {self.name}.
        Personality: {self.personality['name']} - {self.personality['description']}.
        Style: {self.personality['style']}.
        Catchphrase: "{catch}"
        Current mood: {mood}.

        The player is offering {offer} gold for a {item_name}, base price {price} gold.
        Respond in character and negotiate naturally.
        Be polite or aggressive depending on your personality.
        If your {prevoffer} matches the player's offer, you should accept the deal.
        Your {mood} should influence your responses and negotiation preferences.
        End your message by stating your new price or if you accept the deal.
        If the offer is acceptable, clearly say the words "accept" or "deal" to make sure you wanna sell it, Otherwise do not say them.
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Detect acceptance
        if "accept" in text.lower() or "deal" in text.lower():
            self.is_accepted = True

        return text

    def sell(self, character):
        global var
        var = 0
        print(f"{self.name}: Welcome, traveler! Take a look at my wares:")
        for i, itm in enumerate(items, 1):
            print(f"{i}. {itm['name']}")

        try:
            choice = int(input("Enter the number of the item you want to buy: ")) - 1
            offer = int(input("How much gold do you offer? "))
        except ValueError:
            print("Invalid input.")
            return

        if not (0 <= choice < len(items)):
            print("Invalid choice.")
            return

        selected_item = items[choice]
        prevoffer = 0
        while not self.is_accepted and var <= 7:
            response_text = self.negotiate(selected_item['name'], selected_item['Price'], offer, prevoffer)
            print(f"{self.name}: {response_text}")

            if self.is_accepted:
                if character.money >= offer:
                    character.money -= offer
                    character.inventory.append(selected_item)
                    print(f"You bought {selected_item['name']} for {offer} gold. Remaining gold: {character.money}")
                else:
                    print("You don't have enough gold!")
                break
            else:
                try:
                    offer = int(input("Make a new offer: "))
                except ValueError:
                    print("Invalid number, ending negotiation.")
                    break

# ------------------- Personalities -------------------
greedy = {
    "name": "Greedy Merchant Joe",
    "description": "Always trying to get the most money possible.",
    "style": "Arrogant and quick-witted.",
    "catchphrases": ["Nice try, kid.", "You thought you had me, huh?"]
}

polite = {
    "name": "Town Merchant Brok",
    "description": "Kind and fair, often lowers prices for travelers.",
    "style": "Warm and polite.",
    "catchphrases": ["I'm sure we can work something out.", "Good luck on your adventure!"]
}

# ------------------- Items -------------------
Sword = {"name": "Sword", "Type": "weapon", "Damage": 5, "Price": 10}
Armor = {"name": "Armor", "Type": "defense", "Defense": 25, "Price": 40}
items = [Sword, Armor]

# ------------------- Main -------------------
def main():
    print("Welcome to the Shopkeeper Demo!")
    hero = Character("Hero", 100, 50, 10, 50)
    clerk = Shopkeeper("Brok", polite)
    clerk.sell(hero)

if __name__ == "__main__":
    main()
