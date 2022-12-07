import multiprocessing
import os
import sys
from itertools import cycle
from pathlib import Path
from shutil import get_terminal_size
from threading import Thread
from time import perf_counter, sleep
from typing import Any

import certifi
from colorama.ansitowin32 import StreamWrapper

SCRIPT_ROOT = Path(__file__).parent


def init():
    multiprocessing.freeze_support()

    start_time = perf_counter()
    fix_ssl_certificate_errors_on_macos()
    main = import_protostar_main()
    main(SCRIPT_ROOT, start_time)


def fix_ssl_certificate_errors_on_macos():
    os.environ["SSL_CERT_FILE"] = certifi.where()


def import_protostar_main():
    with ProtostarInitializingIndicator(disabled=not is_terminal()):
        # pylint: disable="import-outside-toplevel"
        from protostar import main

        return main


def is_terminal() -> bool:
    return StreamWrapper(sys.stdout, sys.stdin).isatty()


class ProtostarInitializingIndicator:
    def __init__(self, disabled: bool):
        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.interval = 1 / len(self.steps)
        self.done = False
        self._disabled = disabled

    def start(self):
        if self._disabled:
            return

        self._thread.start()
        return self

    def _animate(self):
        for step in cycle(self.steps):
            if self.done:
                break
            print(f"\r{step}", flush=True, end="")
            sleep(self.interval)

    def stop(self):
        if self._disabled:
            return

        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="\r", flush=True)

    def __enter__(self):
        self.start()

    def __exit__(self, *args: Any, **kwargs: Any):
        self.stop()


if __name__ == "__main__":
    init()
