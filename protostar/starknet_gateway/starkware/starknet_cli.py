from io import TextIOWrapper
from typing import Optional, Sequence, Union

from services.external_api.client import RetryConfig
from starkware.starknet.cli.starknet_cli import validate_arguments
from starkware.starknet.definitions import constants, fields
from starkware.starknet.public.abi_structs import identifier_manager_from_abi
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.services.api.gateway.gateway_client import GatewayClient
from starkware.starknet.services.api.gateway.transaction import Deploy
from starkware.starknet.utils.api_utils import cast_to_felts
from starkware.starkware_utils.error_handling import StarkErrorCode

from protostar.starknet_gateway.gateway_response import SuccessfulDeployResponse
from protostar.protostar_exception import ProtostarException


class DeployContractException(ProtostarException):
    pass


async def deploy(
    gateway_url: str,
    compiled_contract_file: TextIOWrapper,
    constructor_args: Optional[Sequence[Union[str, int]]] = None,
    salt: Optional[str] = None,
    token: Optional[str] = None,
) -> SuccessfulDeployResponse:
    """Version of deploy function from starkware.starknet.cli.starknet_cli independent of CLI logic."""

    inputs = cast_to_felts(constructor_args or [])

    if salt is not None and not salt.startswith("0x"):
        raise ValueError(f"salt must start with '0x'. Got: {salt}.")

    try:
        numeric_salt: int = (
            fields.ContractAddressSalt.get_random_value()
            if salt is None
            else int(salt, 16)
        )
    except ValueError as err:
        raise ValueError("Invalid salt format.") from err

    contract_class = ContractClass.loads(data=compiled_contract_file.read())
    abi = contract_class.abi
    assert abi is not None, "Missing ABI in the given contract class."

    for abi_entry in abi:
        if abi_entry["type"] == "constructor":
            validate_arguments(
                inputs=inputs,
                abi_entry=abi_entry,
                identifier_manager=identifier_manager_from_abi(abi=abi),
            )
            break
    else:
        if len(inputs) != 0:
            raise ValueError(
                "Constructor args cannot be specified for contracts without a constructor."
            )

    tx = Deploy(
        contract_address_salt=numeric_salt,
        contract_definition=contract_class,
        constructor_calldata=inputs,
        version=constants.TRANSACTION_VERSION,
    )  # type: ignore

    gateway_client = GatewayClient(
        url=gateway_url, retry_config=RetryConfig(n_retries=1)
    )
    gateway_response = await gateway_client.add_transaction(tx=tx, token=token)

    if gateway_response["code"] != StarkErrorCode.TRANSACTION_RECEIVED.name:
        raise DeployContractException(
            message=f"Failed to send transaction. Response: {gateway_response}."
        )

    contract_address = int(gateway_response["address"], 16)

    return SuccessfulDeployResponse(
        address=contract_address,
        code=gateway_response["code"],
        transaction_hash=gateway_response["transaction_hash"],
    )
