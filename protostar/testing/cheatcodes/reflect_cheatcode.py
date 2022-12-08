from typing import Callable

from starkware.cairo.lang.vm.vm_consts import VmConsts

from protostar.starknet import Cheatcode

from .reflect.reflector import Reflector


class ReflectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reflect"

    def build(self) -> Callable[[VmConsts], Reflector]:
        return self.reflect

    def reflect(self, ids: VmConsts) -> Reflector:
        return Reflector(ids)
