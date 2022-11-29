import dataclasses
from pathlib import Path
from typing import Any, Dict, List, Literal, NamedTuple, Optional, TypeVar, Union

from starknet_py.contract import ContractFunction, InvokeResult
from starknet_py.net import AccountClient
from starknet_py.net.client_errors import ClientError
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import Transaction
from starknet_py.net.signer import BaseSigner
from starknet_py.net.udc_deployer.deployer import Deployer, ContractDeployment
from starknet_py.net.client_models import InvokeFunction
from starknet_py.transaction_exceptions import (
    TransactionFailedError,
    TransactionRejectedError,
)
from starknet_py.utils.data_transformer.data_transformer import CairoData
from starknet_py.utils.data_transformer.errors import CairoSerializerException
from starkware.starknet.public.abi import AbiType
from typing_extensions import Self, TypeGuard

from protostar.compiler import CompiledContractReader
from protostar.protostar_exception import ProtostarException
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.starknet_gateway.account_tx_version_detector import (
    AccountTxVersionDetector,
)
from protostar.starknet_gateway.gateway_response import (
    SuccessfulDeclareResponse,
    SuccessfulDeployAccountResponse,
    SuccessfulDeployResponse,
    SuccessfulInvokeResponse,
)
from protostar.starknet import Address
from protostar.starknet_gateway.multicall.multicall_output import MulticallOutput
from protostar.starknet_gateway.multicall.multicall_protocols import (
    InvokeSignedTransaction,
    MulticallClientProtocol,
)

from .contract_function_factory import ContractFunctionFactory
from ..starknet.abi import has_abi_item

ContractFunctionInputType = Union[List[int], Dict[str, Any]]


Wei = int
Fee = Union[Wei, Literal["auto"]]
ClassHash = int


@dataclasses.dataclass
class DeployAccountArgs:
    account_address: Address
    account_address_salt: int
    account_constructor_input: Optional[list[int]]
    account_class_hash: ClassHash
    max_fee: Fee
    signer: BaseSigner
    nonce: int


TransactionT = TypeVar("TransactionT", bound=Transaction)


def is_cairo_data(inputs: Optional[CairoOrPythonData]) -> TypeGuard[CairoData]:
    return isinstance(inputs, list)


# pylint: disable=too-many-instance-attributes
class GatewayFacade(MulticallClientProtocol):
    def __init__(
        self,
        project_root_path: Path,
        gateway_client: GatewayClient,
        compiled_contract_reader: CompiledContractReader,
    ):
        self._project_root_path = project_root_path
        self._gateway_client = gateway_client
        self._compiled_contract_reader = compiled_contract_reader
        self._account_tx_version_detector = AccountTxVersionDetector(
            self._gateway_client
        )

    async def _create_udc_deployment(
        self,
        class_hash: int,
        account_address: Address,
        inputs: Optional[CairoOrPythonData] = None,
        abi: Optional[AbiType] = None,
        salt: Optional[int] = None,
    ) -> ContractDeployment:
        if isinstance(inputs, list):
            return Deployer(
                account_address=int(account_address)
            ).create_deployment_call_raw(
                class_hash=class_hash,
                raw_calldata=inputs,
                salt=salt,
            )

        if not abi:
            abi = (await self._gateway_client.get_class_by_hash(class_hash)).abi
        if not abi:
            raise ProtostarException(
                "ABI not found neither in arguments nor in API response. \n"
                "Please provide ABI file manually."
            )

        if not has_abi_item(abi, "constructor") and inputs:
            raise InputValidationException(
                "Inputs provided to a contract with no constructor."
            )

        try:
            return Deployer(
                account_address=int(account_address)
            ).create_deployment_call(
                class_hash=class_hash,
                calldata=inputs,
                salt=salt,
                abi=abi,
            )
        except (ValueError, TypeError, CairoSerializerException) as v_err:
            raise InputValidationException(str(v_err)) from v_err

    async def deploy_via_udc(
        self,
        class_hash: int,
        account_address: Address,
        max_fee: Fee,
        signer: BaseSigner,
        inputs: Optional[CairoOrPythonData] = None,
        wait_for_acceptance: bool = False,
        abi: Optional[AbiType] = None,
        salt: Optional[int] = None,
        token: Optional[str] = None,
    ) -> SuccessfulDeployResponse:
        deployment = await self._create_udc_deployment(
            class_hash=class_hash,
            abi=abi,
            account_address=account_address,
            inputs=inputs,
            salt=salt,
        )

        account_client = await self._create_account_client(
            account_address=account_address,
            signer=signer,
        )
        try:
            tx = await account_client.sign_invoke_transaction(
                deployment.udc,
                max_fee=max_fee if isinstance(max_fee, int) else None,
                auto_estimate=max_fee == "auto",
            )
            result = await self._gateway_client.send_transaction(tx, token)

            if wait_for_acceptance:
                _, status = await self._gateway_client.wait_for_tx(
                    result.transaction_hash, wait_for_accept=wait_for_acceptance
                )
                result.code = status.value

            return SuccessfulDeployResponse(
                code=result.code or "",
                address=Address(deployment.address),
                transaction_hash=result.transaction_hash,
            )
        except TransactionFailedError as ex:
            raise TransactionException(str(ex)) from ex

    async def deploy_account(
        self, args: DeployAccountArgs
    ) -> SuccessfulDeployAccountResponse:
        account_client = await self._create_account_client(
            account_address=args.account_address,
            signer=args.signer,
        )

        tx = await account_client.sign_deploy_account_transaction(
            class_hash=args.account_class_hash,
            contract_address_salt=args.account_address_salt,
            constructor_calldata=args.account_constructor_input,
            max_fee=args.max_fee if isinstance(args.max_fee, int) else None,
            auto_estimate=args.max_fee == "auto",
        )
        response = await account_client.deploy_account(tx)
        return SuccessfulDeployAccountResponse(
            code=response.code or "",
            address=Address(response.address),
            transaction_hash=response.transaction_hash,
        )

    def _load_compiled_contract(self, compiled_contract_path: Path) -> str:
        try:
            return compiled_contract_path.read_text("utf-8")
        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(compiled_contract_path) from err

    async def declare(
        self,
        compiled_contract_path: Path,
        account_address: Address,
        signer: BaseSigner,
        max_fee: Fee,
        wait_for_acceptance: bool = False,
        token: Optional[str] = None,
    ):
        compiled_contract = self._load_compiled_contract(
            self._project_root_path / compiled_contract_path
        )
        account_client = await self._create_account_client(
            account_address=account_address, signer=signer
        )
        declare_tx = await account_client.sign_declare_transaction(
            compiled_contract=compiled_contract,
            max_fee=max_fee if isinstance(max_fee, int) else None,
            auto_estimate=max_fee == "auto",
        )
        try:
            response = await self._gateway_client.declare(declare_tx, token=token)

            if wait_for_acceptance:
                _, code = await account_client.wait_for_tx(
                    response.transaction_hash, wait_for_accept=True
                )
                response.code = code.value
        except (ClientError, TransactionRejectedError) as ex:
            fee_ex = FeeExceededMaxFeeException.from_gateway_error(ex)
            if fee_ex is not None:
                raise fee_ex from ex
            raise ex

        return SuccessfulDeclareResponse(
            code=response.code or "?",
            class_hash=response.class_hash,
            transaction_hash=response.transaction_hash,
        )

    async def call(
        self,
        address: Address,
        function_name: str,
        inputs: Optional[ContractFunctionInputType] = None,
    ) -> NamedTuple:
        contract_function = await self._get_contract_function(
            function_name=function_name,
            address=address,
        )

        try:
            result = await self._call_function(contract_function, inputs)
        except TransactionFailedError as ex:
            raise TransactionException(str(ex)) from ex
        except ClientError as ex:
            raise TransactionException(message=ex.message) from ex

        return result

    async def invoke(
        self,
        contract_address: Address,
        function_name: str,
        account_address: Address,
        signer: BaseSigner,
        max_fee: Fee,
        inputs: Optional[CairoOrPythonData] = None,
        wait_for_acceptance: bool = False,
    ) -> SuccessfulInvokeResponse:
        account_client = await self._create_account_client(
            account_address=account_address, signer=signer
        )
        try:
            contract_function = await self._get_contract_function(
                function_name=function_name,
                address=contract_address,
                client=account_client,
            )
            result = await self._invoke_function(
                contract_function=contract_function,
                inputs=inputs,
                max_fee=max_fee,
            )

        except TransactionFailedError as ex:
            raise TransactionException(str(ex)) from ex
        except ClientError as ex:
            raise TransactionException(message=ex.message) from ex

        result = await result.wait_for_acceptance(wait_for_accept=wait_for_acceptance)

        return SuccessfulInvokeResponse(
            transaction_hash=result.hash
            if isinstance(result.hash, int)
            else int(result.hash),
        )

    async def _invoke_function(
        self,
        contract_function: ContractFunction,
        max_fee: Fee,
        inputs: Optional[CairoOrPythonData] = None,
    ) -> InvokeResult:
        fee_params = {
            "max_fee": max_fee if isinstance(max_fee, int) else None,
            "auto_estimate": max_fee == "auto",
        }

        if inputs is None:
            inputs = {}

        try:
            if isinstance(inputs, list):  # List of felts, raw input
                return await contract_function.invoke(*inputs, **fee_params)
            return await contract_function.invoke(**inputs, **fee_params)
        except (TypeError, ValueError) as ex:
            raise InputValidationException(str(ex)) from ex

    async def _create_account_client(
        self,
        account_address: Address,
        signer: BaseSigner,
    ) -> AccountClient:
        supported_by_account_tx_version = (
            await self._account_tx_version_detector.detect(account_address)
        )
        if supported_by_account_tx_version == 0:
            raise ProtostarException(
                "Provided account doesn't support v1 transactions.\n"
                "Please update your account."
            )

        return AccountClient(
            address=int(account_address),
            client=self._gateway_client,
            signer=signer,
            supported_tx_version=supported_by_account_tx_version,
        )

    @staticmethod
    async def _call_function(
        contract_function: ContractFunction,
        inputs: Optional[ContractFunctionInputType] = None,
    ):
        if inputs is None:
            inputs = {}

        try:
            if isinstance(inputs, list):
                return await contract_function.call(*inputs)
            return await contract_function.call(**inputs)
        except (TypeError, ValueError) as ex:
            raise InputValidationException(str(ex)) from ex

    async def _get_contract_function(
        self,
        address: Address,
        function_name: str,
        client: Optional[Union[GatewayClient, AccountClient]] = None,
    ) -> ContractFunction:
        if not client:
            client = self._gateway_client

        return await ContractFunctionFactory(client).create(address, function_name)

    async def send_multicall_transaction(
        self, transaction: InvokeSignedTransaction
    ) -> MulticallOutput:
        result = await self._gateway_client.send_transaction(
            transaction=InvokeFunction(
                version=1,
                contract_address=int(transaction.contract_address),  # type: ignore
                calldata=transaction.calldata,  # type: ignore
                max_fee=transaction.max_fee,
                nonce=transaction.nonce,
                signature=transaction.signature,
            )
        )
        return MulticallOutput(transaction_hash=result.transaction_hash)


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


class FeeExceededMaxFeeException(ProtostarException):
    @classmethod
    def from_gateway_error(
        cls, client_error: Union[ClientError, TransactionRejectedError]
    ) -> Optional[Self]:
        if "Actual fee exceeded max fee" in client_error.message:
            return cls(client_error.message)
        return None
