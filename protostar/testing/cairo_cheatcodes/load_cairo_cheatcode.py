from typing import Callable, Any

from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode


class LoadCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "load"

    def build(
        self,
    ) -> Callable[[str], Any]:
        return self.load

    def load(self, name: str) -> Any:
        return self.cheaters.contracts.load(name)
