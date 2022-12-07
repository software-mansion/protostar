from typing import List, Optional

from starkware.starknet.compiler.compile import compile_starknet_files
from starkware.starknet.services.api.contract_class import ContractClass


def get_contract_class(
    source: Optional[str] = None,
    contract_class: Optional[ContractClass] = None,
    cairo_path: Optional[List[str]] = None,
    disable_hint_validation: bool = False,
) -> ContractClass:
    """
    This function (compared to the original) allows disabling hint validation.
    """
    assert (source is None) != (
        contract_class is None
    ), "Exactly one of source, contract_class should be supplied."
    if contract_class is None:
        contract_class = compile_starknet_files(
            files=[source],
            debug_info=True,
            cairo_path=cairo_path,
            disable_hint_validation=disable_hint_validation,
        )
        source = None
        cairo_path = None
    assert (
        cairo_path is None
    ), "The cairo_path argument can only be used with the source argument."
    assert contract_class is not None
    return contract_class
