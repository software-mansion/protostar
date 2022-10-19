from typing import Optional

from protostar.scripting.typing import CairoOrPythonData


def call(
    contract_address: int,
    function_name: str,
    inputs: Optional[CairoOrPythonData] = None,
) -> None:
    raise NotImplementedError
