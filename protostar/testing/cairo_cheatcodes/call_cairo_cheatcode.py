import asyncio
from typing import Any, Callable, Optional

from protostar.starknet import CheatcodeException
from protostar.starknet.cheaters.contracts import ContractsCheaterException
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.starknet.data_transformer import CairoOrPythonData

from protostar.contract_types import DeployedContract


class CallCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "call"

    def build(self) -> Callable[[Any], Any]:
        return self.call_deployed

    def call_deployed(
        self,
        deployed: DeployedContract,
        class_hash: int,
        fn_name: str,
        inputs: Optional[CairoOrPythonData] = None,
    ):
        return asyncio.run(
            self._call(
                deployed=deployed, class_hash=class_hash, fn_name=fn_name, inputs=inputs
            )
        )

    async def _call(
        self,
        deployed: DeployedContract,
        class_hash: int,
        fn_name: str,
        inputs: Optional[CairoOrPythonData] = None,
    ):
        try:
            return await self.cheaters.contracts.call(
                deployed=deployed,
                class_hash=class_hash.to_bytes(32, "big"),
                fn_name=fn_name,
                inputs=inputs,
            )
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
