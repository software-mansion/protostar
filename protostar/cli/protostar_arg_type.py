from starkware.starknet.utils.api_utils import cast_to_felts

from protostar.starknet_gateway import Fee

from .arg_type import ArgType


class FeltArgType(ArgType[int]):
    def get_name(self) -> str:
        return "felt"

    def parse(self, arg: str) -> int:
        # pylint: disable=unbalanced-tuple-unpacking
        [output] = cast_to_felts([arg])
        return output


class FeeArgType(ArgType[Fee]):
    def get_name(self) -> str:
        return "fee"

    def parse(self, arg: str) -> Fee:
        if arg == "auto":
            return arg
        return int(arg)
