from protostar.starknet.cheatcode import Cheatcode
from protostar.commands.test.cheatcodes.reflect.reflector import Reflector


class ReflectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reflect"

    def build(self) -> Reflector:
        return Reflector()
