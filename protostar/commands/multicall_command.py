import logging
from argparse import Namespace
from typing import Optional

from protostar.cli import ProtostarCommand
from protostar.starknet_gateway.multicall import MulticallUseCase, MulticallInput


class MulticallCommand(ProtostarCommand):
    def __init__(self, multicall_use_case: MulticallUseCase) -> None:
        super().__init__()
        self._multicall_use_case = multicall_use_case

    @property
    def name(self) -> str:
        return "multicall"

    @property
    def description(self) -> str:
        return "Execute multiple deploy (via UDC) and invoke calls ensuring atomicity."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self):
        return []

    async def run(self, args: Namespace) -> None:
        multicall_input = MulticallInput(calls=[])
        # await self._multicall_use_case.execute(multicall_input)
