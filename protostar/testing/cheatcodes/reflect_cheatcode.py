from protostar.starknet import Cheatcode, DelayedBuilder

from .reflect.reflector import Reflector


class ReflectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reflect"

    def build(self) -> DelayedBuilder:
        return DelayedBuilder(lambda exec_locals: Reflector(exec_locals["ids"]))
