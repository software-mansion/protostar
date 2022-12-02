from typing import Any, Literal, Union

ContractFunctionInputType = Union[list[int], dict[str, Any]]
Wei = int
Fee = Union[Wei, Literal["auto"]]
ClassHash = int
