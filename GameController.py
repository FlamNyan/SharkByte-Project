import os
import random
import time

from UI import slow_print, slow_input, print_block
from Characters import Character, enemy_templates
from Combat import Combat
from Shopkeeper import Shopkeeper, greedy, polite


class GameController:
    def __init__(self):
        # Number of enemies defeated in this run
        self.round_counter = 0
        # After your first death, intros run in "fast" mode
        self.is_retry = False
        # Debt for the current run (set in show_intro)
        self.debt = 0

        # Core systems
        self.combat = Combat()
        # You can pick a fixed personality or randomize
        self.shopkeeper_personality = random.choice([greedy, polite])
        self.shopkeeper = Shopkeeper(
            self.shopkeeper_personality["name"],
            self.shopkeeper_personality,
        )

    # ----------------------------------------------------------------------
    # INTRO
    # ----------------------------------------------------------------------
    def show_intro(self) -> str:
        """
        Show the intro.

        If is_retry is False: use original, slower delays.
        If is_retry is True: use faster delays (0.01) for the main intro lines.
        """

        # Helper to swap original delay -> fast delay when retrying
        def d(original_delay: float) -> float:
            return 0.01 if self.is_retry else original_delay

        # New debt each time the intro runs and store it on the controller
        self.debt = random.randint(250, 350)  # Debt is a random number from 250 to 350

        # Clear screen (works on Windows, Mac, Linux)
        os.system("cls" if os.name == "nt" else "clear")

        slow_print("[The arena is dark. Footsteps echo.]", delay=d(0.02))
        time.sleep(0.5)

        print()
        print_block('???: "Wake up. You’re on in five."', delay=d(0.04))
        time.sleep(0.5)

        print()
        print_block(
            '???: "You remember why you’re here, right? '
            f'Not for glory. Not for honor. For debt. {self.debt} gold, to be exact..."',
            delay=d(0.04),
        )
        time.sleep(0.7)

        print()
        slow_print("[A door creaks open. Light spills in.]", delay=d(0.04))
        time.sleep(0.5)

        print()
        print_block(
            '???: "Out there, nobody cares how you swing a sword. '
            'They care if you choose right. '
            'Attack, Block, Feint—three little moves between you and the grave."',
            delay=d(0.04),
        )
        time.sleep(0.9)

        print()
        print_block(
            '???: "Read them, break them, survive them. '
            'Every duel you win buys you one more day. Every mistake… well."',
            delay=d(0.04),
        )
        time.sleep(0.9)

        print()
        slow_print("[The crowd roars in the distance.]", delay=d(0.02))
        time.sleep(0.7)

        print()
        slow_print('???: "Enough talk. Step into the circle."', delay=d(0.04))
        time.sleep(0.9)

        print()
        slow_print("VIGOR RISES WHEN BLADES MEET.", delay=d(0.03))
        slow_print("ARMOR CRACKS WHEN GUARDS FAIL.", delay=d(0.03))
        slow_print("ONLY YOUR CHOICES DECIDE THE REST.", delay=d(0.03))
        time.sleep(0.7)

        print()
        player_name = slow_input(
            '???: "Whether you live or die, who do you wish to be known as?"',
            delay=d(0.04),
        ).strip()
        if not player_name:
            player_name = "Unknown Challenger"
        time.sleep(0.7)

        print()
        slow_print(f'???: "Give them hell, {player_name}!"', delay=d(0.06))

        print()
        input("Press Enter to enter the arena... ")

        return player_name

    # ----------------------------------------------------------------------
    # ENEMY CREATION
    # ----------------------------------------------------------------------
    def _create_enemy(self) -> Character:
        """
        Create a new enemy based on a random template.
        Later, you can scale this using self.round_counter.
        """
        template = random.choice(enemy_templates)
        enemy = Character(
            name=template["name"],
            health=template["health"],
            money=0,
            armor=template["armor"],
            damage=template["damage"],
        )
        enemy.gold_min = template["gold_min"]
        enemy.gold_max = template["gold_max"]
        # Attach their preferred action so the AI can read it
        enemy.preferred_action = template.get("preferred_action")
        return enemy

    # ----------------------------------------------------------------------
    # DEBT-CLEARED ENDING
    # ----------------------------------------------------------------------
    def _run_debt_cleared_ending(self, player: Character):
        """
        Narrative + ending when the player has enough gold to pay their debt.
        Consumes the debt in gold, plays a cinematic text sequence,
        and then returns to let the caller end the run.
        """
        # Capture pre-payment gold for flavor
        total_gold = player.money
        debt = self.debt
        leftover = max(0, total_gold - debt)

        slow_print(
            "\nAs you step from the sand, the roar of the crowd dims, "
            "smothered by the stone of the tunnel.",
            delay=0.03,
        )
        time.sleep(0.5)

        slow_print(
            "For the first time, the noise behind you isn’t what you’re listening to.",
            delay=0.03,
        )
        slow_print(
            "It’s the sound in front of you — the dry scrape of a ledger being opened.",
            delay=0.03,
        )
        time.sleep(0.6)

        slow_print(
            "A clerk in ink-stained robes waits at a small iron table, "
            "flanked by two bored-looking guards.",
            delay=0.03,
        )
        slow_print(
            f"Your purse is heavy. {total_gold} gold pieces. Enough to smother "
            f"the {debt} you owe.",
            delay=0.03,
        )
        time.sleep(0.6)

        slow_print(
            '"By the terms of your sentence," the clerk drones, '
            '"payment in full remits service to the arena."',
            delay=0.03,
        )
        slow_print(
            "The words hang in the air like a blade about to fall.",
            delay=0.03,
        )
        time.sleep(0.7)

        slow_print(
            "The guards shift uneasily. This corridor is meant to funnel fighters "
            "back to the blood and sand, not spit them out into the world.",
            delay=0.03,
        )
        time.sleep(0.6)

        slow_print(
            "One coin. Then another. You lay them out slowly, each clink echoing "
            "louder than any cheer.",
            delay=0.03,
        )

        # Actually pay the debt
        player.money = leftover

        slow_print(
            "When the final coin lands, the clerk’s quill scratches your name one last time.",
            delay=0.03,
        )
        slow_print(
            'The ledger slams shut with a sound like a coffin lid. "Debt satisfied."',
            delay=0.03,
        )
        time.sleep(0.7)

        slow_print(
            "At the far end of the hall, the arena master appears — "
            "robes rich, expression poorer.",
            delay=0.03,
        )
        slow_print(
            "They study you, as if sheer will might turn coin back into chains.",
            delay=0.03,
        )
        time.sleep(0.6)

        slow_print(
            'But law is law, even here. Finally, the master spits the word like poison: "Release them."',
            delay=0.03,
        )
        time.sleep(0.6)

        slow_print(
            "A gate that has only ever opened to swallow you now grinds upward, "
            "revealing a sliver of city sky.",
            delay=0.03,
        )
        slow_print(
            "Behind you, the crowd roars for the next match… "
            "only to find the sand empty, the circle waiting for a fighter who will never return.",
            delay=0.03,
        )
        time.sleep(0.8)

        if leftover > 0:
            slow_print(
                f"You step into the daylight with {leftover} gold still in your pouch "
                "and scars the city will not understand.",
                delay=0.03,
            )
        else:
            slow_print(
                "You step into the daylight with empty pockets and a heartbeat that "
                "finally belongs only to you.",
                delay=0.03,
            )
        time.sleep(0.7)

        print()
        slow_print("YOU HAVE PAID YOUR DEBT.", delay=0.05)
        slow_print("THE ARENA REMEMBERS YOUR NAME.", delay=0.05)
        print()
        input("Press Enter to leave the arena behind... ")

    # ----------------------------------------------------------------------
    # SHOP PHASE
    # ----------------------------------------------------------------------
    def run_shop_phase(self, player: Character):
        """
        Runs the shop phase after a victory.

        The Shopkeeper handles:
        - Negotiation
        - Time limit inside sell()
        - Being annoyed / kicking you out

        Here we just:
        - Let the player choose whether to haggle or leave
        - Then give a single, clean exit line and move on.
        """
        print()
        slow_print(
            "Between matches, you find your way to a cramped little shop "
            "wedged into the arena tunnels...",
            delay=0.03,
        )

        while True:
            slow_print("\nYou are in the shop. What do you do?", delay=0.02)
            slow_print("1. Haggle for an item", delay=0.02)
            slow_print("2. Leave shop", delay=0.02)
            choice = input("> ").strip()
            print()  # blank line after the player's choice

            if choice == "2":
                break
            if choice == "1":
                # Reset shopkeeper state at the start of each haggle
                self.shopkeeper.is_accepted = False
                self.shopkeeper.last_counter_offer = None

                # The shopkeeper handles all flavor + timeouts
                self.shopkeeper.sell(player)
                break

            slow_print("The shopkeeper stares at you, confused.", delay=0.02)

        # Single, clean exit line for ALL outcomes
        slow_print(
            "\nYou step back out of the cramped shop as the arena guards move to escort you.",
            delay=0.03,
        )

    # ----------------------------------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------------------------------
    def run(self):
        """
        Overall game loop.

        - One "run" = intro + repeated rounds until death / quit.
        - Each round:
            * Announce round number
            * Spawn random enemy
            * Fight
            * On victory: go to shop, then next round
        - On death:
            * Combat.run_battle prints death + crowd text
              and asks if you want another criminal.
            * If Combat.run_battle returns "quit", we stop everything here.
        """
        while True:  # Outer loop: full runs
            self.round_counter = 0

            # --- New Run: Intro + Player creation ---
            player_name = self.show_intro()
            player = Character(
                name=player_name,
                health=20,
                money=0,
                armor=5,
                damage=5,
            )

            # --- Inner loop: Rounds within this run ---
            while True:
                current_round = self.round_counter + 1
                slow_print(f"\n[ROUND: {current_round} BEGINS!]", delay=0.03)

                enemy = self._create_enemy()
                result = self.combat.run_battle(player, enemy)

                if result == "enemy_dead":
                    # Completed a round
                    self.round_counter += 1

                    slow_print(
                        f"\nYou leave the sand with {player.money} gold "
                        f"and {player.vigor} Vigor still burning in your veins.",
                        delay=0.03,
                    )

                    # --- Check if the player can now pay off their debt ---
                    if player.money >= self.debt:
                        self._run_debt_cleared_ending(player)
                        return  # End the whole run / game

                    # Shop between rounds
                    self.run_shop_phase(player)

                    # After shopping, it’s *possible* they still have enough to pay
                    # (if they didn’t buy anything or negotiated well).
                    if player.money >= self.debt:
                        self._run_debt_cleared_ending(player)
                        return

                    # Loop continues to next round with the same player
                    continue

                # Explicit quit from Combat
                if result == "quit":
                    slow_print("\nYour story ends here.", delay=0.03)
                    return

                # Player died (or double KO), but chose to see another criminal.
                # Mark this as a retry so intro text is faster next time.
                self.is_retry = True
                slow_print("\nThe arena resets around you...", delay=0.02)
                # Break inner loop to restart from intro with a new character
                break


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    controller = GameController()
    controller.run()
