from protostar.starknet.cheatcode import Cheatcode
from protostar.commands.test.cheatcodes.reflect.reflector import Reflector
from protostar.starknet.delayed_builder import DelayedBuilder


class ReflectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reflect"

    def build(self) -> DelayedBuilder:
        return DelayedBuilder(lambda exec_locals: Reflector(exec_locals["ids"]))
