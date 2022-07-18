from pathlib import Path
from typing import List, Optional

from services.external_api.client import RetryConfig
from starkware.starknet.definitions import constants
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.services.api.gateway.gateway_client import GatewayClient
from starkware.starknet.services.api.gateway.transaction import (
    DECLARE_SENDER_ADDRESS,
    Declare,
)
from starkware.starkware_utils.error_handling import StarkErrorCode

from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway.gateway_response import (
    SuccessfulDeclareResponse,
    SuccessfulDeployResponse,
)
from protostar.starknet_gateway.starkware.starknet_cli import deploy


class TransactionException(ProtostarException):
    pass


class CompilationOutputNotFoundException(ProtostarException):
    def __init__(self, compilation_output_filepath: Path):
        super().__init__(str(compilation_output_filepath))
        self._compilation_output_filepath = compilation_output_filepath

    def __str__(self) -> str:
        return (
            f"Couldn't find `{self._compilation_output_filepath}`\n"
            "Did you run `protostar build` before running this command?"
        )


class GatewayFacade:
    def __init__(self, project_root_path: Path) -> None:
        self._project_root_path = project_root_path

    # pylint: disable=too-many-arguments
    async def deploy(
        self,
        compiled_contract_path: Path,
        gateway_url: str,
        inputs: Optional[List[str]] = None,
        token: Optional[str] = None,
        salt: Optional[str] = None,
    ) -> SuccessfulDeployResponse:

        compilation_output_filepath = self._project_root_path / compiled_contract_path

        try:
            with open(
                self._project_root_path / compilation_output_filepath,
                mode="r",
                encoding="utf-8",
            ) as compiled_contract_file:
                return await deploy(
                    gateway_url=gateway_url,
                    compiled_contract_file=compiled_contract_file,
                    constructor_args=inputs,
                    salt=salt,
                    token=token,
                )

        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(
                compilation_output_filepath
            ) from err

    async def declare(
        self,
        compiled_contract_path: Path,
        gateway_url: str,
        signature: Optional[List[str]] = None,
        token: Optional[str] = None,
    ):
        """Protostar version of starknet/cli/starknet_cli.py::declare"""

        # The following parameters are hardcoded because Starknet CLI have asserts checking if they are equal to these
        # values. Once Starknet removes these asserts, these parameters should be configurable by the user.
        sender = DECLARE_SENDER_ADDRESS
        max_fee = 0
        nonce = 0

        try:
            with open(
                self._project_root_path / compiled_contract_path,
                mode="r",
                encoding="utf-8",
            ) as compiled_contract_file:

                tx = Declare(
                    contract_class=ContractClass.loads(
                        data=compiled_contract_file.read()
                    ),
                    sender_address=sender,
                    max_fee=max_fee,
                    version=constants.TRANSACTION_VERSION,
                    signature=signature or [],
                    nonce=nonce,
                )  # type: ignore

                gateway_client = GatewayClient(
                    url=gateway_url, retry_config=RetryConfig(n_retries=1)
                )
                gateway_response = await gateway_client.add_transaction(
                    tx=tx, token=token
                )

                if gateway_response["code"] != StarkErrorCode.TRANSACTION_RECEIVED.name:
                    raise TransactionException(
                        message=f"Failed to send transaction. Response: {gateway_response}."
                    )

                class_hash = int(gateway_response["class_hash"], 16)

                return SuccessfulDeclareResponse(
                    class_hash=class_hash,
                    code=gateway_response["class_hash"],
                    transaction_hash=gateway_response["transaction_hash"],
                )
        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(compiled_contract_path) from err
