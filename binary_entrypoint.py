import os
import sys
from itertools import cycle
from pathlib import Path
from shutil import get_terminal_size
from threading import Thread
from time import sleep

import certifi


class ProtostarInitializingIndicator:
    def __init__(self):
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
            print(f"\r{step}", flush=True, end="")
            sleep(self.interval)

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="\r", flush=True)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stop()


if __name__ == "__main__":
    try:
        with ProtostarInitializingIndicator():
            from protostar import main

            # Use certifi certs to avoid problems on mac os
            os.environ["SSL_CERT_FILE"] = certifi.where()

        main(Path(__file__).parent)

    except ImportError as err:
        # pylint: disable=no-member
        if err.msg.startswith("Failed to initialize: Bad git executable."):
            print(
                "Protostar requires git executable to be specified in $PATH. Did you install git?"
            )
            sys.exit()
        raise err
