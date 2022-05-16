from io import TextIOWrapper
from typing import Optional, Sequence, cast

from services.external_api.base_client import RetryConfig
from starkware.starknet.cli.starknet_cli import validate_arguments
from starkware.starknet.definitions import fields
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.services.api.gateway.gateway_client import GatewayClient
from starkware.starknet.services.api.gateway.transaction import Deploy
from starkware.starknet.utils.api_utils import cast_to_felts
from typing_extensions import TypedDict


class GatewayResponseFacade(TypedDict):
    code: str
    address: str
    transaction_hash: str


async def deploy_contract(
    gateway_url: str,
    compiled_contract_file: TextIOWrapper,
    constructor_args: Optional[Sequence[str | int]] = None,
    salt: Optional[str] = None,
    token: Optional[str] = None,
) -> GatewayResponseFacade:
    """Version of deploy function from starkware.starknet.cli.starknet_cli independent of CLI logic."""

    inputs = cast_to_felts(constructor_args or [])

    gateway_client = GatewayClient(
        url=gateway_url, retry_config=RetryConfig(n_retries=1)
    )
    if salt is not None and not salt.startswith("0x"):
        raise ValueError(f"salt must start with '0x'. Got: {salt}.")

    numeric_salt: int = 0
    try:
        numeric_salt = (
            fields.ContractAddressSalt.get_random_value()
            if salt is None
            else int(salt, 16)
        )
    except ValueError as err:
        raise ValueError("Invalid salt format.") from err

    contract_definition = ContractDefinition.loads(compiled_contract_file.read())
    abi = contract_definition.abi
    assert abi is not None, "Missing ABI in the given contract definition."

    for abi_entry in abi:
        if abi_entry["type"] == "constructor":
            validate_arguments(
                inputs=inputs,
                abi_entry=abi_entry,
                identifier_manager=identifier_manager_from_abi(abi=abi),
            )
            break
    else:
        if len(inputs) > 0:
            raise ValueError(
                "Constructor args cannot be specified for contracts without a constructor."
            )

    tx = Deploy(
        contract_address_salt=numeric_salt,
        contract_definition=contract_definition,
        constructor_calldata=inputs,
    )  # type: ignore

    return cast(
        GatewayResponseFacade, await gateway_client.add_transaction(tx=tx, token=token)
    )
