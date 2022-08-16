import dataclasses
from logging import Logger
from pathlib import Path
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Union

from starknet_py.contract import Contract, ContractFunction
from starknet_py.net.client_errors import ContractNotFoundError
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import AddressRepresentation, StarknetChainId
from starknet_py.transactions.declare import make_declare_tx
from starknet_py.transactions.deploy import make_deploy_tx
from starkware.starknet.definitions import constants
from starkware.starknet.services.api.gateway.transaction import DECLARE_SENDER_ADDRESS

from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway.gateway_response import (
    SuccessfulDeclareResponse,
    SuccessfulDeployResponse,
)
from protostar.starknet_gateway.starknet_request import StarknetRequest
from protostar.utils.log_color_provider import LogColorProvider

GatewayFacadeSupportedInputType = Union[List[int], Dict[str, Any]]


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
            self._project_root_path = project_root_path
            self._network: Optional[str] = None

        def set_network(self, network: str) -> None:
            self._network = network

        def build(self) -> "GatewayFacade":
            assert self._network is not None

            client = GatewayClient(
                # Starknet.py ignores chain parameter when
                # `mainnet` or `testnet` is passed into the client
                # `StarknetChainId.TESTNET` also works for devnet
                GatewayFacade.map_to_starknet_py_naming(self._network),
                chain=StarknetChainId.TESTNET,
            )

            return GatewayFacade(self._project_root_path, client)

    def __init__(
        self,
        project_root_path: Path,
        gateway_client: GatewayClient,
        logger: Optional[Logger] = None,
        log_color_provider: Optional[LogColorProvider] = None,
    ) -> None:
        self._project_root_path = project_root_path
        self._starknet_requests: List[StarknetRequest] = []
        self._logger: Optional[Logger] = logger
        self._log_color_provider: Optional[LogColorProvider] = log_color_provider
        self._gateway_client = gateway_client

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
        salt: Optional[int] = None,
        wait_for_acceptance: bool = False,
    ) -> SuccessfulDeployResponse:
        try:
            with open(
                self._project_root_path / compiled_contract_path, "r", encoding="utf-8"
            ) as file:
                compiled_contract = file.read()
        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(
                self._project_root_path / compiled_contract_path
            ) from err

        tx = make_deploy_tx(
            compiled_contract=compiled_contract,
            constructor_calldata=inputs or [],
            salt=salt,
        )

        register_response = self._register_request(
            action="DEPLOY",
            payload={
                "contract": str(self._project_root_path / compiled_contract_path),
                "network": GatewayFacade.map_from_starknet_py_naming(
                    str(self._gateway_client.net)
                ),
                "constructor_args": inputs,
                "salt": salt,
                "token": token,
            },
        )

        result = await self._gateway_client.deploy(tx, token)
        register_response(dataclasses.asdict(result))
        if wait_for_acceptance:
            if self._logger:
                self._logger.info("Waiting for acceptance...")
            await self._gateway_client.wait_for_tx(
                result.transaction_hash, wait_for_accept=wait_for_acceptance
            )

        return SuccessfulDeployResponse(
            code=result.code or "",
            address=result.contract_address,
            transaction_hash=result.transaction_hash,
        )

    # pylint: disable=too-many-locals
    async def declare(
        self,
        compiled_contract_path: Path,
        token: Optional[str] = None,
        wait_for_acceptance: bool = False,
        signature: Optional[List[int]] = None,
    ) -> SuccessfulDeclareResponse:
        try:
            with open(
                self._project_root_path / compiled_contract_path, "r", encoding="utf-8"
            ) as file:
                compiled_contract = file.read()
        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(
                self._project_root_path / compiled_contract_path
            ) from err

        # The following parameters are hardcoded because Starknet CLI have asserts checking if they are equal to these
        # values. Once Starknet removes these asserts, these parameters should be configurable by the user.
        sender = DECLARE_SENDER_ADDRESS
        max_fee = 0
        nonce = 0

        tx = make_declare_tx(
            compiled_contract=compiled_contract,
        )

        register_response = self._register_request(
            action="DECLARE",
            payload={
                "contract": str(self._project_root_path / compiled_contract_path),
                "sender_address": sender,
                "max_fee": max_fee,
                "version": constants.TRANSACTION_VERSION,
                "signature": signature or [],
                "nonce": nonce,
            },
        )

        result = await self._gateway_client.declare(tx, token)
        register_response(dataclasses.asdict(result))
        if wait_for_acceptance:
            if self._logger:
                self._logger.info("Waiting for acceptance...")
            await self._gateway_client.wait_for_tx(
                result.transaction_hash, wait_for_accept=wait_for_acceptance
            )

        return SuccessfulDeclareResponse(
            code=result.code or "",
            class_hash=result.class_hash,
            transaction_hash=result.transaction_hash,
        )

    async def call(
        self,
        address: AddressRepresentation,
        function_name: str,
        inputs: Optional[GatewayFacadeSupportedInputType] = None,
    ) -> NamedTuple:
        register_response = self._register_request(
            action="CALL",
            payload={
                "contract_address": address,
                "function_name": function_name,
                "inputs": str(inputs),
            },
        )
        contract_function = await self._create_contract_function(address, function_name)
        result = await self._call_function(contract_function, inputs)
        register_response({"result": str(result._asdict())})
        return result

    async def _create_contract_function(
        self, contract_address: AddressRepresentation, function_name: str
    ):
        try:
            contract = await Contract.from_address(
                address=contract_address, client=self._gateway_client
            )
        except ContractNotFoundError as err:
            raise ContractNotFoundException(contract_address) from err
        try:
            return contract.functions[function_name]
        except KeyError:
            raise UnknownFunctionException(function_name) from KeyError

    @staticmethod
    async def _call_function(
        contract_function: ContractFunction,
        inputs: Optional[GatewayFacadeSupportedInputType] = None,
    ):
        if inputs is None:
            inputs = {}
        if isinstance(inputs, List):
            return await contract_function.call(*inputs)
        return await contract_function.call(**inputs)

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

    @staticmethod
    def map_to_starknet_py_naming(name: str) -> str:
        if name == "alpha-goerli":
            return "testnet"
        if name == "alpha-mainnet":
            return "mainnet"
        return name

    @staticmethod
    def map_from_starknet_py_naming(name: str) -> str:
        if name == "testnet":
            return "alpha-goerli"
        if name == "mainnet":
            return "alpha-mainnet"
        return name


class UnknownFunctionException(ProtostarException):
    def __init__(self, function_name: str):
        super().__init__(f"Tried to call unknown function: '{function_name}'")


class ContractNotFoundException(ProtostarException):
    def __init__(self, contract_address: AddressRepresentation):
        super().__init__(f"Tried to call unknown contract:\n{contract_address}")
