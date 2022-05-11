from typing import Callable

from src.commands.test.cheatcodes._cheatcode import Cheatcode
from src.commands.test.starkware.cheatable_syscall_handler import (
    CheatableSysCallHandler,
)


class RollCheatcode(Cheatcode):
    def __init__(self, cheatable_syscall_handler: CheatableSysCallHandler) -> None:
        super().__init__()
        self._cheatable_syscall_handler = cheatable_syscall_handler

    @property
    def name(self) -> str:
        return "roll"

    def build(self) -> Callable:
        def roll(blk_number: int):
            self._cheatable_syscall_handler.set_block_number(blk_number)

        return roll
