from typing import Literal, Union

from protostar.starknet import Wei

Fee = Union[Wei, Literal["auto"]]
