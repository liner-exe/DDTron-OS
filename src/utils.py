import sys
import time

def print_typing(text: str, delay: float = 0.03, end: str = "\n"):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)

    sys.stdout.write(end)
    sys.stdout.flush()

def format_duration(seconds: float):
    total_seconds = int(seconds)

    minutes = total_seconds // 60
    seconds = total_seconds % 60

    return f"{minutes:02d}:{seconds:02d}"

tprint = print_typing