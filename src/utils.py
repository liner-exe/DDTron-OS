import sys
import time

def print_typing(text: str, delay: float = 0.03, end: str = "\n"):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)

    sys.stdout.write(end)
    sys.stdout.flush()


tprint = print_typing