from protostar.starknet.cheatcode import Cheatcode
from protostar.commands.test.cheatcodes.reflect.reflector import Reflector
from protostar.commands.test.test_environment_exceptions import CheatcodeException


class ReflectCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "reflect"

    def build(self) -> "ReflectClass":
        return ReflectClass()


class ReflectClass:
    def __getattr__(self, name):
        return getattr(Reflector(Cheatcode._exec_locals["ids"]), name)

    # pylint: disable=R0201
    def get(self):
        raise CheatcodeException("reflect", "get() called on no value.")
