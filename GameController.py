# GameController.py

import os
import random
import time

from UI import slow_print, slow_input, print_block
from Characters import Character, enemy_templates
from Combat import Combat
from Shopkeeper import Shopkeeper, greedy, polite  # 'items' import removed – not needed


class GameController:
    def __init__(self):
        # Number of enemies defeated in this run
        self.round_counter = 0
        # After your first death, intros run in "fast" mode
        self.is_retry = False

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

        # New debt each time the intro runs
        debt = random.randint(250, 350)  # Debt is a random number from 250 to 350

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
            f'Not for glory. Not for honor. For debt. {debt} gold, to be exact..."',
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
        input("Press Enter to enter the arena... \n")

        return player_name

    # ----------------------------------------------------------------------
    # SINGLE FIGHT + SHOP
    # ----------------------------------------------------------------------
    def run_single_round(self) -> str:
        """
        Run one full round:
        - Intro
        - Create player + enemy
        - Combat
        - If enemy dies: increment round counter, visit the shop

        Returns the combat result string:
            "enemy_dead", "player_dead", or "double_ko".
        """

        # --- Intro ---
        player_name = self.show_intro()

        # --- Player creation (fresh every loop / new run) ---
        player = Character(
            name=player_name,
            health=20,
            money=0,
            armor=5,
            damage=5,
        )

        # --- Enemy creation ---
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

        # --- Combat ---
        result = self.combat.run_battle(player, enemy)

        # NOTE:
        # - On player death / double KO, the flavor text (including crowd noise)
        #   is handled inside Combat.run_battle().
        # - We do NOT print the raw result tokens ("player_dead", "double_ko") to the player.

        # --- On victory: increment round, go to shop ---
        if result == "enemy_dead":
            self.round_counter += 1

            slow_print(
                f"\nYou leave the sand with {player.money} gold "
                f"and {player.vigor} Vigor still burning in your veins.",
                delay=0.03,
            )

            # Enter the shop after victory, with a time limit
            self.run_shop_phase(player)

        return result

        # ----------------------------------------------------------------------
    # SHOP PHASE
    # ----------------------------------------------------------------------
    def run_shop_phase(self, player):
        """
        Runs the shop phase after a victory, with a time limit and
        limited negotiations. If time runs out or negotiations are exhausted,
        the shopkeeper kicks the player out with some flavor text.
        """
        # Single blank line before the shop flavor
        print()
        slow_print(
            "Between matches, you find your way to a cramped little shop "
            "wedged into the arena tunnels...",
            delay=0.03,
        )

        time_limit_seconds = 30  # or whatever you want
        shop_entry_time = time.perf_counter()
        kicked_out = False

        while True:
            now = time.perf_counter()
            elapsed = now - shop_entry_time

            if elapsed >= time_limit_seconds:
                # Time's up — quirky "you're wasting my time" dialogue
                slow_print(
                    f'\n{self.shopkeeper.name}: "Clock\'s bled dry, friend. '
                    "Gold\'s not the only thing that runs out around here.\"",
                    delay=0.03,
                )
                kicked_out = True
                break

            # Offer the player a small menu in the shop
            slow_print("\nYou are in the shop. What do you do?", delay=0.02)
            slow_print("1. Haggle for an item", delay=0.02)
            slow_print("2. Leave shop", delay=0.02)
            choice = input("> ").strip()

            if choice == "2":
                break
            if choice == "1":
                # Reset shopkeeper state at the start of each haggle
                self.shopkeeper.is_accepted = False
                self.shopkeeper.last_counter_offer = None

                self.shopkeeper.sell(player)

                # If negotiations exceeded limit inside sell(), quirky "stop wasting time"
                if not self.shopkeeper.is_accepted:
                    slow_print(
                        f'\n{self.shopkeeper.name}: "Fun\'s over. '
                        'Come back when you know what you want."',
                        delay=0.03,
                    )
                break

            slow_print("The shopkeeper stares at you, confused.", delay=0.02)

        if kicked_out:
            slow_print(
                "You’re nudged back into the corridor as the door slams behind you.",
                delay=0.03,
            )

    # ----------------------------------------------------------------------
    # DEATH RETRY PROMPT
    # ----------------------------------------------------------------------
    def ask_play_again(self) -> bool:
        """
        Asks: 'Do you wish to see the story of another criminal?'
        Returns True if the player wants to restart, False to quit.
        """
        while True:
            slow_print(
                '???: "Do you wish to see the story of another criminal?" (y/n)',
                delay=0.03,
            )
            choice = input("> ").strip().lower()

            if choice in ("y", "yes"):
                return True
            if choice in ("n", "no"):
                return False

            slow_print(
                "The voice waits for a clearer answer... (yes or no).",
                delay=0.02,
            )

    # ----------------------------------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------------------------------
    def run(self):
        """
        Overall game loop.

        - On death (player_dead or double_ko), the whole project loops *only if*
          the player answers yes to the prompt:
          'Do you wish to see the story of another criminal?'
          * Intro is re-run (with fresh debt and fresh character)
          * is_retry becomes True so future intros are faster
          * round_counter resets to 0 (fresh run)
        - On enemy_dead, the player visits the shop, then the demo ends
          (for now). Later you can expand this to multiple rounds.
        """
        while True:
            # Each run is a fresh attempt; reset round counter
            self.round_counter = 0

            result = self.run_single_round()

            if result in ("player_dead", "double_ko"):
                wants_again = self.ask_play_again()
                if wants_again:
                    self.is_retry = True
                    slow_print("\nThe arena resets around you...", delay=0.02)
                    # Loop back for a totally fresh run (new intro, new debt, new character)
                    continue
                else:
                    slow_print("\nThe tale ends here.", delay=0.03)
                    break

            # Victory (enemy_dead) currently ends the run after the shop.
            slow_print("\nEnd of demo. Thanks for playing!", delay=0.03)
            break


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    controller = GameController()
    controller.run()
