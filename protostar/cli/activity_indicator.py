from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep


class ActivityIndicator:
    """NOTE: Don't put anything to stdout while this indicator is active."""

    def __init__(self, message: str):
        self.message = message

        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.interval = 1 / len(self.steps)
        self.done = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for step in cycle(self.steps):
            if self.done:
                break
            print(f"\r{self.message} {step}", flush=True, end="")
            sleep(self.interval)

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="\r", flush=True)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stop()
