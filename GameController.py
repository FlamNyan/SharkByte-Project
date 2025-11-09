import random
from UI import slow_print, slow_input, print_block
from Characters import Character, enemy_templates
from Combat import Combat

debt = random.randint(250, 350)

def show_intro():
    # Clear screen (works on Windows, Mac, Linux)
    import os
    import time
    os.system("cls" if os.name == "nt" else "clear")

    slow_print("[The arena is dark. Footsteps echo.]", delay=0.02)
    time.sleep(0.5)

    print()
    print_block('???: "Wake up. You’re on in five."', delay=0.04)
    time.sleep(0.5)

    print()
    print_block(
        '???: "You remember why you’re here, right? '
        f'Not for glory. Not for honor. For debt. {debt} gold, to be exact..."',
        delay=0.04
    )
    time.sleep(0.7)

    print()
    slow_print("[A door creaks open. Light spills in.]", delay=0.04)
    time.sleep(0.5)

    print()
    print_block(
        '???: "Out there, nobody cares how you swing a sword. '
        'They care if you choose right. '
        'Attack, Block, Feint—three little moves between you and the grave."',
        delay=0.04
    )
    time.sleep(0.9)

    print()
    print_block(
        '???: "Read them, break them, survive them. '
        'Every duel you win buys you one more day. Every mistake… well."',
        delay=0.04
    )
    time.sleep(0.9)

    print()
    slow_print("[The crowd roars in the distance.]", delay=0.02)
    time.sleep(0.7)

    print()
    slow_print('???: "Enough talk. Step into the circle."', delay=0.04)
    time.sleep(0.9)

    print()
    slow_print("VIGOR RISES WHEN BLADES MEET.", delay=0.03)
    slow_print("ARMOR CRACKS WHEN GUARDS FAIL.", delay=0.03)
    slow_print("ONLY YOUR CHOICES DECIDE THE REST.", delay=0.03)
    time.sleep(0.7)

    print()
    player_name = slow_input(
        '???: "Whether you live or die, who do you wish to be known as?"',
        delay=0.04
    ).strip()
    if not player_name:
        player_name = "Unknown Challenger"
    time.sleep(0.7)

    print()
    slow_print(f'???: "Give them hell, {player_name}!"', delay=0.06)

    print()
    input("Press Enter to enter the arena... \n")

    return player_name

def main():
    # Intro + player creation
    player_name = show_intro()

    player = Character(
        name=player_name,
        health=20,
        money=0,
        armor=5,
        damage=5
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

    slow_print(
        f"\nEnd of demo. Result: {result}. "
        f"You have {player.money} gold and {player.vigor} Vigor.",
        delay=0.03
    )

if __name__ == "__main__":
    main()
