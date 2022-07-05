from contextlib import asynccontextmanager
from typing import Set, Callable

HookHandler = Callable[[], None]


class Hook:
    def __init__(self):
        self._hooks: Set[HookHandler] = set()

    def on(self, listener: HookHandler):
        self._hooks.add(listener)

    def off(self, listener: HookHandler):
        self._hooks.remove(listener)

    @asynccontextmanager
    async def run(self):
        try:
            yield
            for hook in self._hooks:
                hook()
        finally:
            self._hooks.clear()
