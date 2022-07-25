from typing import Callable
from starkware.cairo.lang.vm.vm_consts import VmConsts
from protostar.starknet.cheatcode import Cheatcode
from protostar.commands.test.cheatcodes.reflect.reflector import Reflector


class ReflectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reflect"

    def build(self) -> Callable[[VmConsts], Reflector]:
        return self.reflect

    # pylint: disable=R0201
    def reflect(self, ids: VmConsts) -> Reflector:
        return Reflector(ids)
