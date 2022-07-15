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

from protostar.deployer.gateway_response import SuccessfulGatewayResponse
from protostar.deployer.network_config import NetworkConfig
from protostar.deployer.starkware.starknet_cli import deploy
from protostar.protostar_exception import ProtostarException


class InvalidNetworkConfigurationException(BaseException):
    pass


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


class Deployer:
    def __init__(self, project_root_path: Path) -> None:
        self._project_root_path = project_root_path

    @staticmethod
    def build_network_config(
        gateway_url: Optional[str] = None,
        network: Optional[str] = None,
    ) -> NetworkConfig:
        network_config: Optional[NetworkConfig] = None

        if network:
            network_config = NetworkConfig.from_starknet_network_name(network)
        if gateway_url:
            network_config = NetworkConfig(gateway_url=gateway_url)

        if network_config is None:
            raise InvalidNetworkConfigurationException()

        return network_config

    # pylint: disable=too-many-arguments
    async def deploy(
        self,
        compiled_contract_path: Path,
        gateway_url: str,
        inputs: Optional[List[str]] = None,
        token: Optional[str] = None,
        salt: Optional[str] = None,
    ) -> SuccessfulGatewayResponse:

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
        compilation_output_filepath: Path,
        gateway_url: str,
        signature: Optional[List[str]] = None,
        token: Optional[str] = None,
    ):
        """Protostar version of starknet_cli::declare"""
        sender = DECLARE_SENDER_ADDRESS
        max_fee = 0
        nonce = 0

        try:
            with open(
                self._project_root_path / compilation_output_filepath,
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
                    signature=signature,
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

                contract_address = int(gateway_response["address"], 16)

                return SuccessfulGatewayResponse(
                    address=contract_address,
                    code=gateway_response["code"],
                    transaction_hash=gateway_response["transaction_hash"],
                )
        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(
                compilation_output_filepath
            ) from err
