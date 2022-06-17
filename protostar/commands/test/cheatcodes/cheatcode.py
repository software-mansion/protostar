from abc import abstractmethod
from typing import Any, Type, cast

from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler

from protostar.commands.test.starkware.cheatable_carried_state import CheatableCarriedState
from protostar.commands.test.starkware.cheatable_starknet_general_config import CheatableStarknetGeneralConfig


class Cheatcode(BusinessLogicSysCallHandler):
    @property
    def cheatable_state(self):
        return cast(CheatableCarriedState, self.state)

    @property
    def cheatable_global_config(self):
        return cast(CheatableStarknetGeneralConfig, self.state)

    @staticmethod
    @abstractmethod
    def name() -> str:
        ...

    @abstractmethod
    def execute(self) -> Any:
        ...


class CheatcodeFactory():
    def __init__(self, *args, **kwargs): 
        self.args = args
        self.kwargs = kwargs

    def build(self, cheatcode_type: Type[Cheatcode]):
        return cheatcode_type(*self.args, **self.kwargs)
