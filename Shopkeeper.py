
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # load API key 
api_key = os.getenv("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")

client = OpenAI(api_key= api_key)






class Shopkeeper:

    def __init__(self, name, personality):

        self.name = name
        self.personality = personality






def main():

    print("")

    Hero1 = MainCharacter("Player")

    Cyclops = Enemy ("Cyclops", 120, 10 )

    Clerk1 = Shopkeeper("Joe", greedy)
    Clerk2 = Shopkeeper("Brok", Polite)

    

