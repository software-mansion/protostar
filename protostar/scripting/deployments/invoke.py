from typing import Optional

from protostar.scripting.typing import CairoOrPythonData, Fee


def invoke(
    contract_address: int,
    function_name: str,
    inputs: Optional[CairoOrPythonData],
    *,
    wait_for_acceptance: Optional[bool] = None,
    max_fee: Optional[Fee] = None,
) -> None:
    raise NotImplementedError
