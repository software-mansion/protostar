import dataclasses
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Union

from starknet_py.contract import Contract, ContractFunction, InvokeResult
from starknet_py.net import AccountClient
from starknet_py.net.client import Client
from starknet_py.net.client_errors import ContractNotFoundError
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import AddressRepresentation
from starknet_py.net.signer import BaseSigner
from starknet_py.transaction_exceptions import TransactionFailedError
from starknet_py.transactions.deploy import make_deploy_tx
from starkware.starknet.public.abi import AbiType
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.services.api.gateway.transaction import (
    DEFAULT_DECLARE_SENDER_ADDRESS,
    Declare,
)

from protostar.compiler import CompiledContractReader
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway.account_tx_version_detector import (
    AccountTxVersionDetector,
)
from protostar.starknet_gateway.gateway_response import (
    SuccessfulDeclareResponse,
    SuccessfulDeployResponse,
)
from protostar.starknet_gateway.starknet_request import StarknetRequest
from protostar.utils.abi import has_abi_item
from protostar.utils.data_transformer import (
    CairoOrPythonData,
    DataTransformerException,
    from_python_transformer,
    to_python_transformer,
)
from protostar.utils.log_color_provider import LogColorProvider

ContractFunctionInputType = Union[List[int], Dict[str, Any]]

Wei = int


class GatewayFacade:
    def __init__(
        self,
        project_root_path: Path,
        gateway_client: GatewayClient,
        compiled_contract_reader: CompiledContractReader,
        logger: Optional[Logger] = None,
        log_color_provider: Optional[LogColorProvider] = None,
    ) -> None:
        self._project_root_path = project_root_path
        self._starknet_requests: List[StarknetRequest] = []
        self._logger: Optional[Logger] = logger
        self._log_color_provider: Optional[LogColorProvider] = log_color_provider
        self._gateway_client = gateway_client
        self._compiled_contract_reader = compiled_contract_reader
        self._account_tx_version_detector = AccountTxVersionDetector(
            self._gateway_client
        )

    def get_starknet_requests(self) -> List[StarknetRequest]:
        return self._starknet_requests.copy()

    async def deploy(
        self,
        compiled_contract_path: Path,
        inputs: Optional[ContractFunctionInputType] = None,
        token: Optional[str] = None,
        salt: Optional[int] = None,
        wait_for_acceptance: bool = False,
    ) -> SuccessfulDeployResponse:
        compiled_contract = self._load_compiled_contract(
            self._project_root_path / compiled_contract_path
        )
        cairo_inputs = self._prepare_constructor_inputs(inputs, compiled_contract_path)

        tx = make_deploy_tx(
            compiled_contract=compiled_contract,
            constructor_calldata=cairo_inputs,
            salt=salt,
        )

        register_response = self._register_request(
            action="DEPLOY",
            payload={
                "contract": str(self._project_root_path / compiled_contract_path),
                "network": str(self._gateway_client.net),
                "constructor_args": cairo_inputs,
                "salt": salt,
                "token": token,
            },
        )

        try:
            result = await self._gateway_client.deploy(tx, token)
            register_response(dataclasses.asdict(result))
            if wait_for_acceptance:
                if self._logger:
                    self._logger.info("Waiting for acceptance...")
                _, status = await self._gateway_client.wait_for_tx(
                    result.transaction_hash, wait_for_accept=wait_for_acceptance
                )
                result.code = status
        except TransactionFailedError as ex:
            raise TransactionException(str(ex)) from ex

        return SuccessfulDeployResponse(
            code=result.code or "",
            address=result.contract_address,
            transaction_hash=result.transaction_hash,
        )

    def _load_compiled_contract(self, compiled_contract_path: Path):
        try:
            return self._compiled_contract_reader.load_contract(compiled_contract_path)
        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(compiled_contract_path) from err

    def _prepare_constructor_inputs(
        self, inputs: Optional[CairoOrPythonData], compiled_contract_path: Path
    ):

        abi = self._compiled_contract_reader.load_abi_from_contract_path(
            compiled_contract_path
        )
        assert abi is not None

        if not has_abi_item(abi, "constructor"):
            if inputs:
                raise InputValidationException(
                    "Inputs provided to a contract with no constructor."
                )
            return []

        cairo_inputs = transform_constructor_inputs_from_python(abi, inputs)
        validate_cairo_inputs(abi, cairo_inputs)
        return cairo_inputs

    async def declare(
        self,
        compiled_contract_path: Path,
        account_address: str,
        signer: BaseSigner,
        wait_for_acceptance: bool,
        token: Optional[str],
        max_fee: Optional[Wei],
    ):
        compiled_contract = self._load_compiled_contract(
            self._project_root_path / compiled_contract_path
        )
        account_client = await self._create_account_client(
            account_address=account_address, signer=signer
        )
        declare_tx = await self._create_declare_tx_v1(
            compiled_contract=compiled_contract,
            account_client=account_client,
            auto_estimate_fee=max_fee is None,
            max_fee=max_fee,
        )
        register_response = self._register_request(
            action="DECLARE",
            payload={
                "contract": str(self._project_root_path / compiled_contract_path),
                "sender_address": declare_tx.sender_address,
                "max_fee": declare_tx.max_fee,
                "version": declare_tx.version,
                "nonce": declare_tx.nonce,
                "signature": declare_tx.signature,
            },
        )
        response = await self._gateway_client.declare(declare_tx, token=token)
        if wait_for_acceptance:
            if self._logger:
                self._logger.info("Waiting for acceptance...")
            _, code = await account_client.wait_for_tx(
                response.transaction_hash, wait_for_accept=True
            )
            response.code = code
        register_response(dataclasses.asdict(response))
        return SuccessfulDeclareResponse(
            code=response.code or "?",
            class_hash=response.class_hash,
            transaction_hash=response.transaction_hash,
        )

    async def _create_declare_tx_v1(
        self,
        compiled_contract,
        account_client: AccountClient,
        max_fee: Optional[int],
        auto_estimate_fee: bool,
    ) -> Declare:
        declare_tx = Declare(
            contract_class=compiled_contract,  # type: ignore
            sender_address=account_client.address,  # type: ignore
            max_fee=0,
            signature=[],
            nonce=await account_client.get_contract_nonce(account_client.address),
            version=1,
        )
        # pylint: disable=protected-access
        max_fee = await account_client._get_max_fee(
            transaction=declare_tx, max_fee=max_fee, auto_estimate=auto_estimate_fee
        )
        declare_tx = dataclasses.replace(declare_tx, max_fee=max_fee)
        signature = account_client.signer.sign_transaction(declare_tx)
        return dataclasses.replace(declare_tx, signature=signature, max_fee=max_fee)

    async def declare_v0(
        self,
        compiled_contract_path: Path,
        token: Optional[str] = None,
        wait_for_acceptance: bool = False,
    ) -> SuccessfulDeclareResponse:
        logger = getLogger()
        logger.warning(
            "Unsigned declare transactions are depreciated and will be removed in future versions."
        )
        compiled_contract = self._load_compiled_contract(
            self._project_root_path / compiled_contract_path
        )
        tx = self._create_declare_tx_v0(contract_class=compiled_contract, nonce=None)
        register_response = self._register_request(
            action="DECLARE",
            payload={
                "contract": str(self._project_root_path / compiled_contract_path),
                "sender_address": tx.sender_address,
                "max_fee": tx.max_fee,
                "version": tx.version,
                "nonce": tx.nonce,
            },
        )
        try:
            result = await self._gateway_client.declare(tx, token)
            register_response(dataclasses.asdict(result))
            if wait_for_acceptance:
                if self._logger:
                    self._logger.info("Waiting for acceptance...")
                _, status = await self._gateway_client.wait_for_tx(
                    result.transaction_hash, wait_for_accept=wait_for_acceptance
                )
                result.code = status
        except TransactionFailedError as ex:
            raise TransactionException(str(ex)) from ex
        return SuccessfulDeclareResponse(
            code=result.code or "",
            class_hash=result.class_hash,
            transaction_hash=result.transaction_hash,
        )

    def _create_declare_tx_v0(
        self,
        contract_class: ContractClass,
        nonce: Optional[int],
    ):
        return Declare(
            contract_class=contract_class,  # type: ignore
            sender_address=DEFAULT_DECLARE_SENDER_ADDRESS,  # type: ignore
            max_fee=0,
            nonce=nonce or 0,
            version=0,
            signature=[],
        )

    async def call(
        self,
        address: AddressRepresentation,
        function_name: str,
        inputs: Optional[ContractFunctionInputType] = None,
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

        try:
            result = await self._call_function(contract_function, inputs)
        except TransactionFailedError as ex:
            raise TransactionException(str(ex)) from ex

        register_response({"result": str(result._asdict())})
        return result

    async def invoke(
        self,
        contract_address: int,
        function_name: str,
        account_address: str,
        signer: BaseSigner,
        inputs: Optional[CairoOrPythonData] = None,
        max_fee: Optional[int] = None,
        auto_estimate_fee: bool = False,
        wait_for_acceptance: bool = False,
    ):
        register_response = self._register_request(
            action="INVOKE",
            payload={
                "contract_address": contract_address,
                "function_name": function_name,
                "max_fee": max_fee,
                "auto_estimate_fee": auto_estimate_fee,
                "inputs": str(inputs),
                "signer": str(signer),
            },
        )
        account_client = await self._create_account_client(
            account_address=account_address, signer=signer
        )
        contract_function = await self._create_contract_function(
            contract_address,
            function_name,
            client=account_client,
        )
        try:
            result = await self._invoke_function(
                contract_function,
                inputs,
                max_fee=max_fee,
                auto_estimate=auto_estimate_fee,
            )

        except TransactionFailedError as ex:
            raise TransactionException(str(ex)) from ex

        result = await result.wait_for_acceptance(wait_for_accept=wait_for_acceptance)

        response_dict: StarknetRequest.Payload = {
            "hash": result.hash,
            "contract_address": result.contract.address,
        }
        if result.block_number:
            response_dict["block_number"] = result.block_number
        if result.status:
            response_dict["status"] = result.status.value  # type: ignore

        register_response(response_dict)

    async def _create_account_client(
        self,
        account_address: str,
        signer: BaseSigner,
    ) -> AccountClient:
        supported_by_account_tx_version = (
            await self._account_tx_version_detector.detect(account_address)
        )
        if supported_by_account_tx_version == 0:
            logger = getLogger()
            logger.warning(
                "Provided account doesn't support v1 transactions. "
                "Transaction version 0 is deprecated and will be removed in a future release of StarkNet. "
                "Please update your account."
            )

        return AccountClient(
            address=account_address,
            client=self._gateway_client,
            signer=signer,
            supported_tx_version=supported_by_account_tx_version,
        )

    async def _create_contract_function(
        self,
        contract_address: AddressRepresentation,
        function_name: str,
        client: Optional[Client] = None,
    ):
        try:
            contract = await Contract.from_address(
                address=contract_address, client=client or self._gateway_client
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
        inputs: Optional[ContractFunctionInputType] = None,
    ):
        if inputs is None:
            inputs = {}

        try:
            if isinstance(inputs, List):
                return await contract_function.call(*inputs)
            return await contract_function.call(**inputs)
        except (TypeError, ValueError) as ex:
            raise InputValidationException(str(ex)) from ex

    @staticmethod
    async def _invoke_function(
        contract_function: ContractFunction,
        inputs: Optional[ContractFunctionInputType] = None,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> InvokeResult:
        if inputs is None:
            inputs = {}
        try:
            if isinstance(inputs, List):
                return await contract_function.invoke(
                    *inputs,
                    max_fee=max_fee,
                    auto_estimate=auto_estimate,
                )
            return await contract_function.invoke(
                **inputs,
                max_fee=max_fee,
                auto_estimate=auto_estimate,
            )
        except (TypeError, ValueError) as ex:
            raise InputValidationException(str(ex)) from ex

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


class UnknownFunctionException(ProtostarException):
    def __init__(self, function_name: str):
        super().__init__(f"Tried to call unknown function: '{function_name}'")


class ContractNotFoundException(ProtostarException):
    def __init__(self, contract_address: AddressRepresentation):
        super().__init__(f"Tried to call unknown contract:\n{contract_address}")


class InputValidationException(ProtostarException):
    def __init__(self, message: str):
        super().__init__(
            "Input validation failed with the following error:\n" + message
        )


class TransactionException(ProtostarException):
    pass


class CompilationOutputNotFoundException(ProtostarException):
    def __init__(self, compilation_output_filepath: Path):
        super().__init__(
            f"Couldn't find `{str(compilation_output_filepath.resolve())}`\n"
            "Did you run `protostar build`?"
        )
        self._compilation_output_filepath = compilation_output_filepath


def transform_constructor_inputs_from_python(
    abi: AbiType, inputs: Optional[CairoOrPythonData]
) -> List[int]:
    if not inputs:
        return []
    if isinstance(inputs, List):
        return inputs

    try:
        return from_python_transformer(abi, fn_name="constructor", mode="inputs")(
            inputs
        )
    except DataTransformerException as ex:
        raise InputValidationException(str(ex)) from ex


def validate_cairo_inputs(abi: AbiType, inputs: List[int]):
    try:
        to_python_transformer(abi, "constructor", "inputs")(inputs)
    except DataTransformerException as ex:
        raise InputValidationException(str(ex)) from ex
