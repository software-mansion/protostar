from starkware.starknet.utils.api_utils import cast_to_felts

from .arg_type import ArgType


class FeltArgType(ArgType[int]):
    def get_name(self) -> str:
        return "felt"

    def parse(self, arg: str) -> int:
        # pylint: disable=unbalanced-tuple-unpacking
        [output] = cast_to_felts([arg])
        return output
