from typing import Any, Callable
from starkware.cairo.lang.vm.vm_consts import VmConsts
from protostar.starknet.cheatcode import Cheatcode
from protostar.commands.test.cheatcodes.reflect.reflector import Reflector


class ReflectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reflect"

    def build(self) -> Callable[..., Any]:
        return self.reflect

    # pylint: disable=R0201
    def reflect(self, ids: VmConsts):
        return Reflector(ids)
