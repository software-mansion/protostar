from typing import Callable, Any

from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode


class StoreCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "store"

    def build(
        self,
    ) -> Callable[[str, Any], None]:
        return self.store

    def store(self, name: str, value: Any) -> None:
        self.cheaters.contracts.store(name=name, value=value)
