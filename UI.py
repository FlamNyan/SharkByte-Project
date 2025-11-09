# UI.py
import time
import textwrap

def slow_print(text, delay=0.03):
    """Print text character by character for a little flair."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  # newline at the end

def slow_input(prompt, delay=0.03):
    """Slow print, then input."""
    slow_print(prompt, delay=delay)
    return input("> ")

def print_block(text, delay=0.03):
    """Wrap long text nicely, then slow_print each line."""
    wrapped = textwrap.fill(text, width=80)
    slow_print(wrapped, delay=delay)
