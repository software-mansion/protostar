from typing import List, Optional

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.cheatcode_factory import CheatcodeFactory
from protostar.utils.starknet_compilation import StarknetCompiler


class MigratorCheatcodeFactory(CheatcodeFactory):
    def __init__(self) -> None:
        super().__init__()
        self._starknet_compiler: Optional[StarknetCompiler] = None

    def set_starknet_compiler(self, starknet_compiler: StarknetCompiler):
        self._starknet_compiler = starknet_compiler

    def build(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        assert self._starknet_compiler is not None

        return []
