import dataclasses
from pathlib import Path
from typing import Optional, TypeVar, Union

from starknet_py.net.account.account import Account
from starknet_py.net.client_errors import ClientError
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import Transaction, Invoke
from starknet_py.net.signer import BaseSigner
from starknet_py.net.udc_deployer.deployer import Deployer, ContractDeployment
from starknet_py.net.client_models import Call
from starknet_py.transaction_exceptions import (
    TransactionFailedError,
    TransactionRejectedError,
)
from starknet_py.utils.data_transformer.errors import CairoSerializerException
from typing_extensions import Self, TypeGuard

from protostar.protostar_exception import ProtostarException
from protostar.starknet import (
    ContractAbi,
    Address,
    CairoData,
    TransactionHash,
    Selector,
)
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.starknet_gateway.account_tx_version_detector import (
    AccountTxVersionDetector,
)
from protostar.starknet_gateway.gateway_response import (
    SuccessfulDeclareResponse,
    SuccessfulDeployAccountResponse,
    SuccessfulDeployResponse,
)
from protostar.starknet_gateway.multicall import MulticallClientResponse
from protostar.starknet_gateway.multicall.multicall_protocols import (
    SignedMulticallTransaction,
    MulticallClientProtocol,
)
from protostar.starknet_gateway.core import PreparedInvokeTransaction

from .type import ClassHash, Fee


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
    ):
        self._project_root_path = project_root_path
        self._gateway_client = gateway_client
        self._account_tx_version_detector = AccountTxVersionDetector(
            self._gateway_client
        )

    async def _create_udc_deployment(
        self,
        class_hash: int,
        account_address: Address,
        inputs: Optional[CairoOrPythonData] = None,
        contract_abi: Optional[ContractAbi] = None,
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

        if not contract_abi:
            abi_entries = (await self._gateway_client.get_class_by_hash(class_hash)).abi
            if abi_entries:
                contract_abi = ContractAbi.from_abi_entries(abi_entries)
        if not contract_abi:
            raise ProtostarException(
                "ABI not found neither in arguments nor in API response. \n"
                "Please provide ABI file manually."
            )

        if inputs and not contract_abi.has_constructor():
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
                abi=contract_abi.to_abi_type(),
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
        contract_abi: Optional[ContractAbi] = None,
        salt: Optional[int] = None,
        token: Optional[str] = None,
    ) -> SuccessfulDeployResponse:
        deployment = await self._create_udc_deployment(
            class_hash=class_hash,
            contract_abi=contract_abi,
            account_address=account_address,
            inputs=inputs,
            salt=salt,
        )

        account = await self._get_account(
            account_address=account_address,
            signer=signer,
        )
        try:
            tx = await account.sign_invoke_transaction(
                deployment.call,
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
        except ClientError as ex:
            account_address_hex = hex(int(account_address))
            if (
                ex.code == "500"
                and f"Requested contract address {account_address_hex} is not deployed"
                in ex.message
            ):
                raise TransactionException(
                    f"Account {account_address_hex} is not deployed"
                ) from ex
            raise TransactionException(str(ex)) from ex

    async def deploy_account(
        self, args: DeployAccountArgs
    ) -> SuccessfulDeployAccountResponse:
        account = await self._get_account(
            account_address=args.account_address,
            signer=args.signer,
        )

        tx = await account.sign_deploy_account_transaction(
            class_hash=args.account_class_hash,
            contract_address_salt=args.account_address_salt,
            constructor_calldata=args.account_constructor_input,
            max_fee=args.max_fee if isinstance(args.max_fee, int) else None,
            auto_estimate=args.max_fee == "auto",
        )
        response = await account.client.deploy_account(tx)
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
        account = await self._get_account(
            account_address=account_address, signer=signer
        )
        declare_tx = await account.sign_declare_transaction(
            compiled_contract=compiled_contract,
            max_fee=max_fee if isinstance(max_fee, int) else None,
            auto_estimate=max_fee == "auto",
        )
        try:
            response = await self._gateway_client.declare(declare_tx, token=token)

            if wait_for_acceptance:
                _, code = await account.wait_for_tx(
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

    async def _get_account(
        self,
        account_address: Address,
        signer: BaseSigner,
    ) -> Account:
        return Account(
            address=int(account_address),
            client=self._gateway_client,
            signer=signer,
        )

    async def send_multicall_transaction(
        self, transaction: SignedMulticallTransaction
    ) -> MulticallClientResponse:
        try:
            result = await self._gateway_client.send_transaction(
                transaction=Invoke(
                    version=1,
                    contract_address=int(transaction.contract_address),  # type: ignore
                    calldata=transaction.calldata,  # type: ignore
                    max_fee=transaction.max_fee,
                    nonce=transaction.nonce,
                    signature=transaction.signature,
                )
            )
            return MulticallClientResponse(transaction_hash=result.transaction_hash)
        except ClientError as ex:
            raise TransactionException(message=ex.message) from ex

    async def send_call(
        self,
        address: Address,
        selector: Selector,
        cairo_calldata: Optional[CairoData] = None,
    ) -> CairoData:
        try:
            return await self._gateway_client.call_contract(
                call=Call(
                    to_addr=int(address),
                    selector=int(selector),
                    calldata=cairo_calldata or [],
                )
            )
        except ClientError as ex:
            if "ENTRY_POINT_NOT_FOUND_IN_CONTRACT" in ex.message:
                raise TransactionException(
                    message=f'Entry point "{selector}" not found in the contract with address "{address}"'
                ) from ex
            if "UNINITIALIZED_CONTRACT" in ex.message:
                raise TransactionException(
                    message=f'Contract with address "{address}" not found'
                ) from ex
            raise TransactionException(message=ex.message) from ex

    async def send_prepared_invoke_tx(
        self, prepared_invoke_tx: PreparedInvokeTransaction
    ) -> TransactionHash:
        try:
            contract_address = int(prepared_invoke_tx.account_address)
            calldata = prepared_invoke_tx.account_execute_calldata
            result = await self._gateway_client.send_transaction(
                transaction=Invoke(
                    version=1,
                    contract_address=contract_address,  # type: ignore
                    calldata=calldata,  # type: ignore
                    max_fee=prepared_invoke_tx.max_fee,
                    nonce=prepared_invoke_tx.nonce,
                    signature=prepared_invoke_tx.signature,
                )
            )
            return result.transaction_hash
        except ClientError as ex:
            raise TransactionException(message=ex.message) from ex

    async def wait_for_acceptance(self, tx_hash: int):
        await self._gateway_client.wait_for_tx(tx_hash=tx_hash, wait_for_accept=True)


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
