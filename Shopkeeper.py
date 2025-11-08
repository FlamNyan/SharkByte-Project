from openai import OpenAI
from dotenv import load_dotenv
import os
import random
import time 

load_dotenv()  # load API key 
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key = api_key)

class Shopkeeper:

    def __init__(self, name, personality):

        """
        personality: dictionary with keys:
        'name' , 'description' , 'style' , 'cathphrases'
        """

        self.name = name
        self.personality = personality


    def negotiate(self, item, price, base_price):
        catch = random.choide(self.personality["catchphrases"])
        
        prompt = f"""
        You are a shopkeeper named {self.name}.
        Personality: {self.personality['name']} - {self.personality['description']}.
        Communication style: {self.personality['style']}.
        Catch Phrase: "{catch}"

        The player is offering you {price} gold for a {item}.
        The base price is {base_price} gold.

        You are in a fantasy world, respond in character and negotiate naturally.
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
        "description": "Always tryng to get the most amount of money out of the player posssible",
        "style": "Quick-witted, arrogant, does not give up easy",
        "catchphrases": ["Nice try kid", "You thought you had me huh?"]


    },

Polite = {
        "name": "Town Merchant Brok",
        "description": "Generous and willing to lower his prices, polite as wel",
        "style": "warm, kind, easy to negotiate with",
        "catchphrases": ["I'm sure we can work something out", "Good luck on your adventure"]


    }

personalities = [Greedy, Polite]

def start_shop_timer():
    start_time = time.perf_counter()
    time_now = time.perf_counter()
    elapsed_time = time_now - start_time

    if (elapsed_time >= 30):
        shop_eviction()

def shop_eviction():

    # holds automated kick out text and ends the shopkeeper functions
    pass



def main():

    

   # Hero1 = MainCharacter("Player")

    #Cyclops = Enemy ("Cyclops", 120, 10 )

    #Clerk1 = Shopkeeper("Joe", Greedy)
    #Clerk2 = Shopkeeper("Brok", Polite)

    
    pass
