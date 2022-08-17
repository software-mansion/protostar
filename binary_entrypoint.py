import os
import sys
from itertools import cycle
from pathlib import Path
from shutil import get_terminal_size
from threading import Thread
from time import perf_counter, sleep

import certifi

SCRIPT_ROOT = Path(__file__).parent


def init():
    start_time = perf_counter()
    fix_ssl_certificate_errors_on_mac_os()
    main = import_protostar_main()
    main(SCRIPT_ROOT, start_time)


def fix_ssl_certificate_errors_on_mac_os():
    os.environ["SSL_CERT_FILE"] = certifi.where()


def import_protostar_main():
    try:
        # pylint: disable="import-outside-toplevel"
        from protostar import main

        return main
    except ImportError as err:
        handle_git_error(err)
        raise err


def handle_git_error(err: ImportError):
    if err.msg.startswith("Failed to initialize: Bad git executable."):
        print(
            "Protostar requires git executable to be specified in $PATH. Did you install git?"
        )
        sys.exit()


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
    init()
