import time
import textwrap

def slow_print(text, delay=0.03):
    # Function that prints text character by character
    # Delay determines how slow each key ends up getting typed
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  # newline at the end

def slow_input(prompt, delay=0.03):
    # Slow print, then input
    slow_print(prompt, delay=delay)
    return input("> ")


def print_block(text, delay=0.03):
    # Slow print function, but for longer text
    wrapped = textwrap.fill(text, width=80)
    slow_print(wrapped, delay=delay)

def show_intro():
    # Clear screen (works on Windows, Mac, Linux)
    import os
    os.system("cls" if os.name == "nt" else "clear")

    slow_print("[The screen is dark. Footsteps echo.]", delay=0.02)
    time.sleep(0.5)

    print()
    print_block('???: "Wake up. You’re on in five."', delay=0.04)
    time.sleep(0.5)

    print()
    print_block('???: "You remember why you’re here, right? '
                'Not for glory. Not for honor. For debt. 200 gold to be exact..."', delay=0.04)
    time.sleep(0.7)

    print()
    slow_print("[A door creaks open. Light spills in.]", delay=0.04)
    time.sleep(0.5)

    print()
    print_block('???: "Out there, nobody cares how you swing a sword. '
                'They care if you choose right. '
                'Attack, Block, Feint—three little moves between you and the grave."', delay=0.04)
    time.sleep(0.9)

    print()
    print_block('???: "Read them, break them, survive them. '
                'Every duel you win buys you one more day. Every mistake… well."', delay=0.04)
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

    # SLOW-PRINT THE PROMPT, THEN GET INPUT NORMALLY
    print()
    player_name = slow_input('???: "Whether you live or die, who do you wish to be known as?"', delay=0.04)
    time.sleep(0.7)

    print()
    slow_print(f'???: "Give them hell, {player_name}!"', delay=0.06)

    print()
    input("Press Enter to enter the arena... \n")

# If you want this to run immediately when you start the script:
if __name__ == "__main__":
    show_intro()
