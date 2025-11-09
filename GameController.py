import random
from UI import slow_print, slow_input, print_block
from Characters import Character, enemy_templates
from Combat import Combat


def show_intro(is_retry=False):
    """
    Show the intro.

    If is_retry is False: use original, slower delays.
    If is_retry is True: use faster delays (0.01) for the main intro lines.
    """
    import os
    import time

    # Helper to swap original delay -> fast delay when retrying
    def d(original_delay: float) -> float:
        return 0.01 if is_retry else original_delay

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


def run_single_fight(is_retry: bool) -> str:
    """
    Run one full loop: intro -> create player/enemy -> combat.

    Returns the combat result string:
        "enemy_dead", "player_dead", or "double_ko".

    NOTE: We no longer print the raw result token (e.g. 'player_dead').
    """
    player_name = show_intro(is_retry=is_retry)

    # Player creation (fresh every loop)
    player = Character(
        name=player_name,
        health=20,
        money=0,
        armor=5,
        damage=5,
    )

    # Pick a random enemy template and instantiate enemy
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

    combat = Combat()
    result = combat.run_battle(player, enemy)

    # Only show a post-fight status line on victory.
    # On death, the flavor text is handled inside Combat.run_battle
    # and we avoid printing 'player_dead' / 'double_ko' to the player.
    if result == "enemy_dead":
        slow_print(
            f"\nYou leave the sand with {player.money} gold "
            f"and {player.vigor} Vigor still burning in your veins.",
            delay=0.03,
        )

    return result


def main():
    """
    Main loop:
    - On death (player_dead or double_ko), the whole project loops:
      * Screen is cleared via show_intro()
      * A new debt is rolled
      * New player and enemy are created
      * Intro text is sped up (0.01 delay) for all the intro lines
    - On enemy_dead, we end the demo.
    """
    is_retry = False

    while True:
        result = run_single_fight(is_retry=is_retry)

        if result in ("player_dead", "double_ko"):
            # After any death, future intros run in "fast" mode
            is_retry = True
            # Short pause before the loop restarts
            slow_print("\nThe arena resets around you...", delay=0.02)
            continue

        # Victory or other non-death result: end the demo
        slow_print("\nEnd of demo. Thanks for playing!", delay=0.03)
        break


if __name__ == "__main__":
    main()
