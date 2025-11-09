# UI.py
import time
import textwrap

# Print text character by character
# Delay determines how slow each character is printed after another
def slow_print(text, delay=0.03):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

# Apply slow_print function
# Then apply an input
def slow_input(prompt, delay=0.03):
    slow_print(prompt, delay=delay)
    return input("> ")

# slow_print function for long text
def print_block(text, delay=0.03):
    wrapped = textwrap.fill(text, width=80)
    slow_print(wrapped, delay=delay)
