from logging import Logger
from pathlib import Path
from typing import Callable, List, Optional

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.transactions.deploy import make_deploy_tx
from starknet_py.transactions.declare import make_declare_tx

from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway.gateway_response import (
    SuccessfulDeclareResponse,
    SuccessfulDeployResponse,
)
from protostar.starknet_gateway.starknet_request import StarknetRequest
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
    class Builder:
        def __init__(self, project_root_path: Path):
            self._gateway_facade = GatewayFacade(project_root_path)

        def set_network(self, network: str) -> None:
            self._gateway_facade._gateway_client = GatewayClient(network)

        def set_logger(
            self, logger: Logger, log_color_provider: LogColorProvider
        ) -> None:
            self._gateway_facede._logger = logger
            self._gateway_facade._log_color_provider = log_color_provider

        def build(self) -> "GatewayFacade":
            assert hasattr(self._gateway_facade, "_gateway_client")
            return self._gateway_facade

    def __init__(self, project_root_path: Path) -> None:
        self._project_root_path = project_root_path
        self._starknet_requests: List[StarknetRequest] = []
        self._logger: Optional[Logger] = None
        self._log_color_provider: Optional[LogColorProvider] = None

    def set_logger(self, logger: Logger, log_color_provider: LogColorProvider) -> None:
        self._logger = logger
        self._log_color_provider = log_color_provider

    def get_starknet_requests(self) -> List[StarknetRequest]:
        return self._starknet_requests.copy()

    # pylint: disable=too-many-arguments
    async def deploy(
        self,
        compiled_contract_path: Path,
        inputs: Optional[List[int]] = None,
        token: Optional[str] = None,
        salt: Optional[str] = None,
        wait_for_acceptance: bool = False,
    ) -> SuccessfulDeployResponse:
        try:
            with open(compiled_contract_path, "r") as f:
                compiled_contract = f.read()
        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(compiled_contract_path) from err

        tx = make_deploy_tx(
            compiled_contract=compiled_contract, constructor_calldata=inputs, salt=salt
        )

        result = await self._gateway_client.deploy(tx, token)
        await self._gateway_client.wait_for_tx(
            result.hash, wait_for_accept=wait_for_acceptance
        )

        return SuccessfulDeployResponse(
            code=result.code,
            address=result.contract_address,
            transaction_hash=result.transaction_hash,
        )

    # pylint: disable=too-many-locals
    async def declare(
        self,
        compiled_contract_path: Path,
        # signature: Optional[List[int]] = None,
        token: Optional[str] = None,
        wait_for_acceptance: bool = False,
    ) -> SuccessfulDeclareResponse:
        try:
            with open(compiled_contract_path, "r") as f:
                compiled_contract = f.read()
        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(compiled_contract_path) from err

        tx = make_declare_tx(
            compiled_contract=compiled_contract,
        )

        result = await self._gateway_client.declare(tx, token)

        await self._gateway_client.wait_for_tx(
            result.hash, wait_for_accept=wait_for_acceptance
        )

        return SuccessfulDeclareResponse(
            code=result.code,
            class_hash=result.class_hash,
            transaction_hash=result.transaction_hash,
        )

    def _register_request(
        self, action: StarknetRequest.Action, payload: StarknetRequest.Payload
    ) -> Callable[[StarknetRequest.Payload], None]:

        if self._logger:
            self._logger.info(
                "\n".join(
                    [
                        StarknetRequest.prettify_data_flow(
                            color_provider=self._log_color_provider,
                            action=action,
                            direction="TO_STARKNET",
                        ),
                        StarknetRequest.prettify_payload(
                            color_provider=self._log_color_provider, payload=payload
                        ),
                    ]
                )
            )

        def register_response(response: StarknetRequest.Payload):
            if self._logger:
                self._logger.info(
                    "\n".join(
                        [
                            StarknetRequest.prettify_data_flow(
                                color_provider=self._log_color_provider,
                                action=action,
                                direction="FROM_STARKNET",
                            ),
                            StarknetRequest.prettify_payload(
                                color_provider=self._log_color_provider,
                                payload=response,
                            ),
                        ]
                    )
                )

            self._starknet_requests.append(
                StarknetRequest(action=action, payload=payload, response=response)
            )

        return register_response
