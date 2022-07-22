from logging import Logger
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
from protostar.starknet_gateway.starknet_interaction import StarknetInteraction
from protostar.starknet_gateway.starkware.starknet_cli import deploy
from protostar.utils.log_color_provider import LogColorProvider


class TransactionException(ProtostarException):
    pass


class CompilationOutputNotFoundException(ProtostarException):
    def __init__(self, compilation_output_filepath: Path):
        super().__init__(
            f"Couldn't find `{str(compilation_output_filepath.resolve())}`\n"
            "Did you run `protostar build`?"
        )
        self._compilation_output_filepath = compilation_output_filepath


class GatewayFacade:
    def __init__(
        self,
        project_root_path: Path,
    ) -> None:
        self._project_root_path = project_root_path
        self.starknet_interactions: List[StarknetInteraction] = []
        self._logger: Optional[Logger] = None
        self._log_color_provider: Optional[LogColorProvider] = None

    def set_logger(self, logger: Logger, log_color_provider: LogColorProvider) -> None:
        self._logger = logger
        self._log_color_provider = log_color_provider

    # pylint: disable=too-many-arguments
    async def deploy(
        self,
        compiled_contract_path: Path,
        gateway_url: str,
        inputs: Optional[List[int]] = None,
        token: Optional[str] = None,
        salt: Optional[str] = None,
    ) -> SuccessfulDeployResponse:

        compilation_output_filepath = self._project_root_path / compiled_contract_path

        try:
            with open(
                compilation_output_filepath,
                mode="r",
                encoding="utf-8",
            ) as compiled_contract_file:
                self._add_interaction(
                    StarknetInteraction(
                        direction="TO_STARKNET",
                        action="DEPLOY",
                        payload={
                            "contract": str(compilation_output_filepath),
                            "gateway_url": gateway_url,
                            "constructor_args": inputs,
                            "salt": salt,
                            "token": token,
                        },
                    )
                )
                response = await deploy(
                    gateway_url=gateway_url,
                    compiled_contract_file=compiled_contract_file,
                    constructor_args=inputs,
                    salt=salt,
                    token=token,
                )
                self._add_interaction(
                    StarknetInteraction(
                        direction="FROM_STARKNET",
                        action="DEPLOY",
                        payload=response.__dict__,
                    )
                )
                return response

        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(
                compilation_output_filepath
            ) from err

    # pylint: disable=too-many-locals
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

        compiled_contract_abs_path = self._project_root_path / compiled_contract_path
        try:
            with open(
                compiled_contract_abs_path,
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

                self._add_interaction(
                    StarknetInteraction(
                        direction="TO_STARKNET",
                        action="DECLARE",
                        payload={
                            "contract": str(compiled_contract_abs_path),
                            "sender_address": sender,
                            "max_fee": max_fee,
                            "version": constants.TRANSACTION_VERSION,
                            "signature": signature or [],
                            "nonce": nonce,
                        },
                    )
                )
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
                response = SuccessfulDeclareResponse(
                    class_hash=class_hash,
                    code=gateway_response["code"],
                    transaction_hash=gateway_response["transaction_hash"],
                )
                self._add_interaction(
                    StarknetInteraction(
                        direction="FROM_STARKNET",
                        action="DECLARE",
                        payload=response.__dict__,
                    )
                )
                return response
        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(compiled_contract_path) from err

    def _add_interaction(self, starknet_interaction: StarknetInteraction):
        if self._logger:
            self._logger.info(
                starknet_interaction.prettify(color_provider=self._log_color_provider)
            )
        self.starknet_interactions.append(starknet_interaction)
